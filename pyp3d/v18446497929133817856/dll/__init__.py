# Copyright (C), 2019-2028, Beijing GLory PKPM Tech. Co., Ltd.
# Brief: PKPM-BIMBase Python二次开发SDK与参数化组件功能。
# Author: YouQi
# Date: 2021/08/07
from ..p3d_type import *
import math
sin = math.sin
cos = math.cos
pi = math.pi
sqrt = math.sqrt

@overload
def scale(factor_xyz:float):...
@overload
def scale(factor_x:float, factor_y:float):...
@overload
def scale(factor_x:float, factor_y:float, factor_z:float):...
@overload
def scale(factor:list):...
@overload
def scale(factor:tuple):...

@overload
def translate(vec:GeVec2d):...
@overload
def translate(vec:GeVec3d):...
@overload
def translate(x:float, y:float):...
@overload
def translate(x:float, y:float, z:float):...
@overload
def translate(factor:list):...
@overload
def translate(factor:tuple):...

@overload
def rotate(axis:GeVec3d, angle:float):...
@overload
def rotate(angle:float, axis:GeVec3d):...
@overload
def rotate(angle:float, axis:GeVec3d=GeVec3d(0,0,1)):...

def is_all_num(num)->bool: #判断对象是否为数字
    '''
    judge a object is Number(int or float), using recursion
    '''
    if isinstance(num, int) or isinstance(num, float):
        return True
    elif isinstance(num, list) or isinstance(num, tuple):
        for i in num:
            if is_all_num(i):
                continue
            else:
                return False
        return True
    else:
        return False

def is_num(num)->bool: #判断对象是否为数字，两层嵌套
    '''
    judge a object is Number(int or float) 
    '''
    if isinstance(num, int) or isinstance(num, float):
        return True
    elif isinstance(num, list) or isinstance(num, tuple):
        for i in num:
            if isinstance(i, int) or isinstance(i, float):
                continue
            elif (isinstance(i, list) or isinstance(i, tuple)) and len(num)==1:
                for j in i: #two-layer nesting, to compat (*agrs)
                    if isinstance(j, int) or isinstance(j, float):
                        continue
                    else:
                        return False
            else:
                return False
        return True
    else:
        return False

def is_same_direction(vec1: GeVec3d,vec2: GeVec3d):
    if isinstance(vec1, GeVec3d) and isinstance(vec2, GeVec3d):
        if norm(vec1)*norm(vec2)<1e-10:
            raise ValueError('please donot input zero vector!')
        if abs(dot(vec1,vec2)-norm(vec1)*norm(vec2))<1e-10:
            return True
        elif abs(dot(vec1,vec2)+norm(vec1)*norm(vec2))<1e-10:
            return -1
        else:
            return False
    else:
        raise ValueError('please input two GeVec3d!')

def norm(vec: GeVec3d)->float: #计算模长（二范数）
    '''
    the absolute length of vector
    '''
    return sqrt(vec.x*vec.x + vec.y*vec.y + vec.z*vec.z)

def unitize(vec: GeVec3d)->GeVec3d: #计算单位矢量
    '''
    convert a vector to be a unit vector
    '''
    # if vec.x==0.0 and vec.y==0.0 and vec.z==0.0: 
    if abs(vec.x)+abs(vec.y)+abs(vec.z)<1e-10: 
        raise ValueError('zero-vector has no unit vector!')
    inv_norm = 1.0 / norm(vec)
    return GeVec3d(vec.x*inv_norm, vec.y*inv_norm, vec.z*inv_norm)

def linspace(a, b, n)->list: #产生线性分布
    if isinstance(a, GeVec3d) and isinstance(b, GeVec3d): 
        return [GeVec3d(x, y, z) for (x, y, z) in zip(linspace(a.x, b.x, n), linspace(a.y, b.y, n), linspace(a.z, b.z, n))]
    elif (isinstance(a, int) or isinstance(a, float)) and (isinstance(b, int) or isinstance(b, float)):
        if n==1:
            d = a
        else:
            d = (b-a)/(n-1)
        return list(map(lambda x: a+x*d, range(n)))
    else: 
        raise TypeError('improper parameter!')

def dot(a: GeVec3d, b: GeVec3d)->float: #矢量点积
    '''
    vector dot product
    '''
    return a.x*b.x + a.y*b.y + a.z*b.z

def cross(a: GeVec3d, b: GeVec3d)->GeVec3d: #矢量叉积
    '''
    vector cross product
    '''
    return GeVec3d(a.y*b.z-a.z*b.y, a.z*b.x-a.x*b.z, a.x*b.y-a.y*b.x)

