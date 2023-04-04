import math
from typing import Any, Callable, Dict, List

from utils import Point, PointF, sign

def draw_line(p_list:List[Point], algorithm:str) -> List[Point]:
    """绘制线段

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    if len(p_list) < 2:
        return p_list
    a,b = p_list[0].copy(),p_list[1].copy()
    if a.equal(b):
        return [a]
    result:List[Point] = []
    
    sign_x,sign_y = sign(b.x-a.x),sign(b.y-a.y)
    if a.x == b.x:
        for y in range(a.y,b.y+sign_y,sign_y):
            result.append(Point(a.x,y))
        return result
    k = a.slope(b)
    if algorithm == 'Naive':	
        for x in range(a.x,b.x+sign_x,sign_x):
            result.append(Point(x,k*(x-a.x)+a.y))	
    elif algorithm == 'DDA':
        if abs(k) > 1:
            x_step =  sign_y / k
            x_begin = a.x
            for y in range(a.y,b.y+sign_y,sign_y):
                result.append(Point(x_begin,y))
                x_begin += x_step
        else:
            y_step =  sign_x * k
            y_begin = a.y
            for x in range(a.x,b.x+sign_x,sign_x):
                result.append(Point(x,y_begin))
                y_begin += y_step
    else:
        dy = abs(b.y-a.y)
        dx = abs(b.x-a.x)
        if abs(k) > 1:
            p = 2 * dx -dy
            x_begin = a.x
            for y in range(a.y,b.y+sign_y,sign_y):
                result.append(Point(x_begin,y))
                if p > 0:
                    x_begin += sign_x
                    p -= 2*dy
                p += 2 * dx
        else:
            p = 2 * dy - dx
            y_begin = a.y
            for x in range(a.x,b.x+sign_x,sign_x):
                result.append(Point(x,y_begin))
                if p > 0:
                    y_begin += sign_y
                    p -= 2*dx
                p += 2 *dy
    return result

def draw_polygon(p_list:List[Point], algorithm:str) -> List[Point]:
    """绘制多边形

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    if len(p_list) == 2:
        return draw_line(p_list,algorithm)
    result:list[Point] = []
    for i in range(len(p_list)):
        result.extend(draw_line([p_list[i - 1], p_list[i]], algorithm))        
    return result

def draw_rect(p_list:List[Point],algorithm:str) -> List[Point]:
    p0,p1 = p_list[0:2]
    sign_x,sign_y = sign(p1.x - p0.x),sign(p1.y-p0.y)
    res:List[Point] = []
    if sign_x == 0 or sign_y == 0:
        return res
    for x in range(p0.x,p1.x+sign_x,sign_x):
        res.extend([Point(x,p0.y),Point(x,p1.y)])
    for y in range(p0.y,p1.y+sign_y,sign_y):
        res.extend([Point(p0.x,y),Point(p1.x,y)])
    return res

