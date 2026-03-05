#Coding:utf-8
from pathlib import Path
import json, copy, time, traceback, string, threading, sys
from datetime import datetime, timedelta, timezone
from psycopg2 import sql

# ==========================
# TABLE SIMPLE
# ==========================
def create_table_simple(self, conn, base_table):
	if base_table in self.created_tables:
		return
	cur = conn.cursor()
	index_name = f'idx_{base_table}_updated_at'
	cur.execute(
		sql.SQL("""
			CREATE TABLE IF NOT EXISTS {} (
				id BIGSERIAL PRIMARY KEY,
				data JSONB NOT NULL,
				created_at TIMESTAMP NOT NULL DEFAULT NOW(),
				updated_at TIMESTAMP NOT NULL DEFAULT NOW()
			)
		""").format(sql.Identifier(base_table))
	)
	cur.execute(
		sql.SQL("""
			CREATE INDEX IF NOT EXISTS {index_name}
			ON {table} (updated_at)
		""").format(
				index_name = sql.Identifier(index_name),
				table = sql.Identifier(base_table),
			)
	)
	self.created_tables.add(base_table)
	conn.commit()
	cur.close()

# ==========================
# GET DATA SIMPLE
# ==========================
def get_data_simple(self, base_table, record_id: int = None):
	"""
	Récupère les données d'une table simple.
	Si record_id est fourni, renvoie uniquement cette ligne.
	Sinon, renvoie toutes les lignes.
	"""
	conn = self.get_conn()
	try:
		self.create_table_simple(conn, base_table)
		cur = conn.cursor()

		if record_id:
			query = """
				SELECT id, data, created_at, updated_at
				FROM {table}
				WHERE id = %s
			"""
			cur.execute(sql.SQL(query).format(table=sql.Identifier(base_table)), (record_id,))
		else:
			query = """
				SELECT id, data, created_at, updated_at
				FROM {table}
				ORDER BY id ASC
			"""
			cur.execute(sql.SQL(query).format(table=sql.Identifier(base_table)))

		rows = cur.fetchall()
		result = {}
		for rid, data, created_at, updated_at in rows:
			data_copy = copy.deepcopy(data)
			# Ajout des dates dans le data pour filtrage facile côté client
			data_copy['created_at'] = created_at.astimezone(timezone.utc).isoformat()
			data_copy['updated_at'] = updated_at.astimezone(timezone.utc).isoformat()
			where = self.get_my_where(base_table)
			th_rid = self.set_ident_of(where,rid)
			data_copy["N°"] = th_rid
			data_copy['id'] = rid
			result[th_rid] = data_copy

		if record_id:
			result = result.get(record_id)

		cur.close()
		return self.success_response(result, base_table, "get")

	except Exception as e:
		print(traceback.format_exc())
		conn.rollback()
		return self.failed_response(str(e), base_table, "get")
	finally:
		self.put_conn(conn)

# ==========================
# SAVE DATA SIMPLE
# ==========================
def save_data_simple(self, base_table, data):
	conn = self.get_conn()
	record_id = data.get("id")

	try:
		with conn:
			with conn.cursor() as cur:
				self.create_table_simple(conn, base_table)
				json_data = json.dumps(data)

				if record_id:
					cur.execute(
						sql.SQL("""
							INSERT INTO {} (id, data, updated_at)
							VALUES (%s, %s, NOW())
							ON CONFLICT (id)
							DO UPDATE SET 
								data = EXCLUDED.data,
								updated_at = NOW()
							RETURNING id
						""").format(sql.Identifier(base_table)),
						(record_id,json_data)
					)
				else:
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
		data['N°'] = record_id
		return self.success_response(data, base_table, "save")
	except Exception as e:
		return self.failed_response(str(e), base_table, "save")
	finally:
		self.put_conn(conn)

# ==========================
# DELETE DATA SIMPLE
# ==========================
def delete_data_simple(self, base_table, record_id: int = None):
	"""
	Supprime les données d'une table simple.
	Si record_id est fourni → suppression ciblée
	Sinon → supprime toutes les lignes
	"""
	conn = self.get_conn()
	try:
		with conn:
			with conn.cursor() as cur:
				self.create_table_simple(conn, base_table)

				if record_id:
					query = sql.SQL("DELETE FROM {} WHERE id = %s").format(sql.Identifier(base_table))
					cur.execute(query, (record_id,))
				else:
					# Supprime tout
					query = sql.SQL("DELETE FROM {}").format(sql.Identifier(base_table))
					cur.execute(query)

		return self.success_response({"deleted_id": record_id}, base_table, "delete")

	except Exception as e:
		conn.rollback()
		return self.failed_response(str(e), base_table, "delete")
	finally:
		self.put_conn(conn)
