#Coding:utf-8
"""
	Gestion de la base Local sqlite
"""
from pathlib import Path
import json, copy, time, traceback, string, threading, sys, asyncio
from datetime import datetime, timedelta, timezone
from psycopg2 import sql

def normalize_table_name(base_name: str) -> str:
	base = re.sub(r"[^a-zA-Z0-9_]", "_", base_name.strip())
	return base

class local:
	from .table_partitionner import (partition_get_data,
		partition_create_table,save_data_partition,
		delete_data_partition)

	from .table_simple import (create_table_simple,
		get_data_simple,save_data_simple,
		delete_data_simple)

	def __init__(self):
		self.general_fic = "general"
		self.user_fic = "users"
		self.menu_fic = "menus"
		self.categorie_fic = 'categories'
		self.commande_fic = 'commandes'
		self.livraison_fic = 'livraisons'
		self.article_fic = "articles"
		self.commission_fic = "commissions"
		self.recette_fic = "recettes"
		self.finance_fic = 'finances'
		self.depense_fic = 'depenses'

		self.statique_ident = 1

		self.where_fonc_hand = {
			self.user_fic : self.user_message_handler,
			self.menu_fic : self.menu_message_handler,
			self.categorie_fic : self.categorie_message_handler,
			self.commande_fic : self.commande_message_handler,
			self.livraison_fic : self.livraison_message_handler,
			self.article_fic : self.article_message_handler,
			self.commission_fic: self.commission_message_handler

		}

		self.partion_table = [
			self.livraison_fic,
			self.commande_fic
		]

	def delete_all_from_DB(self):
		conn = self.get_conn()
		try:
			cur = conn.cursor()
			cur.execute("DROP SCHEMA public CASCADE;")
			cur.execute("CREATE SCHEMA public;")
			conn.commit()
			cur.close()
		finally:
			self.put_conn(conn)

	def success_response(self,data,where,action):
		dic = {
			"status":"ok",
			"data":data,
			"message":f'{action} {where} went successfully',
			"action":action,
			"where":where
		}
		return dic
	
	def failed_response(self,data,where,action,E = None):
		if not E:
			E = traceback.format_exc()
			print(E)
		return {
			"status":"error",
			"data":data,
			"message":f'{action} {where} went wrong. \n this is what goes wrong:\n{E}',
			"action":action,
			"where":where
		}

# Gestion des api d'envoie, de save et de delete
	async def save_data(self, base_table, data):
		main_table = base_table.split('_z_o_e_')[1]
		
		await_dic = await asyncio.to_thread(self.save_data_simple,
			base_table, data)
		dic = await_dic.get('data')
		return await self.verif_info(dic,base_table,"save")

	async def get_data(self, base_table, date = None, record_id = None):
		all_dic = dict()
		try:
			if isinstance(base_table, (list,tuple)):
				for tab in base_table:
					dic = await self.__get_data(tab,date,record_id)
					all_dic[tab] = dic
			elif isinstance(base_table, str):
				##print(base_table,record_id)
				all_dic = await self.__get_data(base_table,date,record_id)
			return self.success_response(all_dic,base_table,'get')
		except:
			return self.failed_response(all_dic,base_table,'get')

	async def __get_data(self, base_table, date = None, record_id = None):
		main_table = base_table.split('_z_o_e_')[1]
		record_id = self.get_ident_of(record_id)
		await_dic = await asyncio.to_thread(self.get_data_simple,
			base_table, record_id)
		#print(await_dic)
		dic = await_dic.get('data')
		#print(dic)
		#print('----------------\n')
		return dic

	async def delete_data(self, base_table, date = None, record_id = None):
		main_table = base_table.split('_z_o_e_')[1]
		record_id = self.get_ident_of(record_id)
		if main_table.lower() in self.partion_table:
			await_dic = await asyncio.to_thread(self.delete_data_partition,
				base_table, date, record_id)
			dic = await_dic.get('data')
		else:
			await_dic = await asyncio.to_thread(self.delete_data_simple,
				base_table, record_id)
			dic = await_dic.get('data')
		return await self.verif_info(dic,base_table,"delete")

	async def verif_info(self,data_dic,where,action):
		ent_name,part = where.split('_z_o_e_')

		data_dic['N°'] = self.set_ident_of(part,data_dic.get('id'))
		success_dic = self.success_response(data_dic,where,action)
		#print(success_dic)
		await self.ws.broadcast_table_update(ent_name,success_dic)

		return success_dic
		

	async def verif_what_to_send(self,data,where):
		dic = data.get('data')
		#print(f"#################\n{dic}\n###################")
		if dic:
			id = dic.get('id')
			dic['N°'] = self.set_ident_of(where,id)
			return self.success_response(dic,where,"save")
		else:
			raise Exception("Erreur inconus")
			#return self.failed_response(dic,where,"save","Erreur au niveau du serveur! Critique")

	def set_ident_of(self,part,ident):
		if part.lower() == 'rupin':
			raise ValueError("info nnot ")
		p = part[:3].upper()
		if isinstance(ident,(int,float)):
			ident = str(int(ident))
			while len(ident) < 5:
				ident = "0"+ident
			ident = f'{p}N°{ident}'
		return ident

	def get_ident_of(self,ident):
		if ident and isinstance(ident,(str,)):
			if 'N°' in ident:
				id = ident.split('N°')[1]
			else:
				#print(ident)
				id = ident
			ident = int(id)
		return ident


	# ------------------
	def redo_ident(self,where):
		if where:
			p = "1234567890_"+string.ascii_lowercase
			th_txt = str()
			for i in where.lower():
				if i not in p:
					i = "xx"
				th_txt += i
			return th_txt
		return str()

	def _up_cache_local(self,where,data,id = None):
		with self._lock_dict.setdefault(where,threading.Lock()):
			tab_dic = self._local_cache.get(where,dict())
			if id:
				tab_dic[id] = data
			else:
				tab_dic.update(data)
			self._local_cache[where] = tab_dic


	