from pathlib import Path
import json, copy, time, traceback, string, threading, sys
from datetime import datetime, timedelta, timezone
from psycopg2 import sql

# ==========================
# GET DATA PARTITIONNEE
# ==========================
def partition_get_data(self, base_table, date: datetime = None, record_id: int = None):
	"""
	Récupère les données d'une table partitionnée.
	Filtrage possible par date (UTC) et/ou id.
	"""
	conn = self.get_conn()
	try:
		self.partition_create_table(conn, base_table)
		cur = conn.cursor()

		conditions = []
		params = []

		if date:
			# On prend les partitions correspondant à la date
			start_date = datetime(date.year, date.month, date.day, tzinfo=timezone.utc)
			end_date = start_date + timedelta(days=1)
			conditions.append("updated_at >= %s AND updated_at < %s")
			params.extend([start_date, end_date])

		if record_id:
			conditions.append("id = %s")
			params.append(record_id)

		where_clause = ""
		if conditions:
			where_clause = "WHERE " + " AND ".join(conditions)

		query = f"""
			SELECT id, data, created_at, updated_at
			FROM {base_table}
			{where_clause}
			ORDER BY updated_at ASC, id ASC
		"""

		cur.execute(query, params)
		rows = cur.fetchall()

		result = {}
		for rid, data, created_at, updated_at in rows:
			data_copy = copy.deepcopy(data)
			data_copy['created_at'] = created_at.astimezone(timezone.utc).isoformat()
			data_copy['updated_at'] = updated_at.astimezone(timezone.utc).isoformat()
			where = self.get_my_where(base_table)
			data_copy['id'] = rid
			data_copy['N°'] = self.set_ident_of(where,rid)
			result[rid] = data_copy

		cur.close()
		return result

	except Exception as e:
		print(traceback.format_exc())
		conn.rollback()
		return {}
	finally:
		self.put_conn(conn)

# ==========================
# TABLE PARTITIONNEE
# ==========================
def partition_create_table(self, conn, base_table):
	today = datetime.utcnow().date()
	tomorrow = today + timedelta(days=1)
	partition_name = f"{base_table}_{today.strftime('%Y_%m_%d')}"

	cur = conn.cursor()
	# 1️⃣ Crée la table parent si nécessaire
	if base_table not in self.created_tables:
		cur.execute(
			sql.SQL("""
				CREATE TABLE IF NOT EXISTS {table} (
					id BIGSERIAL NOT NULL,
					data JSONB NOT NULL,
					updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
					PRIMARY KEY (id, updated_at)
				) PARTITION BY RANGE (updated_at)
			""").format(table=sql.Identifier(base_table))
		)
		cur.execute(
			sql.SQL("""
				CREATE INDEX IF NOT EXISTS idx_{0}_updated_at
				ON {0} (updated_at)
			""").format(sql.Identifier(base_table))
		)
		self.created_tables.add(base_table)

	# 2️⃣ Crée la partition du jour si nécessaire
	if partition_name not in self.created_tables:
		cur.execute(
			sql.SQL("""
				CREATE TABLE IF NOT EXISTS {partition}
				PARTITION OF {parent}
				FOR VALUES FROM (%s) TO (%s)
			""").format(
				partition=sql.Identifier(partition_name),
				parent=sql.Identifier(base_table),
			),
			(today, tomorrow)
		)
		self.created_tables.add(partition_name)

	conn.commit()
	cur.close()

# ==========================
# SAVE DATA PARTITIONNEE (INSERT ONLY)
# ==========================
def save_data_partition(self, base_table, data):
	conn = self.get_conn()
	try:
		with conn:
			with conn.cursor() as cur:
				self.partition_create_table(conn, base_table)
				json_data = json.dumps(data)

				# INSERT ONLY → pas de update pour partition
				cur.execute(
					sql.SQL("""
						INSERT INTO {} (data, updated_at)
						VALUES (%s, NOW())
						RETURNING id
					""").format(sql.Identifier(base_table)),
					(json_data,)
				)
				record_id = cur.fetchone()[0]

		data["id"] = record_id
		return self.success_response(data, base_table, "save")
	except Exception as e:
		conn.rollback()
		return self.failed_response(str(e), base_table, "save")
	finally:
		self.put_conn(conn)


# ==========================
# DELETE DATA PARTITIONNEE
# ==========================
def delete_data_partition(self, base_table, date: datetime = None, record_id: int = None):
    """
    Supprime les données d'une table partitionnée.
    Filtrage possible par date (UTC) et/ou id.
    """
    conn = self.get_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                self.partition_create_table(conn, base_table)

                conditions = []
                params = []

                if date:
                    start_date = datetime(date.year, date.month, date.day, tzinfo=timezone.utc)
                    end_date = start_date + timedelta(days=1)
                    conditions.append("updated_at >= %s AND updated_at < %s")
                    params.extend([start_date, end_date])

                if record_id:
                    conditions.append("id = %s")
                    params.append(record_id)

                if conditions:
                    where_clause = "WHERE " + " AND ".join(conditions)
                else:
                    # Pas de filtre → supprimer tout
                    where_clause = ""

                query = f"DELETE FROM {base_table} {where_clause}"
                cur.execute(query, params)

        return self.success_response(
            {"id": record_id, "deleted_date": date.isoformat() if date else None},
            base_table, "delete"
        )

    except Exception as e:
        conn.rollback()
        return self.failed_response(str(e), base_table, "delete")
    finally:
        self.put_conn(conn)

