#Coding:utf-8

class finances:
	def __init__(self):
		...

	async def get_finance(self,ent_name):
		where = await self.set_my_where(ent_name,self.finance_fic)
		_finance_dic = await self.get_data(where,record_id = 1)
		th_finance = _finance_dic.get('data')
		return th_finance

	async def _get_finance(self,ent_name):
		where = await self.set_my_where(ent_name,self.finance_fic)
		_finance_dic = await self.get_data(where,record_id = 1)
		return await self.verif_what_to_send(_finance_dic, self.recette_fic)

	async def modif_finance(self,ent_name,dic):
		await self.save_finance(ent_name,dic)

	async def save_finance(self,ent_name,dic):
		where = await self.set_my_where(ent_name,self.finance_fic)
		await self.save_data(where,dic)

	async def save_this_recette(self,ent_name,cmd_mont,liv_mont,ref,recet_id):
		com_dic = await self.get_commission(ent_name)
		cmd_com = float(cmd_dic.get("commande",.1))
		liv_com = float(cmd_dic.get("livraison",.12))

		finance_dic = await self.get_finance(ent_name)

		gene_solde = float(finance_dic.setdefault("solde général",0))
		presta_solde = float(finance_dic.setdefault("solde prestataire",0))
		liv_solde = float(finance_dic.setdefault("solde livreur",0))
		com_solde = float(finance_dic.setdefault("solde commission",0))

		gene_solde += cmd_mont
		gene_solde += liv_mont

		comm_cmd = (cmd_mont * cmd_com)
		comm_liv = (liv_mont * liv_com)
		comm = comm_cmd + comm_liv
		com_solde += comm

		presta_mon = cmd_mont - comm_cmd
		liv_mon = liv_mont - comm_liv

		liv_solde += liv_mon
		presta_solde += presta_mon

		finance_dic["solde général"] = gene_solde
		finance_dic["solde prestataire"] = presta_solde
		finance_dic["solde livreur"] = liv_solde
		finance_dic["solde commission"] = com_solde

		await self.modif_finance(ent_name,finance_dic)

		await self.update_soldes(ent_name,recet_id,ref, presta_mon,liv_mon)

	async def save_this_depense(self,ent_name,mont,motif):
		finance_dic = await self.get_finance(ent_name)
		gene_solde = finance_dic.get('solde général',int())
		gene_solde -= mont
		finance_dic["solde général"] = gene_solde
		if motif.lower() == "paiement livreur":
			liv_solde = finance_dic.get('solde livreur',int())
			liv_solde -= mont
			finance_dic['solde livreur'] = liv_solde
		elif motif.lower() == "paiement prestataire":
			presta_solde = finance_dic.get('solde prestataire',int())
			presta_solde -= mont
			finance_dic['solde prestataire'] = presta_solde
		else:
			com_solde = finance_dic.get("solde commission",int())
			com_solde -= mont
			finance_dic['solde commission'] = com_solde
		await self.modif_finance(ent_name,finance_dic)

	async def update_soldes(self,ent_name,recet_id,ref,presta_mon,liv_mon):
		_cmd_dic = await self.get_commandes(ent_name,int(ref.split("N°")[-1]))
		if _cmd_dic.get('status') == "ok":
			cmd_dic = _cmd_dic.get('data')
			presta = cmd_dic.get('prestataire')
			liv = cmd_dic.get('livreur')
			if presta:
				await self.save_recette_of_this(ent_name,presta,
					recet_id,presta_mon)
			if liv:
				await self.save_recette_of_this(ent_name,liv,
					recet_id,liv_mon)

# Handler
	def finance_message_handler(self,msg):
		action = msg.get('action').lower()
		ent_name = msg.get('base_name')
		data = msg.get('data')
		id = msg.get('id')
		date = msg.get('date')

		if action == "save":
			return await self.save_finance(ent_name,data)
		elif action == "get":
			return await self._get_finance(ent_name)
		elif action == "update":
			return await self.modif_finance(ent_name,data)
		
			

