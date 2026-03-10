# Coding:utf-8

from Base.serveur.main import *
import traceback
import sys
from lib.serveur.DAV_BASE.MyData import date_obj
# =========================
# DATABASE (Railway)
# =========================

#DATABASE_URL = "postgresql://postgres:davtechbenin@localhost:8432/postgres"
DATABASE_URL = "postgresql://postgres:OjAXnBDSJNNzqnrCMgJbLvmQHFkhUwac@caboose.proxy.rlwy.net:23351/railway"

# =========================
# UTILS
# =========================
def normalize_table_name(base_name: str, table: str) -> str:
	base = re.sub(r"[^a-zA-Z0-9_]", "_", base_name.strip())
	table = re.sub(r"[^a-zA-Z0-9_]", "_", table.strip())
	return f"{base}__{table}"

# =========================
# CONNECTION MANAGER
# =========================
class ConnectionManager:
	def __init__(self):
		# WebSocket

		self.th_base_hand = data_main(self)
		#self.th_base_hand.delete_all_from_DB()
		#sys.exit()

		self.active_connections: dict[int, WebSocket] = {}
		self.subscriptions: dict[str, set[int]] = {}
		self.lock = asyncio.Lock()
		self.data_lock = asyncio.Lock()
		self.table_locks = dict()

		self.Data_Table = dict()

		# Thread executor
		self.executor = concurrent.futures.ThreadPoolExecutor(
			max_workers=os.cpu_count() or 4
		)

		# PostgreSQL pool
		self.pool = SimpleConnectionPool(
			minconn=1,
			maxconn=5,
			dsn=DATABASE_URL,
			sslmode="require"
		)
		self.created_tables = set()

		# Local folders
		self.info_dir = os.path.join(Path.home(), ".ProGest")
		os.makedirs(self.info_dir, exist_ok=True)

	# =========================
	# PostgreSQL helpers
	# =========================
	def get_conn(self):
		return self.pool.getconn()

	def put_conn(self, conn):
		self.pool.putconn(conn)

	def close_all(self):
		self.pool.closeall()

# =========================
# WebSocket lifecycle
# =========================
	async def connect(self, websocket: WebSocket):
		await websocket.accept()
		async with self.lock:
			self.active_connections[id(websocket)] = websocket

	async def disconnect(self, websocket: WebSocket):
		async with self.lock:
			ws_id = id(websocket)
			self.active_connections.pop(ws_id, None)
			for key in list(self.subscriptions.keys()):
				self.subscriptions[key].discard(ws_id)
				if not self.subscriptions[key]:
					self.subscriptions.pop(key)

	# =========================
	# Subscriptions
	# =========================
	async def subscribe(self, websocket: WebSocket, base_name: str):
		async with self.lock:
			self.subscriptions.setdefault(base_name, set()).add(id(websocket))

	async def unsubscribe(self, websocket: WebSocket, base_name: str):
		async with self.lock:
			ws_id = id(websocket)
			if base_name in self.subscriptions:
				self.subscriptions[base_name].discard(ws_id)
				if not self.subscriptions[base_name]:
					self.subscriptions.pop(base_name)

# =========================
# Dispatcher
# =========================
	async def handle_message(self, websocket: WebSocket, raw_message: str):
		try:
			msg = json.loads(raw_message)
		except json.JSONDecodeError:
			return await self._send_error(websocket, None, "Invalid JSON")
		#print(msg)
		#print("------------------------")
		action = msg.get("action")
		base_name = msg.get("base_name")
		request_id = msg.get("request_id")
		data = msg.get("data")
		t = time.time()

		if action == "subscribe":
			#self.th_base_hand.drop_all_tab_of(base_name)
			await self.subscribe(websocket, base_name)
			return await self._send_ok(websocket, request_id, action)

		if action == "unsubscribe":
			await self.unsubscribe(websocket, base_name)
			return await self._send_ok(websocket, request_id, action)

		else:
			await self.th_base_hand.manage_msg(msg)
		
		#return await self._send_error(websocket, request_id, "Unknown action")

	# =========================
	# Broadcast
	# =========================
	async def broadcast_table_update(self, base_name, payload: dict):
		async with self.lock:
			receivers = [
				self.active_connections[i]
				for i in self.subscriptions.get(base_name, set())
				if i in self.active_connections
			]
		await asyncio.gather(*(self._safe_send(ws, payload) for ws in receivers))

	async def _safe_send(self, websocket: WebSocket, payload: dict):
		try:
			await websocket.send_text(json.dumps(payload))
		except Exception:
			await self.disconnect(websocket)

	async def _send_ok(self, ws, request_id, action,result = {}):
		if not result:
			result = dict()
		dic = {
			"request_id": request_id,
			"status": "ok",
			"action": action,
			"date":self.get_today(),
			"heure":self.get_hour(),
			'result':result,
		}
		await self._safe_send(ws, dic)

	async def _send_error(self, ws, request_id, action, data = {},error_format = None):
		await self._safe_send(ws, {
			"request_id": request_id,
			"status": "error",
			"action": action,
			"result":data,
			"error_format":error_format
		})

# Gestion des dates
	def get_today(self):
		return self.normalize_date(date_obj().date__)

	def get_hour(self):
		return date_obj().hour

	def get_now(self):
		return f"{self.get_today()} .{self.get_hour()}"

	def normalize_date(self,date):
		date = date.replace("/","-")
		d,m,y = date.split('-')
		if len(y)==2:
			y = '20'+y
		elif len(y)==3:
			y = "2"+y
		elif len(y)==1:
			y = "202"+y
		if len(d)==1:
			d = '0'+d
		if len(m)==1:
			m = "0"+m
		text = f"{d}-{m}-{y}"
		return text