def draw_ellipse(p_list:List[Point],alg:str) -> List[Point]:
    """绘制椭圆（采用中点圆生成算法）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 椭圆的矩形包围框左上角和右下角顶点坐标
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    p0,p1 = p_list[0].copy(),p_list[1].copy()
    if p0.x > p1.x:
        p0.x,p1.x = p1.x,p0.x
    if p0.y > p1.y:
        p0.y,p1.y = p1.y,p0.y
    rx,ry =  (p1.x-p0.x)/ 2, (p1.y-p0.y)/2
    rx2,ry2 = rx*rx,ry*ry
    xc,yc =  (p1.x+p0.x)/ 2, (p1.y+p0.y)/2
    x,y = 0,ry
    quadrant:List[Point] = [Point(x,y)]
    p = ry2 - rx2*ry + rx2/4
    while ry2*x < rx2*y:
        if p >= 0:
            y -= 1
            p += 2*rx2*(1-y)
        p += ry2*(3+2*x)
        x += 1
        quadrant.append(Point(x,y))
    p = ry2*(x+0.5)*(x+0.5) + rx2*(y-1)*(y-1) - rx2*ry2
    while y > 0 :
        if p <= 0:
            x +=1
            p += 2*ry2*(1+x)
        y -= 1
        p += rx2 * (3-2*y)
        quadrant.append(Point(x,y))
    result = [Point(nx*p.x+xc-0.001,ny*p.y+yc-0.001) for p in quadrant for nx in (-1, 1) for ny in (-1, 1)]
    return result


def draw_curve(p_list:List[Point], algorithm:str) -> List[Point]:
    """绘制曲线
    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    u,du = 0,0.001
    n = len(p_list)
    res:List[Point] = []
    if algorithm == 'Bezier':
        while u <= 1:
            p_copy = [PointF(p.x,p.y) for p in p_list]
            for i in range(n):
                for j in range(n-1-i):
                    p0,p1 = p_copy[j],p_copy[j+1]
                    p_copy[j] = PointF((1-u)*p0.x + u*p1.x, (1-u)*p0.y + u*p1.y)
            res.append(Point(int(p_copy[0].x+0.5),int(p_copy[0].y+0.5)))
            u += du
    else:
        def b_spline3_vector(u:float) -> List[float]:
            temp = [(-u**3+3*u**2-3*u+1)/6, (3*u**3-6*u**2+4)/6, (-3*u**3+3*u**2+3*u+1)/6, (u**3)/6]
            return temp

        def b_spline3_mul(mat:List[float],p_list:List[Point]) -> Point:
            x,y = 0,0
            for i in range(4):
                x += p_list[i].x * mat[i]
                y += p_list[i].y * mat[i]
            return Point(x,y)
        if n <= 3:
            return []
        while u <= 1:
            vector = b_spline3_vector(u)
            for i in range(n-3):
                res.append(b_spline3_mul(vector,p_list[i:i+4]))
            u += du
    return res

def draw_freenom(p_list:List[Point],alg):
    return p_list

def translate(p_list:List[Point], dx:int|str, dy:int|str) -> List[Point]:
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    dx,dy = int(dx),int(dy)
    return [Point(p.x + dx, p.y + dy) for p in p_list]


def rotate(p_list:List[Point], x:int|str, y:int|str, r:float|str,flag:bool = False) -> List[Point]:
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度
    :param flag: (bool) 表示使用的单位，为True表示使用弧度制
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    x,y,r = int(x),int(y),float(r)
    theta = r if flag else (r / 360 * 2 * math.pi)
    cos = math.cos(theta)
    sin = math.sin(theta)
    return [Point((p.x-x)*cos-(p.y-y)*sin+x,(p.x-x)*sin+(p.y-y)*cos+y) for p in p_list]


def scale(p_list:List[Point], x:int|str, y:int|str, s:float|str,sy:float|str = 0) -> List[Point]:
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    x,y,s,sy = int(x),int(y),float(s),float(sy)
    sy = s if sy == 0 else sy
    return [ Point((p.x-x)*s + x, (p.y - y)*sy + y) for p in p_list ]


