#Coding:utf-8

class general:
	def __init__(self):
		...

	async def get_general_info(self,ent_name,part:str=None):
		general_dic = await self.get_general(ent_name)
		if part:
			return general_dic.get(part,dict())
		else:
			return general_dic

	async def get_general(self,ent_name):
		where = await self.set_my_where(ent_name,self.general_fic)
		_general_dic = await self.get_data(where,record_id = 1)
		th_general = _general_dic.get('data')
		return th_general.get(1,dict())

	async def save_general(self,ent_name,dic):
		where = await self.set_my_where(ent_name,self.general_fic)
		await self.save_data(where,dic)

	async def set_general_info(self,ent_name,part,data):
		where = await self.set_my_where(ent_name,self.general_fic)
		general_dic = await self.get_general(ent_name)
		part_d = general_dic.get(part,dict())
		part_d.update(dict(data))
		general_dic[part] = part_d
		await self.save_general(ent_name,general_dic)

# Enrégistrement des idents 
	async def save_id_into(self,ent_name,part,ident):
		data = {ident:self.set_ident_of(part,ident)}
		await self.set_general_info(ent_name,part,data)

	async def get_id_from(self,ent_name,part):
		return await self.get_general_info(ent_name,part)

	async def delete_id_from(self,ent_name,part,ident):
		data = await self.get_general_info(ent_name,part)
		if ident in data:
			data.pop(ident)
			await self.set_general_info(ent_name,part,data)

# enrégistrement des historiques
	async def save_hist_into(self,ent_name,part,ident,date):
		hist = await self.get_general_info(ent_name,part)
		date_list = hist.setdefault(date,list())
		if ident not in date_list:
			date_list.append(ident)
			hist[date] = date_list
			await self.set_general_info(ent_name,part,hist)

	async def get_hist_from(self,ent_name,part,date=None):
		all_dic = await self.get_general_info(ent_name,part)
		if date:
			return all_dic.get(date)
		else:
			return all_dic

	async def delete_hist_from(self,ent_name,part,date,ident):
		data = await self.get_hist_from(ent_name,part)
		date_lis = data.get(date,list())
		if ident in date_list:
			date_list.remove(ident)
			data[date] = date_list
			await self.set_general_info(ent_name,part,data)



