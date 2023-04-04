import pickle
from typing import List,Dict
from item import ItemDesc,MyItem
from PyQt5.QtWidgets import(
	QGraphicsView
)
import algorithms as alg
from PyQt5.QtGui import QColor

class OPRecord:
	def __init__(self,view:QGraphicsView) -> None:
		self.redo_stk:List[ItemDesc] = []
		self.undo_stk:List[ItemDesc] = []
		self.view:QGraphicsView = view
		self.item_mp:Dict[str,MyItem] = {}
		self.tmp_item = None
	
	def redo(self):
		if not self.canRedo():
			return 
		desc = self.redo_stk[-1]
		self.redo_stk.pop()
		self.view.clearSelection()
		self.do(desc,False)
		self.finish()

	def undo(self):
		if not self.canUndo():
			return
		desc = self.undo_stk[-1]
		self.undo_stk.pop()
		self.redo_stk.append(desc)
		self.view.clearSelection()
		if desc.extra == "delete":
			desc  = desc.copy()
			desc.extra = None
			item = MyItem(desc)
			self.view.scene().addItem(item)
			self.view.addToListWidget(desc.id)
			self.item_mp[desc.id] = item
		elif desc.item_type in ItemDesc.DRAW:
			self.deleteItem(desc.id)
		else:
			item = self.item_mp[desc.id]
			item.desc.p_list=alg.p_transform(desc.item_type,item.desc.p_list,desc.p_list,desc.algorithm,True)
			desc.p_list = desc.extra if desc.item_type == "clip" else desc.p_list
			desc.extra = None
		self.view.actionChanged.emit()
		self.view.scene().update()

	def do(self,desc:ItemDesc,clear=True):
		self.undo_stk.append(desc)
		if clear:
			self.redo_stk.clear()
		self.tmp_item = MyItem(desc)
		if desc.extra == "delete":
			self.deleteItem(desc.id)
		elif desc.item_type == "clip":
			desc.item_type,desc.extra,desc.color = "rect","clip",QColor(255,0,0)
			self.view.scene().addItem(self.tmp_item)
		elif desc.item_type in ItemDesc.DRAW:
			self.view.scene().addItem(self.tmp_item)
			self.item_mp[desc.id] = self.tmp_item
		else:
			self.item_mp[desc.id].desc.extra = desc
		self.view.actionChanged.emit()
		self.view.scene().update()
	
	def finish(self) -> bool:
		trans = self.undo_stk[-1]
		if trans.extra == "delete":
			return False
		item = self.item_mp[trans.id]
		trans.item_type = "clip" if trans.extra == "clip" else trans.item_type			
		if trans.item_type not in ItemDesc.DRAW:
			desc = item.desc
			p_list = alg.p_transform(trans.item_type,desc.p_list,trans.p_list,trans.algorithm)
			if trans.item_type == "clip" :
				trans.extra,trans.p_list  = trans.p_list , desc.p_list
				self.view.scene().removeItem(self.tmp_item)
			desc.extra, desc.p_list = None , p_list
		self.view.addToListWidget(trans.id)
		self.view.scene().update()
		return trans.item_type not in ItemDesc.APPEND

	def saveToFile(self,file_name):
		file = open(file_name,"wb")
		h,w = self.view.height(),self.view.width()
		pickle.dump([h,w,self.undo_stk,self.redo_stk], file)

	def loadFromFile(self,file_name):
		file = open(file_name,"rb")
		objs = pickle.load(file)
		self.view.reset(objs[0],objs[1])
		for op in objs[2]:
			self.do(op)
			self.finish()
		self.redo_stk = objs[3]

	def select(self,id,selected = True):
		self.item_mp[id].desc.selected = selected
		self.view.scene().update()

	def delete(self,item_id):
		desc = self.item_mp[item_id].desc.copy()
		desc.extra = "delete"
		self.do(desc)
	
	def clear(self):
		self.redo_stk.clear()
		self.undo_stk.clear()
		self.item_mp.clear()
		self.view.scene().clear()
		self.view.actionChanged.emit()

	def deleteItem(self,id):
		self.view.removeFromListWidget(id)
		self.view.scene().removeItem(self.item_mp[id])
		self.item_mp.pop(id)

	def canClip(self,id) -> bool:
		return self.item_mp[id].desc.item_type == "line"
	
	def canRedo(self) -> bool:
		return len(self.redo_stk) != 0
	
	def canUndo(self) -> bool:
		return len(self.undo_stk) != 0