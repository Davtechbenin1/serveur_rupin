#Coding:utf-8
"""
	Gestion de connexion
"""
class recettes:
	def __init__(self):
		...

	def get_recette_model_info(self):
		return {
			'client':str(),
			'reférence':str(),
			"opérateur":str(),
			"motif":str(),
			"date":self.get_today(),
			"heure":self.get_hour(),
			'montant':float(),
			"cmd montant":float(),
			"liv montant":float(),
		}

	async def save_recettes(self,ent_name,dic):
		where = await self.set_my_where(ent_name,self.recette_fic)
		th_d = self.get_recette_model_info()
		th_d.update(dic)
		_data = await self.save_data(where,th_d)
		if _data.get('status') == 'ok':
			data = _data.get('data')
			
			recet_id = data.get('N°')
			client = data.get('client')
			mont = data.get('montant')
			date = data.get('date')

			ref = data.get('reférence')

			cmd_mont = data.get('cmd montant')
			liv_mont = data.get('liv montant')
			
			await self.save_hist_into(ent_name,self.recette_fic,
				data.get("N°"),date)
			
			await self.save_recette_of_this(ent_name,client,cmd_id,mont)
			
			await self.save_this_recette(ent_name,cmd_mont,liv_mont,ref,recet_id)

		return await self.verif_what_to_send(_data, self.recette_fic)

	async def modif_recettes(self,ent_name,dic):
		return await self.save_recettes(ent_name,dic)
		
	async def get_recettes(self,ent_name,ident):
		where = await self.set_my_where(ent_name,self.recette_fic)
		data = await self.get_data(where,record_id = ident)
		return await self.verif_what_to_send(data, self.recette_fic)

	async def delete_this_recette(self,ent_name,ident):
		where = await self.set_my_where(ent_name,self.recette_fic)
		data = await self.delete_data(where,record_id = ident)
		return await self.verif_what_to_send(data, self.recette_fic)

# Message handler
	async def recette_message_handler(self,msg):
		action = msg.get('action').lower()
		ent_name = msg.get('base_name')
		data = msg.get('data')
		id = msg.get('id')
		date = msg.get('date')

		if action == "save":
			return await self.save_recettes(ent_name,data)
		elif action == "get":
			return await self.get_recettes(ent_name,id)
		elif action == 'delete':
			return await self.delete_this_recette(ent_name,id)
		elif action == "update":
			return await self.modif_recettes(ent_name,data)
		elif action == 'get-history':
			return await self.get_hist_from(ent_name,self.recette_fic,date)
			
