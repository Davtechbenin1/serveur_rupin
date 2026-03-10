#Coding:utf-8

class commissions:
	def __init__(self):
		...

	async def get_commission(self,ent_name):
		where = await self.set_my_where(ent_name,self.commission_fic)
		_commission_dic = await self.get_data(where,record_id = 1)
		th_commission = _commission_dic.get('data')
		return th_commission

	async def modif_commission(self,ent_name,dic):
		await self.save_commission(ent_name,dic)

	async def save_commission(self,ent_name,dic):
		where = await self.set_my_where(ent_name,self.commission_fic)
		await self.save_data(where,dic)

# Handler
	async def commission_message_handler(self,msg):
		action = msg.get('action').lower()
		ent_name = msg.get('base_name')
		data = msg.get('data')
		id = msg.get('id')
		date = msg.get('date')

		if action == "save":
			return await self.save_commission(ent_name,data)
		elif action == "get":
			return await self.get_commission(ent_name,id)
		elif action == "update":
			return await self.modif_commission(ent_name,data)
		
			