def clip(p_list:List[Point],x_min:int|str,y_min:int|str,x_max:int|str,y_max:int|str,alg:str) -> List[Point]:
    """线段裁剪

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param x_min: 裁剪窗口左上角x坐标
    :param y_min: 裁剪窗口左上角y坐标
    :param x_max: 裁剪窗口右下角x坐标
    :param y_max: 裁剪窗口右下角y坐标
    :param algorithm: (string) 使用的裁剪算法，包括'Cohen-Sutherland'和'Liang-Barsky'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1]]) 裁剪后线段的起点和终点坐标
    """
    x_min,y_min,x_max,y_max = int(x_min),int(y_min),int(x_max),int(y_max)
    p0,p1 = p_list[0].copy(),p_list[1].copy()
    if x_min > x_max:
        x_max, x_min = x_min, x_max
    if y_min > y_max:
        y_max, y_min = y_min, y_max
    if alg == 'Cohen-Sutherland':
        LEFT,RIGHT,BOTTOM,TOP = 1,2,4,8
        LR,TB = LEFT+RIGHT,TOP+BOTTOM
        def encode(x, y):
            ret = 0
            ret |= (LEFT if x < x_min else 0)
            ret |= (RIGHT if x > x_max else 0)
            ret |= (BOTTOM if y < y_min else 0)
            ret |= (TOP if y > y_max else 0)
            return ret
        while True:
            code0,code1 = encode(p0.x,p0.y),encode(p1.x,p1.y)
            if (code0&code1)!=0:
                return []
            if (code0|code1)==0:
                return [p0,p1]
            if code0 == 0:
                p0,p1 = p1,p0
            code = encode(p0.x,p0.y)
            x,y = p0.x,p0.y
            if code & LR:
                x = x_min if code & LEFT else x_max
                y = round(p0.slope(p1) *(x - p0.x) + p0.y)
            elif code & TB:
                y = y_max if code & TOP else y_min
                x = (y-p0.y) * p0.slope_y(p1) + p0.x
            p0.x,p0.y = int(x),int(y)
    else:
        p = [p0.x - p1.x, p1.x - p0.x, p0.y - p1.y, p1.y - p0.y]
        q = [p0.x - x_min, x_max - p0.x, p0.y - y_min, y_max - p0.y]
        rn1,rn2 = 0,1
        for i in range(0,4):
            if p[i] == 0: 
                if q[i] < 0:
                    return []
            elif p[i] < 0:
                rn1 = max(rn1,q[i]/p[i])
            else:
                rn2 = min(rn2,q[i]/p[i])
        if rn1 > rn2:
            return []
        return [Point(p0.x+(p1.x-p0.x)*rn1,p0.y+(p1.y-p0.y)*rn1),Point(p0.x+(p1.x-p0.x)*rn2,p0.y+(p1.y-p0.y)*rn2)]

DRAW_TYPE = Callable[[List[Point],str],List[Point]]
DRAW_FUNC:Dict[str,DRAW_TYPE] = {
    'line':draw_line,'polygon':draw_polygon,'ellipse':draw_ellipse,'curve':draw_curve,'rect':draw_rect,
    'freenom':draw_freenom
}

TRANS_FUNC_TYPE = Callable[[List[Point],Any],List[Point]]
TRANS_FUNC = {
    'translate':translate,'rotate':rotate,'scale':scale,'clip':clip
}

def draw(type:str,p_list:List[Point],alg:str) -> List[Point] :
    return DRAW_FUNC[type](p_list,alg)

def transform(type:str,args) -> List[Point]:
    return TRANS_FUNC[type](*args)

# 变换的参数由点的形式给出
def p_transform(type:str,origin:List[Point],ctr_p:List[Point],alg:str,undo=False) -> List[Point]:
    p0,p1 = ctr_p[0:2]
    if type == 'translate':
        dx,dy = p1.x - p0.x,p1.y - p0.y
        if undo:
            dx,dy = -dx,-dy
        return translate(origin,dx,dy)
    elif type == 'rotate':
        if p0.equal(p1):
            return origin
        theta = math.pi/2 if p1.x == p0.x else math.atan(p0.slope(p1))
        theta = theta if p1.x > p0.x else theta + math.pi
        theta = 2 * math.pi - theta if undo else theta
        return rotate(origin,p0.x,p0.y,theta,True)
    elif type == 'scale':
        # if undo:
        #     return ctr_p
        # x_min,y_min = origin[0].x,origin[0].y
        # for p in origin:
        #     x_min,y_min = min(x_min,p.x),min(y_min,p.y)
        # if x_min == p0.x or y_min == p0.y or p0.x == p1.x or p0.y == p1.y:
        #  or :
            
        # sx,sy = abs((p1.x - p0.x)/(x_min - p0.x) ),abs((p1.y - p0.y) /(y_min - p0.y))
        sx = abs((p1.x - p0.x)/50)  if p0.x != p1.x else 1
        sy = abs((p1.y - p0.y) /50) if p0.y != p1.y else 1
        if undo:
            sx,sy = 1/sx,1/sy
        return scale(origin,p0.x,p0.y,sx,sy)
    else:
        if undo:
            return ctr_p
        return clip(origin,p0.x,p0.y,p1.x,p1.y,alg)