def scale(*args): #缩放矩阵
    '''
    Genetate a scale zoom matrix
    '''
    if len(args) == 1 :
        if isinstance(args[0],int) or isinstance(args[0],float):
            return GeTransform([[args[0], 0, 0, 0], [0, args[0], 0, 0], [0, 0, args[0], 0]])
        elif len(args[0])==3 and (isinstance(args[0],list) or isinstance(args[0],tuple)) and is_num(args[0]):
            return GeTransform([[args[0][0], 0, 0, 0], [0, args[0][1], 0, 0], [0, 0, args[0][2], 0]])
        elif len(args[0])==2 and (isinstance(args[0],list) or isinstance(args[0],tuple)) and is_num(args[0]):
            return GeTransform([[args[0][0], 0, 0, 0], [0, args[0][1], 0, 0], [0, 0, 1, 0]])
        else: raise ValueError('improper parameter!')
    elif len(args) == 2 and is_num(args):
        return GeTransform([[args[0], 0, 0, 0], [0, args[1], 0, 0], [0, 0, 1, 0]])
    elif len(args) == 3 and is_num(args):
        return GeTransform([[args[0], 0, 0, 0], [0, args[1], 0, 0], [0, 0, args[2], 0]])
    else: raise ValueError('improper parameter!')

def translate(*args): #平移矩阵
    '''
    Genetate a translation matrix
    '''
    if len(args) == 1 :
        if isinstance(args[0],GeVec3d): 
            return GeTransform([[1, 0, 0, args[0].x], [0, 1, 0, args[0].y], [0, 0, 1, args[0].z]])
        elif isinstance(args[0],GeVec2d): 
            return GeTransform([[1, 0, 0, args[0].x], [0, 1, 0, args[0].y], [0, 0, 1, 0]])
        elif len(args[0])==3 and (isinstance(args[0],list) or  isinstance(args[0],tuple)) and is_num(args[0]):
            return GeTransform([[1, 0, 0, args[0][0]], [0, 1, 0, args[0][1]], [0, 0, 1, args[0][2]]])
        elif len(args[0])==2 and (isinstance(args[0],list) or  isinstance(args[0],tuple)) and is_num(args[0]):
            return GeTransform([[1, 0, 0, args[0][0]], [0, 1, 0, args[0][1]], [0, 0, 1, 0]])
        else: raise ValueError('improper parameter!')
    elif len(args) == 2 and is_num(args): 
        return GeTransform([[1, 0, 0, args[0]], [0, 1, 0, args[1]], [0, 0, 1, 0]])
    elif len(args) == 3 and is_num(args): 
        return GeTransform([[1, 0, 0, args[0]], [0, 1, 0, args[1]], [0, 0, 1, args[2]]])
    else: raise ValueError('improper parameter!')

def rotate(*args):
    '''
    Generate a rotation matrix, using axis-angle method (radian)
    '''
    if len(args) == 1 and is_num(args):
        nv, angle = GeVec3d(0,0,1), float(args[0])
    elif len(args) == 1 and isinstance(args[0],GeVec3d):
        return GeTransform()
    elif len(args) == 2:
        if isinstance(args[0], GeVec3d) and is_num(args[1]): 
            nv, angle = unitize(args[0]), float(args[1])
        elif isinstance(args[1], GeVec3d) and is_num(args[0]): 
            nv, angle = unitize(args[1]), float(args[0])
        else: raise TypeError('improper parameter!')
    else: raise ValueError('improper parameter!')
    # Rodrigues' rotation formula
    c, s = 1-cos(angle), sin(angle)
    T = GeTransform([[0.0, -nv.z*c, nv.y*c, 0.0], [nv.z*c, 0.0, -nv.x*c, 0.0], [-nv.y*c, nv.x*c, 0.0, 0.0]]) * \
        GeTransform([[0.0, -nv.z, nv.y, 0.0], [nv.z, 0.0, -nv.x, 0.0], [-nv.y, nv.x, 0.0, 0.0]])
    return GeTransform([[T._mat[0][0]+1.0, T._mat[0][1]-nv.z*s, T._mat[0][2]+nv.y*s, 0.0], 
                        [T._mat[1][0]+nv.z*s, T._mat[1][1]+1.0, T._mat[1][2]-nv.x*s, 0.0], 
                        [T._mat[2][0]-nv.y*s, T._mat[2][1]+nv.x*s, T._mat[2][2]+1.0, 0.0]])

