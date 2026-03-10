#Coding:utf-8
"""
	Gestion de connexion
"""
class depenses:
	def __init__(self):
		...

	def get_depense_model_info(self):
		return {
			'user':str(),
			"opérateur":str(),
			"motif":str(),
			"date":self.get_today(),
			"heure":self.get_hour(),
			'montant':float(),
		}

	async def save_depenses(self,ent_name,dic):
		where = await self.set_my_where(ent_name,self.depense_fic)
		th_d = self.get_depense_model_info()
		th_d.update(dic)
		_data = await self.save_data(where,th_d)
		if _data.get('status') == 'ok':
			data = _data.get('data')

			motif = data.get('motif')
			mont = data.get('montant')
			date = data.get('date')

			if motif.lower() in ("paiement livreur","paiement prestataire"):
				user = data.get('user')
				await self.save_depense_of_this(ent_name,user,mont)
			
			await self.save_hist_into(ent_name,self.depense_fic,
				data.get("N°"),date)
			
			await self.save_this_depense(ent_name,mont,motif)
			
		return await self.verif_what_to_send(_data, self.depense_fic)

	async def modif_depenses(self,ent_name,dic):
		return await self.save_depenses(ent_name,dic)
		
	async def get_depenses(self,ent_name,ident):
		where = await self.set_my_where(ent_name,self.depense_fic)
		data = await self.get_data(where,record_id = ident)
		return await self.verif_what_to_send(data, self.depense_fic)

	async def delete_this_depense(self,ent_name,ident):
		where = await self.set_my_where(ent_name,self.depense_fic)
		data = await self.delete_data(where,record_id = ident)
		return await self.verif_what_to_send(data, self.depense_fic)

# Message handler
	async def depense_message_handler(self,msg):
		action = msg.get('action').lower()
		ent_name = msg.get('base_name')
		data = msg.get('data')
		id = msg.get('id')
		date = msg.get('date')

		if action == "save":
			return await self.save_depenses(ent_name,data)
		elif action == "get":
			return await self.get_depenses(ent_name,id)
		elif action == 'delete':
			return await self.delete_this_depense(ent_name,id)
		elif action == "update":
			return await self.modif_depenses(ent_name,data)
		elif action == 'get-history':
			return await self.get_hist_from(ent_name,self.depense_fic,date)
			
