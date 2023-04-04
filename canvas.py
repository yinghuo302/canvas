from item import ItemDesc
from utils import Point
from PyQt5.QtWidgets import (
    QGraphicsView,
    QMessageBox,
    QColorDialog,
)
from PyQt5.QtGui import QMouseEvent, QColor
from PyQt5.QtCore import Qt,pyqtSignal
from oprecord import OPRecord


class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """
    actionChanged = pyqtSignal()
    def __init__(self, *args):
        super().__init__(*args)
        self.main_window = None
        self.list_widget = None
        self.tmp_type = 'freenom'
        self.alg = ''
        self.tmp_id = '0'
        self.color = QColor(0,0,0)
        self.selected_id = ''
        self.op_record = OPRecord(self)
        self.tmp_desc:ItemDesc|None = None

    def reset(self,h=None,w=None):
        h = h if h else self.height()
        w = w if w else self.width()
        self.clearSelection()
        self.op_record.clear()
        self.setFixedSize(h, w)
        self.tmp_id,self.tmp_desc,self.color = '0',None,QColor(0,0,0)
        self.op_record.view = self

    def start(self, type:str,algorithm:str) -> bool:
        if type == 'clip':
            if not self.op_record.canClip(self.selected_id):
                QMessageBox.warning(self,"type error","只支持线段的裁剪",QMessageBox.Ok)
                self.tmp_type = 'freenom'
                return False
        self.tmp_id = self.main_window.get_id(self.tmp_desc!=None)
        self.tmp_type,self.alg,self.tmp_desc = type,algorithm,None
        if self.tmp_type in ItemDesc.DRAW:
            self.clearSelection()
        return True

    def clearSelection(self):
        if self.selected_id != '':
            self.op_record.select(self.selected_id,False)
            self.selected_id = ''
        self.list_widget.clearSelection()

    def selectionChanged(self, selected):
        self.main_window.statusBar().showMessage('图元选择： %s' % selected)
        if self.selected_id != '':
            self.op_record.select(self.selected_id,False)
        if selected != '':
            self.selected_id = selected
            self.op_record.select(self.selected_id)
        self.tmp_type = "freenom"

    def setColor(self):
        temp_color = QColorDialog.getColor()
        if temp_color.isValid():
            self.color = temp_color

    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x,y = int(pos.x()), int(pos.y())
        if self.tmp_type not in ItemDesc.DRAW:
            if self.selected_id == '':
                QMessageBox.warning(self,"type error","请选择需要变换的元素",QMessageBox.Ok)
                self.tmp_type = 'freenom'
                return 
            self.tmp_id = self.selected_id
        if self.tmp_desc:
            self.tmp_desc.p_list.append(Point(x,y))
        else:
            self.tmp_desc = ItemDesc(self.tmp_id,self.tmp_type,[Point(x,y),Point(x,y)],self.alg,self.color)
            self.op_record.do(self.tmp_desc)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x,y = int(pos.x()),int(pos.y())
        if self.tmp_type == "freenom":
            self.tmp_desc.p_list.append(Point(x,y))
        else:
            self.tmp_desc.p_list[-1] = Point(x,y)
        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.main_window.modified = True
        if self.op_record.finish():
            self.tmp_desc = None
        self.tmp_id = self.main_window.get_id(self.tmp_type in ItemDesc.INC)
        super().mouseReleaseEvent(event)
    
    def deleteItem(self):
        if self.selected_id == '':
            QMessageBox.warning(self,"Error","请选择需要删除的元素",QMessageBox.Ok)
        else:
            self.op_record.delete(self.selected_id)

    def saveToFile(self,file_name):
        self.op_record.saveToFile(file_name)
    
    def loadFromFile(self,file_name):
        self.reset()
        self.op_record.loadFromFile(file_name)
    
    def addToListWidget(self,id):
        if not self.list_widget.findItems(id, Qt.MatchContains):
            self.list_widget.addItem(id)

    def removeFromListWidget(self,id):
        self.clearSelection()
        number = self.list_widget.findItems(id, Qt.MatchContains)
        row = self.list_widget.row(number[0])
        self.list_widget.takeItem(row)