def arbitrary_rotate(q:GeVec3d, f:GeVec3d, theta): # 绕过点q的矢量f,旋转theta弧度
    '''
    appoint point and vector to rotate
    '''
    return translate(q)*rotate(f,theta)*translate(-q)

def rotx(theta): # 基本旋转矩阵
    return GeTransform([[1,0,0,0],[0,cos(theta),-sin(theta),0],[0,sin(theta),cos(theta),0]])

def roty(theta):
    return GeTransform([[cos(theta),0,sin(theta),0],[0,1,0,0],[-sin(theta),0,cos(theta),0]])

def rotz(theta):
    return GeTransform([[cos(theta),-sin(theta),0,0],[sin(theta),cos(theta),0,0],[0,0,1,0]])

def rot(axis, theta):
    if isinstance(axis, str):
        if (axis=='x' or axis=='X'):
            return rotx(theta)
        elif (axis=='y' or axis=='Y'):
            return roty(theta)
        elif (axis=='z' or axis=='Z'):
            return rotz(theta)
        else:
            raise TypeError('Must assign coord axis rotate!')
    elif isinstance(axis, GeVec3d):
        if is_same_direction(GeVec3d(1,0,0), axis):
            return rotx(theta)
        elif is_same_direction(GeVec3d(0,1,0), axis):
            return roty(theta)
        elif is_same_direction(GeVec3d(0,0,1), axis):
            return rotz(theta)
        else:
            raise TypeError('Must assign coord axis rotate!')
    else:
        raise TypeError('Must assign coord axis rotate!')

def reflect(*arg): 
    if len(arg)==1:
        if isinstance(arg[0], str):
            # 关于坐标轴的反射变换
            if arg[0]=='x' or arg[0]=='X':
                return GeTransform([[1,0,0,0],[0,-1,0,0],[0,0,-1,0]])
            elif arg[0]=='y' or arg[0]=='Y':
                return GeTransform([[-1,0,0,0],[0,1,0,0],[0,0,-1,0]])
            elif arg[0]=='z' or arg[0]=='Z':
                return GeTransform([[-1,0,0,0],[0,-1,0,0],[0,0,1,0]])
            # 关于坐标平面的反射变换
            elif arg[0]=='xy' or  arg[0]=='XY' or arg[0]=='yx' or  arg[0]=='YX':
                return GeTransform([[1,0,0,0],[0,1,0,0],[0,0,-1,0]])
            elif arg[0]=='yz' or arg[0]=='YZ' or arg[0]=='zy' or  arg[0]=='ZY':
                return GeTransform([[-1,0,0,0],[0,1,0,0],[0,0,1,0]])
            elif arg[0]=='zx' or arg[0]=='ZX' or arg[0]=='xz' or  arg[0]=='XZ':
                return GeTransform([[1,0,0,0],[0,-1,0,0],[0,0,1,0]])
            # 关于原点的反射变换
            elif arg[0]=='o' or arg[0]=='O':
                return GeTransform([[-1,0,0,0],[0,-1,0,0],[0,0,-1,0]])
            else:
                raise TypeError('Must assign proper parameter!')
        elif isinstance(arg[0], GeVec3d):
            if is_same_direction(GeVec3d(1,0,0), arg[0]):
                return GeTransform([[1,0,0,0],[0,-1,0,0],[0,0,-1,0]])
            elif is_same_direction(GeVec3d(0,1,0), arg[0]):
                return GeTransform([[-1,0,0,0],[0,1,0,0],[0,0,-1,0]])
            elif is_same_direction(GeVec3d(0,0,1), arg[0]):
                return GeTransform([[-1,0,0,0],[0,-1,0,0],[0,0,1,0]])
            elif norm(arg[0])<1e-10:
                return GeTransform([[-1,0,0,0],[0,-1,0,0],[0,0,-1,0]])
            else:
                raise TypeError('Must assign proper argument!')
        else:
            raise TypeError('Must assign proper argument!')
    elif len(arg)==2:
        if isinstance(arg[0], GeVec3d) and isinstance(arg[1], GeVec3d):
            axis3=cross(arg[0],arg[1])
            if is_same_direction(GeVec3d(0,0,1), axis3) or is_same_direction(GeVec3d(0,0,1), axis3)==-1:
                return GeTransform([[1,0,0,0],[0,1,0,0],[0,0,-1,0]])
            elif is_same_direction(GeVec3d(1,0,0), axis3) or is_same_direction(GeVec3d(1,0,0), axis3)==-1:
                return GeTransform([[-1,0,0,0],[0,1,0,0],[0,0,1,0]])
            elif is_same_direction(GeVec3d(0,1,0), axis3) or is_same_direction(GeVec3d(0,1,0), axis3)==-1:
                return GeTransform([[1,0,0,0],[0,-1,0,0],[0,0,1,0]])
            else:
                raise TypeError('please input proper argument!')
        else:
            raise TypeError('please input proper argument!')
    else:
        raise TypeError('please input proper argument!')

