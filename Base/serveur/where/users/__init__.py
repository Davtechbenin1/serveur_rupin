#Coding:utf-8
"""
	Gestion de connexion
"""
class users:
	def __init__(self):
		...

	def get_user_model_info(self):
		return {
			'nom':str(),
			'prénom':str(),
			'role':str(),
			'NPI':str(),
			"img":"media/logo.png",
			"solde":str(),
			"adresse":str(),
			"last adresse":str(),
			'téléphone':str(),
			'commandes':dict(),
			"livraisons":dict(),
			'paiements':dict(),
			"note":list(),
			"date d'ajout":self.get_today(),
			"état":"actif",
			"menus":dict(),
			"articles":dict(),
			'solde':float(),
		}

	async def save_users(self,ent_name,dic):
		where = await self.set_my_where(ent_name,self.user_fic)
		if not dic.get("role"):
			return self.failed_response(dic,where,"save","Le rôle est obligatoire")
		th_d = self.get_user_model_info()
		th_d.update(dic)
		data = await self.save_data(where,th_d)
		if data.get('status') == "ok":
			await self.save_id_into(ent_name,self.user_fic,
				data.get('data',dict()).get('id'))
			th_ = {
				"data":data
			}
		#print(f"-----------------\n{data}\n------------------")
		return await self.verif_what_to_send(data, self.user_fic)

	async def modif_users(self,ent_name,dic):
		#print(ent_name,dic)
		return await self.save_users(ent_name,dic)
		
	async def get_users(self,ent_name,ident):
		where = await self.set_my_where(ent_name,self.user_fic)
		data = await self.get_data(where,record_id = ident)
		return await self.verif_what_to_send(data, self.user_fic)

	async def delete_this_user(self,ent_name,ident):
		where = await self.set_my_where(ent_name,self.user_fic)
		data = await self.delete_data(where,record_id = ident)
		return await self.verif_what_to_send(data, self.user_fic)


# Gestion divers
	async def save_cmd_of_this(self,ent_name,user_id,cmd_id,cmd_mont,
			status,presta = False):
		_user = await self.get_users(ent_name,user_id)
		if _user.get('status') == 'ok':
			user = _user.get('data')
			if status == "livrée":
				if presta:
					user["solde"]+=float(cmd_mont)
				else:
					user["solde"]-=float(cmd_mont)
			old_mont = user['commandes'].get(cmd_id,int())
			if old_mont != cmd_mont:
				user["commandes"][cmd_id] = cmd_mont
				await self.modif_users(ent_name,user)
		else:
			print(ent_name,user_id,men_id,prix)
			print(_user)
		
	async def save_livraison_of_this(self,ent_name,user_id,cmd_id,cmd_mont):
		_user = await self.get_users(ent_name,user_id)
		if _user.get('status') == 'ok':
			user = _user.get('data')
			user["solde"]-=float(cmd_mont)
			old_mont = user['livraisons'].get(cmd_id,int())
			if old_mont != cmd_mont:
				user["livraisons"][cmd_id] = cmd_mont
				await self.modif_users(ent_name,user)
		else:
			print(ent_name,user_id,men_id,prix)
			print(_user)

	async def save_recette_of_this(self,ent_name,user_id,cmd_id,cmd_mont):
		_user = await self.get_users(ent_name,user_id)
		if _user.get('status') == 'ok':
			user = _user.get('data')
			user["solde"]+=float(cmd_mont)
			old_mont = user['paiements'].get(cmd_id,int())
			if old_mont != cmd_mont:
				user["paiements"][cmd_id] = cmd_mont
				await self.modif_users(ent_name,user)
		else:
			print(ent_name,user_id,men_id,prix)
			print(_user)

	async def save_depense_of_this(self,ent_name,user_id,cmd_mont):
		_user = await self.get_users(ent_name,user_id)
		if _user.get('status') == 'ok':
			user = _user.get('data')
			user["solde"]+=float(cmd_mont)
			await self.modif_users(ent_name,user)
		else:
			print(ent_name,user_id,men_id,prix)
			print(_user)

	async def save_menu_to_prest(self,ent_name,user_id,men_id,prix):
		_user = await self.get_users(ent_name,user_id)
		if _user.get('status') == 'ok':
			user = _user.get('data')
			old_mont = user['menus'].get(men_id,int())
			if old_mont != prix:
				user["menus"][men_id] = prix
				await self.modif_users(ent_name,user)
		else:
			print(ent_name,user_id,men_id,prix)
			print(_user)

	async def save_article_to_prest(self,ent_name,user_id,men_id,prix):
		_user = await self.get_users(ent_name,user_id)
		if _user.get('status') == 'ok':
			user = _user.get('data')
			old_mont = user['articles'].get(men_id,int())
			if old_mont != prix:
				user["articles"][men_id] = prix
				await self.modif_users(ent_name,user)
		else:
			print(ent_name,user_id,men_id,prix)
			print(_user)

# Message handler
	async def user_message_handler(self,msg):
		action = msg.get('action').lower()
		ent_name = msg.get('base_name')
		data = msg.get('data')
		id = msg.get('id')
		date = msg.get('date')

		if action == "save":
			return await self.save_users(ent_name,data)
		elif action == "get":
			return await self.get_users(ent_name,id)
		elif action == 'delete':
			return await self.delete_this_user(ent_name,id)
		elif action == "update":
			return await self.modif_users(ent_name,data)
		elif action == 'get-history':
			return await self.get_id_from(ent_name,self.user_fic)
			