from utils import Point
import algorithms as alg
from typing import List, Optional
from PyQt5.QtWidgets import (
    QGraphicsItem,
    QWidget,
    QStyleOptionGraphicsItem,
)
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QRectF

class ItemDesc:
    DRAW = ["line","polygon","ellipse","curve","freenom","rect"]
    APPEND = ["polygon","curve","freenom"]
    INC = ["line","ellipse"]
    # IRREVERSIBLE = ["clip","scale"]
    def __init__(self,item_id: str, item_type: str, p_list: list, algorithm: str = '',color:QColor = QColor(0,0,0)) -> None:
        self.id = item_id           # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list:List[Point] = p_list        # 图元参数
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.selected = False
        self.color = color
        self.extra:str|ItemDesc = None

    def copy(self) -> 'ItemDesc':
        return ItemDesc(self.id,self.item_type,self.p_list,self.algorithm,self.color)

class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """
    def __init__(self, desc:ItemDesc, parent: QGraphicsItem = None):
        """
        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param parent:
        """
        super().__init__(parent)
        self.desc = desc
    
    @staticmethod
    def draw(type,p_list,algr,painter:QPainter,color):
        item_pixels = alg.draw(type,p_list,algr)
        painter.setPen(color)
        for p in item_pixels:
            painter.drawPoint(p.x,p.y)
    
    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        p_list,desc,extra = self.desc.p_list,self.desc,self.desc.extra
        if isinstance(extra,ItemDesc):
            p_list = alg.p_transform(extra.item_type,p_list,extra.p_list,extra.algorithm)
        MyItem.draw(desc.item_type,p_list,desc.algorithm,painter,desc.color)
        if desc.item_type == 'curve':
            MyItem.draw('polygon',p_list,'',painter,QColor(0,0,255))
        if desc.selected:
            painter.setPen(QColor(255, 0, 0))
            painter.drawRect(self.boundingRect())

    def boundingRect(self) -> List[Point]:
        p_list,extra = self.desc.p_list,self.desc.extra
        if isinstance(extra,ItemDesc):
            p_list = alg.p_transform(extra.item_type,p_list,extra.p_list,extra.algorithm)
        x_min,x_max,y_min,y_max = 100000,-1,10000,-1
        for p in p_list:
            x_min,x_max = min(x_min,p.x),max(x_max,p.x)
            y_min,y_max = min(y_min,p.y),max(y_max,p.y)
        return QRectF(x_min-1,y_min-1,x_max-x_min+2,y_max-y_min+2 )
    
    def setPList(self,p_list):
        self.desc.p_list = p_list