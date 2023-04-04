from functools import partial
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    qApp,
    QGraphicsScene,
    QListWidget,
    QHBoxLayout,
    QWidget,
    QMessageBox,
    QInputDialog,
    QAction,
    QFileDialog,
)
from canvas import MyCanvas
from PyQt5.QtGui import QImage,QPainter,QColor

class MainWindow(QMainWindow):
    """
    主窗口类
    """
    def __init__(self):
        super().__init__()
        self.item_cnt = 0

        # 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(200)

        # 使用QGraphicsView作为画布
        self.scene = QGraphicsScene(self)
        h,w = 600,600
        self.scene.setSceneRect(0, 0, h, w)
        self.canvas:MyCanvas = MyCanvas(self.scene, self)
        self.canvas.setFixedSize(h, w)
        self.canvas.main_window = self
        self.canvas.list_widget = self.list_widget
        self.modified = False
        self.file_name = ''
        # 设置菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        file_menu.addAction('设置画笔').triggered.connect(self.canvas.setColor)
        file_menu.addAction('重置画布').triggered.connect(self.resetCanvas)
        file_menu.addAction('调整画布大小').triggered.connect(partial(self.resetCanvas,True))
        file_menu.addAction('保存画布').triggered.connect(self.save_slot)
        file_menu.addAction('加载画布').triggered.connect(self.load_slot)
        file_menu.addAction('导出画布').triggered.connect(self.export_slot)
        file_menu.addAction('退出').triggered.connect(self.quit_slot)
        draw_menu = menubar.addMenu('DRAW')
        line_menu = draw_menu.addMenu('Line')
        line_menu.addAction('Naive')
        line_menu.addAction('DDA')
        line_menu.addAction('Bresenham')
        polygon_menu = draw_menu.addMenu('Polygon')
        polygon_menu.addAction('DDA')
        polygon_menu.addAction('Bresenham')
        draw_menu.addAction('Ellipse')
        curve_menu = draw_menu.addMenu('Curve')
        curve_menu.addAction('Bezier')
        curve_menu.addAction('B-spline')
        edit_menu = menubar.addMenu('Edit')
        edit_menu.addAction('translate')
        edit_menu.addAction('rotate')
        edit_menu.addAction('scale')
        clip_menu = edit_menu.addMenu('clip')
        clip_menu.addAction('Cohen-Sutherland')
        clip_menu.addAction('Liang-Barsky')
        history_menu = menubar.addMenu('历史记录')
        self.undo_action = history_menu.addAction('撤销')
        self.undo_action.triggered.connect(self.canvas.op_record.undo)
        self.redo_action = history_menu.addAction('重做')
        self.redo_action.triggered.connect(self.canvas.op_record.redo)
        self.delete_action = history_menu.addAction('删除')
        self.delete_action.triggered.connect(self.canvas.deleteItem)
        self.canvas.actionChanged.connect(self.updateMenu)
        self.updateMenu()
        # 连接信号和file_menu.children()槽函数
        for func_menu in [draw_menu,edit_menu]:
            for menu in func_menu.children():
                if isinstance(menu,QAction):
                    type = menu.text()
                    menu.triggered.connect(partial(self.draw_slot,type,''))
                    continue
                type = menu.title()
                for action in menu.children():
                    algr = action.text()
                    action.triggered.connect(partial(self.draw_slot,type,algr))                    
        self.list_widget.currentTextChanged.connect(self.canvas.selectionChanged)
        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('freenom')
        self.resize(h, w)
        self.setWindowTitle('CG Demo')
        self.canvas.start("freenom","")

    def get_id(self,inc=False):
        if inc:
            self.item_cnt += 1
        return str(self.item_cnt)
    
    def resetCanvas(self,resize=False):
        h,w = None,None
        if resize:
            h = QInputDialog.getInt(self, '请输入', '长度', 800, 200, 1500)[0]
            w = QInputDialog.getInt(self, '请输入', '宽度', 800, 200, 900)[0]
            self.scene.setSceneRect(0, 0, h, w)
        self.list_widget.clearSelection()
        self.list_widget.clear()
        self.item_cnt = 0
        self.file_name = ''
        self.canvas.reset(h,w)

    def draw_slot(self,type:str,algr:str):
        type = type.lower()
        if self.canvas.start(type,algr):
            self.statusBar().showMessage(type+'-'+algr)
    
    def quit_slot(self):
        if self.modified:
            ret = QMessageBox.question(self, '退出 - 是否保存', '是否保存当前草稿？', QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
            if ret == QMessageBox.Cancel:
                return 
            if ret == QMessageBox.Yes:
                self.save_slot()
        qApp.quit()
    
    def export_slot(self):
        file_name = QFileDialog.getSaveFileName(self,caption="导出画布", filter="bmp;;png;;jpg")
        if file_name[0] != '':
            scene = self.canvas.scene()
            scene.clearSelection()
            image = QImage(scene.sceneRect().size().toSize(), QImage.Format.Format_ARGB32)
            image.fill(QColor(255,255,255))
            painter = QPainter(image)
            scene.render(painter)
            image.save(file_name[0]+'.'+file_name[1])
            painter.end()
            
    def save_slot(self):
        if self.file_name == '':
            file_name = QFileDialog.getSaveFileName(self,caption="保存画布", filter="canvas")
            if file_name[0] == '':
                return 
            self.file_name = file_name[0] + '.' + file_name[1]
        self.canvas.saveToFile(self.file_name)

    def load_slot(self):
        file_name = QFileDialog.getOpenFileName(self,caption="加载画布", filter="画布(*.canvas)")
        if file_name[0] != '':
            self.file_name = file_name[0]
        self.canvas.loadFromFile(self.file_name)
    
    def closeEvent(self, e) -> None:
        self.quit_slot()
        return super().closeEvent(e)

    def updateMenu(self):
        self.undo_action.setEnabled(self.canvas.op_record.canUndo())
        self.redo_action.setEnabled(self.canvas.op_record.canRedo())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
