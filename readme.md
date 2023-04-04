# 简介

该程序为一个简单的绘图程序，实现了直线，多边形，椭圆和曲线的绘制，并且可以对每一个单独的图元进行平移，旋转，放缩和对直线的裁剪操作。

## 使用说明

1. 安装程序依赖
  ```
		pip install -r requirements.txt
  ```
2.运行程序
  ```
		python gui.py
  ```
进入程序界面后默认为自由绘图模式，程序将记录鼠标所经过的每一个点，通过菜单项DRAW可以选择绘制图元的类型和算法，然后进行绘制。如果需要对图元进行变换，首先在右侧列表上选择图元，然后在菜单项EDIT可以选择变换的类型和算法，通过历史记录菜单项可以撤销重做和删除图元，通过文件菜单项可以选择画笔颜色，保存画笔，导出画布等。

## 系统框架

#### algorithm

1. 在`algorithm.py`编写`draw_line,draw_polygon,draw_ellipse,draw_curve`函数，这几个函数大多类似，可以将它们统一成同一个形式`def draw_polygon(p_list:List[Point], algorithm:str) -> List[Point]`，并且提供统一接口，根据输入参数点生成所有需要绘制的像素点的集合。
2. 同时完成`translate,rotate,scale,clip`函数，这几个函数参数类型各异，但是在`cg_cli.py`是从文件中读取字符串并且调用函数，所以可以将函数参数设定为字符串兼容型，提供统一接口`def transform(type:str,args) -> List[Point]`，`args`是不定项参数，包含一个`p_list`和变换所需的字符串类型参数，在命令行测试程序`test.py`中直接调用该函数进行测试。对于`canvas.py`，调用这些函数时会由几个控制点生成变换所需的参数，该过程由`p_transform`完成

#### test

命令行绘图程序的逻辑较为简单，每次读取一行指令，然后根据指令格式进行解析即可。遇到Draw指令将其转换为Item类储存起来，遇到变换指令调用algorithm的transform方法对Item的控制点进行变换，遇到saveCanvas调用algorithm的draw方法进行绘制。


#### OPRecord

**OPRecord**是图形界面绘制的核心部分，它维护两个栈**`redo_stk`和`undo_stk`**，并实现两个方法**`do`和`undo`**，`do`方法进行操作并将操作压入`undo_stk`栈并加入`QGraphicsScene`进行渲染，`undo`方法从`undo_stk`栈取出元素，进行撤销。而重做`redo`方法是通过`do`方法实现，从`redo_stk`栈取出元素，调用`do`方法。

#### Canvas

上层的Canvas类则只需要与UI交互，获取绘制和变换参数。Canvas类主要实现**mousePressEvent**，**mouseMoveEvent**，**mouseReleaseEvent**，完成参数获取。mousePressEvent调用OPRecord的`do`方法，mouseMoveEvent更新参数重新渲染，mouseReleaseEvent调用OPRecord的的`finish`方法，将mouseMoveEvent更新的额外参数进行保存。

#### Item

操作的内容通过`ItemDesc`进行记录。在绘图程序中所有的操作包括绘制和变换。其中绘制和变换都可以统一为`ItemDesc`，不过绘制需要添加进`QGraphicsScene`进行渲染，而变换影响绘制类`ItemDesc`的渲染，两者属性基本一致。`ItemDesc`的extra成员变量指向变换，在渲染时需要获取变换的属性，并实现delete和clip两种的特殊操作。
