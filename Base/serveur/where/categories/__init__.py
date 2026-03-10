#Coding:utf-8
"""
	Gestion de connexion
"""
class categories:
	def __init__(self):
		...

	def get_categorie_model_info(self):
		return {
			"nom":str(),
			"menus":dict(),
			"articles":dict(),
		}

	async def save_categories(self,ent_name,dic):
		where = await self.set_my_where(ent_name,self.categorie_fic)
		th_d = self.get_categorie_model_info()
		th_d.update(dic)
		_data = await self.save_data(where,th_d)
		if _data:
			data = _data.get('data')
			await self.save_id_into(ent_name,self.categorie_fic,data.get("id"))
		return await self.verif_what_to_send(_data, self.categorie_fic)

	async def modif_categories(self,ent_name,dic):
		return await self.save_categories(ent_name,dic)
		
	async def get_categories(self,ent_name,ident):
		where = await self.set_my_where(ent_name,self.categorie_fic)
		data = await self.get_data(where,record_id = ident)
		return await self.verif_what_to_send(data, self.categorie_fic)

	async def delete_this_categorie(self,ent_name,ident):
		where = await self.set_my_where(ent_name,self.categorie_fic)
		data = await self.delete_data(where,record_id = ident)
		return await self.verif_what_to_send(data, self.categorie_fic)

# Gestion divers
	async def save_menu_of(self,ent_name,categorie_id,menu_id,mont):
		th_categorie = await self.get_categories(ent_name,categorie_id)
		if th_categorie.get('status') == "ok":
			th_categorie = th_categorie.get('data')
			cmds = th_categorie.get('menus',dict())
			th_qte = cmds.get(menu_id,int())
			if th_qte != mont:
				cmds[menu_id] = mont
				th_categorie['menus'] = cmds
				await self.modif_categories(ent_name,th_categorie)

	async def save_article_of(self,ent_name,categorie_id,article_id,mont):
		th_categorie = await self.get_categories(ent_name,categorie_id)
		if th_categorie.get('status') == "ok":
			th_categorie = th_categorie.get('data')
			cmds = th_categorie.get('articles',dict())
			th_qte = cmds.get(article_id,int())
			if th_qte != mont:
				cmds[article_id] = mont
				th_categorie['articles'] = cmds
				await self.modif_categories(ent_name,th_categorie)


# Message handler
	async def categorie_message_handler(self,msg):
		action = msg.get('action').lower()
		ent_name = msg.get('base_name')
		data = msg.get('data')
		id = msg.get('id')
		date = msg.get('date')

		if action == "save":
			return await self.save_categories(ent_name,data)
		elif action == "get":
			return await self.get_categories(ent_name,id)
		elif action == 'delete':
			return await self.delete_this_categorie(ent_name,id)
		elif action == "update":
			return await self.modif_categories(ent_name,data)
		elif action == 'get-history':
			return await self.get_id_from(ent_name,self.categorie_fic)
			