def shear(axis, * ,x=0, y=0, z=0): # 三维错切矩阵
    ''' * enforce using keyword to pass args
    generate shear matrix
    '''
    # return GeTransform([[1,b,c,0],[d,1,f,0],[g,h,1,0]])
    if isinstance(axis, str):
        # 指定单位基准坐标轴的偏移距离
        if axis=='x' or axis=='X': # x轴错切
            # d、g为单位x轴末端，向y、z方向平行偏移的距离
            return GeTransform([[1,0,0,0],[y,1,0,0],[z,0,1,0]])
        elif axis=='y' or axis=='Y': # y轴错切
            # b、h为单位x轴末端，向x、z方向平行偏移的距离
            return GeTransform([[1,x,0,0],[0,1,0,0],[0,z,1,0]])
        elif axis=='z' or axis=='Z': # z轴错切
            # c、f为单位x轴末端，向x、y方向平行偏移的距离
            return GeTransform([[1,0,x,0],[0,1,y,0],[0,0,1,0]])
        # 其他轴向指定轴偏移错切
        elif axis=='tox' or axis=='toX': # 向x轴错切
            # 单位y、z末端平行偏移的距离b、c
            return GeTransform([[1,y,z,0],[0,1,0,0],[0,0,1,0]])
        elif axis=='toy' or axis=='toY': # 向y轴错切
            # 单位x、z末端平行偏移的距离d、f
            return GeTransform([[1,0,0,0],[x,1,z,0],[0,0,1,0]])
        elif axis=='toz' or axis=='toZ': # 向z轴错切
            # 单位x、y末端平行偏移的距离g、h
            return GeTransform([[1,0,0,0],[0,1,0,0],[x,y,1,0]])
        else:
            raise TypeError('please input proper argument!')
    # 指定轴
    elif isinstance(axis, GeVec3d):
        if is_same_direction(GeVec3d(1,0,0), axis):
            return GeTransform([[1,0,0,0],[y,1,0,0],[z,0,1,0]])
        elif is_same_direction(GeVec3d(0,1,0), axis):
            return GeTransform([[1,x,0,0],[0,1,0,0],[0,z,1,0]])
        elif is_same_direction(GeVec3d(0,0,1), axis):
            return GeTransform([[1,0,x,0],[0,1,y,0],[0,0,1,0]])
        else:
            raise TypeError('please input proper argument!')
    else:
        raise TypeError('please input proper argument!')

def inverse(M:GeTransform)->GeTransform:
    '''
    generate a inverse matrix of the input matrix
    '''
    if not isinstance(M,GeTransform):
        raise TypeError('parameter must be matrix!')
    T_inv=GeTransform([[1,0,0,-M._mat[0][3]],[0,1,0,-M._mat[1][3]],[0,0,1,-M._mat[2][3]]])
    a11=M._mat[0][0]
    a12=M._mat[0][1]
    a13=M._mat[0][2]
    a21=M._mat[1][0]
    a22=M._mat[1][1]
    a23=M._mat[1][2]
    a31=M._mat[2][0]
    a32=M._mat[2][1]
    a33=M._mat[2][2]
    M_det=a11*a22*a33 + a12*a23*a31 + a13*a32*a21 - a13*a22*a31 - a12*a21*a33 - a11*a32*a23
    if abs(M_det)<1e-10:
        raise TypeError('matrix determinant value is zero!')
    b11=a22*a33-a23*a32
    b12=a21*a33-a23*a31
    b13=a21*a32-a22*a31
    b21=a12*a33-a13*a32
    b22=a11*a33-a13*a31
    b23=a11*a32-a12*a31
    b31=a12*a23-a13*a22
    b32=a11*a23-a13*a21
    b33=a11*a22-a12*a21
    M_adj=GeTransform([[b11,-b21,b31,0], #transpose matrix
                    [-b12,b22,-b32,0],
                    [b13,-b23,b33,0]])
    return (1/M_det)*M_adj*T_inv
