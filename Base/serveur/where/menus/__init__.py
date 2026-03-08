#Coding:utf-8
"""
	Gestion de connexion
"""
class menus:
	def __init__(self):
		...

	def get_menu_model_info(self):
		return {
			'désignation':str(),
			'catégorie':str(),
			'prestataire':str(),
			'prix':float(),
			"status":"en traitement",#disponible #indisponible
			"temps de cuisson":str(),
			'commandes':dict(),
		}

	async def save_menus(self,ent_name,dic):
		where = await self.set_my_where(ent_name,self.menu_fic)
		th_d = self.get_menu_model_info()
		th_d.update(dic)
		_data = await self.save_data(where,th_d)
		if _data.get('status') == 'ok':
			data = _data.get('data')
			m_id = data.get('N°')
			cat_id = data.get('catégorie')
			prix = data.get('prix')
			us_id = data.get("prestataire")
			await self.save_menu_to_prest(ent_name, us_id, m_id, prix)
			await self.save_menu_of(ent_name, cat_id, m_id, prix)
			await self.save_id_into(ent_name,self.menu_fic,data.get("id"))
		return await self.verif_what_to_send(_data, self.menu_fic)

	async def modif_menus(self,ent_name,dic):
		return await self.save_menus(ent_name,dic)
		
	async def get_menus(self,ent_name,ident):
		where = await self.set_my_where(ent_name,self.menu_fic)
		data = await self.get_data(where,record_id = ident)
		return await self.verif_what_to_send(data, self.menu_fic)

	async def delete_this_menu(self,ent_name,ident):
		where = await self.set_my_where(ent_name,self.menu_fic)
		data = await self.delete_data(where,record_id = ident)
		return await self.verif_what_to_send(data, self.menu_fic)

# Gestion divers
	async def save_cmd_of(self,ent_name,menu_id,cmd_id,qte):
		_th_menu = await self.get_menus(ent_name,menu_id)
		if _th_menu.get('status') == "ok":
			th_menu = _th_menu.get('data')
			cmds = th_menu.get('commandes')
			th_qte = cmds.get(cmd_id,int())
			if th_qte != qte:
				cmds[cmd_id] = qte
				th_menu['commandes'] = cmds
				await self.modif_menus(ent_name,th_menu)
		else:
			print(_th_menu)


# Message handler
	async def menu_message_handler(self,msg):
		action = msg.get('action').lower()
		ent_name = msg.get('base_name')
		data = msg.get('data')
		id = msg.get('id')
		date = msg.get('date')

		if action == "save":
			return await self.save_menus(ent_name,data)
		elif action == "get":
			return await self.get_menus(ent_name,id)
		elif action == 'delete':
			return await self.delete_this_menu(ent_name,id)
		elif action == "update":
			return await self.modif_menus(ent_name,data)
		elif action == 'get-history':
			return await self.get_id_from(ent_name,self.menu_fic)
			





