#Coding:utf-8
"""
	Rassemblement de toutes les informations de données
"""
from .categories import categories
from .commandes import commandes
from .general import general
from .livraisons import livraisons
from .menus import menus
from .users import users
from .articles import articles
from .commissions import commissions

class where(categories,commandes,general,livraisons,menus,
	users,articles,commissions):
	def __init__(self):
		categories.__init__(self)
		commandes.__init__(self)
		general.__init__(self)
		livraisons.__init__(self)
		menus.__init__(self)
		users.__init__(self)
		articles.__init__(self)
		commissions.__init__(self)

# Gestion des messages reçus du serveur
	async def manage_msg(self,msg):
		w = msg.get('where')
		fonc = self.where_fonc_hand.get(w)
		if fonc:
			return await fonc(msg)



