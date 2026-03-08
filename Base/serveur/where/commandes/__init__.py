#Coding:utf-8
"""
	Gestion de connexion
"""
class commandes:
	def __init__(self):
		...

	def get_commande_model_info(self):
		return {
			'client':str(),
			'prestataire':str(),
			'livreur':str(),
			'livraison':str(),
			'menus':dict(),
			"date":self.get_today(),
			"heure":self.get_hour(),
			'montant':float(),
			"status":'en attente',
			"status paye":'non payée',
		}

	async def save_commandes(self,ent_name,dic):
		where = await self.set_my_where(ent_name,self.commande_fic)
		th_d = self.get_commande_model_info()
		th_d.update(dic)
		_data = await self.save_data(where,th_d)
		if _data.get('status') == 'ok':
			data = _data.get('data')
			client = data.get('client')
			prest = data.get('prestataire')
			cmd_id = data.get('N°')
			mont = data.get('montant')
			liv_id = data.get('livreur')
			date = data.get('date')
			await self.save_hist_into(ent_name,self.commande_fic,
				data.get("N°"),date)
			
			await self.save_cmd_of_this(ent_name,client,cmd_id,mont)
			await self.save_cmd_of_this(ent_name,prest,cmd_id,mont)

			all_menu = data.get('menus')
			for m_id in all_menu:
				d = all_menu[m_id]
				qte = d.get("qté")
				await self.save_cmd_of(ent_name,m_id,cmd_id,qte)

			if liv_id:
				await self.save_cmd_of_this(ent_name,liv_id,cmd_id,mont)

		return await self.verif_what_to_send(_data, self.commande_fic)

	async def modif_commandes(self,ent_name,dic):
		return await self.save_commandes(ent_name,dic)
		
	async def get_commandes(self,ent_name,ident):
		where = await self.set_my_where(ent_name,self.commande_fic)
		data = await self.get_data(where,record_id = ident)
		return await self.verif_what_to_send(data, self.commande_fic)

	async def delete_this_commande(self,ent_name,ident):
		where = await self.set_my_where(ent_name,self.commande_fic)
		data = await self.delete_data(where,record_id = ident)
		return await self.verif_what_to_send(data, self.commande_fic)

# Gestion des informations divers
	async def set_livraison_id(self,ent_name,cmd_id,liv_id,person_id):
		cmd_dic = await self.get_commandes(ent_name,cmd_id)
		if cmd_dic.get('status') == "ok":
			cmd_dic = cmd_dic.get('data')
			cmd_dic['livreur'] = person_id
			cmd_dic['livraison'] = liv_id
			await self.modif_commandes(ent_name,cmd_dic)


# Message handler
	async def commande_message_handler(self,msg):
		action = msg.get('action').lower()
		ent_name = msg.get('base_name')
		data = msg.get('data')
		id = msg.get('id')
		date = msg.get('date')

		if action == "save":
			return await self.save_commandes(ent_name,data)
		elif action == "get":
			return await self.get_commandes(ent_name,id)
		elif action == 'delete':
			return await self.delete_this_commande(ent_name,id)
		elif action == "update":
			return await self.modif_commandes(ent_name,data)
		elif action == 'get-history':
			return await self.get_hist_from(ent_name,self.commande_fic,date)
			



	



