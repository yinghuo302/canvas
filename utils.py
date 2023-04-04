from typing import Any

class Point:
	x:int
	y:int
	def __init__(self,x:Any,y:Any) -> None:
		if isinstance(x,float):
			x = round(x)
		if isinstance(y,float):
			y = round(y)
		self.x,self.y = int(x),int(y)
	
	def equal(self,p:'Point') -> bool :
		return p.x == self.x and p.y == self.y 

	def slope(self,other:'Point') -> float:
		return (self.y - other.y) / (self.x-other.x)

	def slope_y(self,other:'Point') -> float:
		return (self.x-other.x) / (self.y - other.y)
	
	def copy(self) -> 'Point':
		return Point(self.x,self.y)

class PointF:
	x:float
	y:float
	def __init__(self,x:Any,y:Any) -> None:
		self.x,self.y = float(x),float(y)
	
	def slope(self,other:'PointF') -> float:
		return (self.y - other.y) / (self.x-other.x)

	def slope_y(self,other:'PointF') -> float:
		return (self.x-other.x) / (self.y - other.y)
	
	def copy(self) -> 'PointF':
		return PointF(self.x,self.y)

def sign(x:int) -> int :
	if x > 0:
		return 1
	elif x == 0:
		return 0
	return -1