#Coding:utf-8
"""
	Gestion de connexion
"""
class livraisons:
	def __init__(self):
		...

	def get_livraison_model_info(self):
		return {
			'client':str(),
			'prestataire':str(),
			'livreur':str(),
			'commande':str(),
			'menus':dict(),
			"date":self.get_today(),
			'montant':float(),
			"status":"en cours",
		}

	async def save_livraisons(self,ent_name,dic):
		where = await self.set_my_where(ent_name,self.livraison_fic)
		th_d = self.get_livraison_model_info()
		th_d.update(dic)
		data = await self.save_data(where,th_d)
		if data:
			cmd_id = data.get('commande')
			liv_id = data.get('id')
			person_id = data.get('livreur')
			date = data.get('date')

			await self.save_hist_into(ent_name,self.livraison_fic,
				data.get("N°"),date)
			await self.set_livraison_id(ent_name,cmd_id,liv_id,person_id)
		return await self.verif_what_to_send(data, self.livraison_fic)

	async def modif_livraisons(self,ent_name,dic):
		return await self.save_livraisons(ent_name,dic)
		
	async def get_livraisons(self,ent_name,ident):
		where = await self.set_my_where(ent_name,self.livraison_fic)
		data = await self.get_data(where,record_id = ident)
		return await self.verif_what_to_send(data, self.livraison_fic)

	async def delete_this_livraison(self,ent_name,ident):
		where = await self.set_my_where(ent_name,self.livraison_fic)
		data = await self.delete_data(where,record_id = ident)
		return await self.verif_what_to_send(data, self.livraison_fic)


# Message handler
	async def livraison_message_handler(self,msg):
		action = msg.get('action').lower()
		ent_name = msg.get('base_name')
		data = msg.get('data')
		id = msg.get('id')
		date = msg.get('date')

		if action == "save":
			return await self.save_livraisons(ent_name,data)
		elif action == "get":
			return await self.get_livraisons(ent_name,id)
		elif action == 'delete':
			return await self.delete_this_livraison(ent_name,id)
		elif action == "update":
			return await self.modif_livraisons(ent_name,data)
		elif action == 'get-history':
			return await self.get_hist_from(ent_name,self.livraison_fic,date)

