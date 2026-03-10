#Coding:utf-8
"""
	Gestion de connexion
"""
class articles:
	def __init__(self):
		...

	def get_article_model_info(self):
		return {
			'désignation':str(),
			'catégorie':str(),
			'prestataire':str(),
			"img":'media/logo.png',
			'prix':float(),
			"date":self.sc.get_today(),
			"status":"en traitement",#disponible #indisponible
			'commandes':dict(),
		}

	async def save_articles(self,ent_name,dic):
		where = await self.set_my_where(ent_name,self.article_fic)
		th_d = self.get_article_model_info()
		th_d.update(dic)
		_data = await self.save_data(where,th_d)
		if _data.get('status') == 'ok':
			data = _data.get('data')
			m_id = data.get('N°')
			cat_id = data.get('catégorie')
			prix = data.get('prix')
			us_id = data.get("prestataire")
			await self.save_article_to_prest(ent_name, us_id, m_id, prix)
			await self.save_article_of(ent_name, cat_id, m_id, prix)
			await self.save_id_into(ent_name,self.article_fic,data.get("id"))
		return await self.verif_what_to_send(_data, self.article_fic)

	async def modif_articles(self,ent_name,dic):
		return await self.save_articles(ent_name,dic)
		
	async def get_articles(self,ent_name,ident):
		where = await self.set_my_where(ent_name,self.article_fic)
		data = await self.get_data(where,record_id = ident)
		return await self.verif_what_to_send(data, self.article_fic)

	async def delete_this_article(self,ent_name,ident):
		where = await self.set_my_where(ent_name,self.article_fic)
		data = await self.delete_data(where,record_id = ident)
		return await self.verif_what_to_send(data, self.article_fic)

# Gestion divers
	async def save_cmd_of_th_article(self,ent_name,article_id,cmd_id,qte):
		_th_article = await self.get_articles(ent_name,article_id)
		if _th_article.get('status') == "ok":
			th_article = _th_article.get('data')
			cmds = th_article.get('commandes')
			th_qte = cmds.get(cmd_id,int())
			if th_qte != qte:
				cmds[cmd_id] = qte
				th_article['commandes'] = cmds
				await self.modif_articles(ent_name,th_article)
		else:
			print(_th_article)

# Message handler
	async def article_message_handler(self,msg):
		action = msg.get('action').lower()
		ent_name = msg.get('base_name')
		data = msg.get('data')
		id = msg.get('id')
		date = msg.get('date')

		if action == "save":
			return await self.save_articles(ent_name,data)
		elif action == "get":
			return await self.get_articles(ent_name,id)
		elif action == 'delete':
			return await self.delete_this_article(ent_name,id)
		elif action == "update":
			return await self.modif_articles(ent_name,data)
		elif action == 'get-history':
			return await self.get_id_from(ent_name,self.article_fic)
			





