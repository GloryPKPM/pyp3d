# Copyright (C), 2019-2028, Beijing GLory PKPM Tech. Co., Ltd.
# Brief: PKPM-BIMBase Python二次开发SDK与参数化组件功能。
# Author: YouQi, akingse
# Date: 2021/08/07

from .pyp3d_data import *
from math import *
import math

'''
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
'''
# -------------------------------------------------------------------------------
# lambda function
# lean_section = lambda pointY,pointX,theta:rotate(GeVec3d(0,0,1),atan2(pointY.y-pointX.y,pointY.x-pointX.x)+theta)
# translate2d = lambda point:GeTransform([[1,0,0,point.x], [0,1,0,point.y], [0,0,1,0]]) #原translate不支持GeVec2d
# transl = lambda point:translate(point) if (point is GeVec3d) else translate2d(point)
atan_posi = lambda y,x:atan2(y,x) if atan2(y,x) >=0 else atan2(y,x)+2*pi
angle_posi = lambda theta: theta+2*pi if theta<0 else theta # 弧度强转 0-2*pi
near_zero = lambda x: 0 if abs(x)<1e-10 or abs(abs(x)-2*pi)<1e-10 else x
is_zero = lambda x: True if abs(x) < 1e-10 else False
is_all_vec = lambda points: True if all(isinstance(i,(GeVec2d, GeVec3d)) for i in points) else False
is_all_vec2 = lambda points: True if all(isinstance(i,GeVec2d) for i in points) else False
is_all_vec3 = lambda points: True if all(isinstance(i,GeVec3d) for i in points) else False
atanp=atan_posi
posi=angle_posi
axisX = GeVec3d(1,0,0)
axisY = GeVec3d(0,1,0)
axisZ = GeVec3d(0,0,1)
# acos = pyp3d_matrix.acos
# sqrt = pyp3d_matrix.sqrt

def sqrt(x): #override base math funciton, to avoid floating devition.
    if abs(x)<1e-10:
        return 0.0
    else:
        return math.sqrt(x)

def acos(x):
    if abs(x-1)<1e-10:
        return 0.0
    elif abs(x+1)<1e-10:
        return pi
    else:
        return math.acos(x)

def is_all_num(num)->bool: #判断对象是否为数字
    '''
    judge a object is Number(int or float), using recursion
    '''
    if isinstance(num, (int,float)):
        return True
    elif isinstance(num, (list,tuple)):
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
    if isinstance(num, (int,float)):
        return True
    elif isinstance(num, (list,tuple)):
        for i in num:
            if isinstance(i, (int,float)):
                continue
            elif (isinstance(i, (list,tuple))) and len(num)==1:
                for j in i: #two-layer nesting, to compat (*agrs)
                    if isinstance(j, (int,float)):
                        continue
                    else:
                        return False
            else:
                return False
        return True
    else:
        return False

def is_same_direction(vec1: GeVec3d,vec2: GeVec3d): # 矢量同向判断
    '''
    if same direction return 1
    if opposite direction return -1
    else uncorrelated return 0 
    '''
    if isinstance(vec1, (GeVec2d,GeVec3d)) and isinstance(vec2, (GeVec2d,GeVec3d)):
        if norm(vec1)*norm(vec2)<1e-10:
            return 2 #raise ValueError('please donot input zero vector!')
        if abs(dot(vec1,vec2)-norm(vec1)*norm(vec2))<1e-10:
            return 1 #同向
        elif abs(dot(vec1,vec2)+norm(vec1)*norm(vec2))<1e-10:
            return -1 #反向
        else:
            return 0 #无关
    else:
        raise ValueError('please input two GeVec3d!')

def norm(vec)->float: #计算模长（二范数）
    '''
    the absolute length of vector
    '''
    if isinstance(vec,GeVec2d):
        return sqrt(vec.x*vec.x + vec.y*vec.y)
    elif isinstance(vec,GeVec3d):
        return sqrt(vec.x*vec.x + vec.y*vec.y + vec.z*vec.z)
    else:
        raise ValueError('please input a vector!')

def unitize(vec): #计算单位矢量
    '''
    convert a vector to be a unit vector
    '''
    if isinstance(vec,GeVec2d):
        if abs(vec.x)+abs(vec.y)<1e-10: 
            raise ValueError('zero-vector has no unit vector!')
        else:
            inv_norm = 1.0 / norm(vec)
            return GeVec2d(vec.x*inv_norm, vec.y*inv_norm)
    elif isinstance(vec,GeVec3d):
        if abs(vec.x)+abs(vec.y)+abs(vec.z)<1e-10: 
            raise ValueError('zero-vector has no unit vector!')
        else:
            inv_norm = 1.0 / norm(vec)
            return GeVec3d(vec.x*inv_norm, vec.y*inv_norm, vec.z*inv_norm)
    else:
        raise ValueError('please input a vector!')

def linspace(a, b, n)->list: #产生线性分布（按照点的个数）
    # 区分n，点的个数，段的个数
    if isinstance(a, GeVec3d) and isinstance(b, GeVec3d): 
        return [GeVec3d(x, y, z) for (x, y, z) in zip(linspace(a.x, b.x, n), linspace(a.y, b.y, n), linspace(a.z, b.z, n))]
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if n==1:
            d = a
        else:
            d = (b-a)/(n-1)
        return list(map(lambda x: a+x*d, range(n)))
    else: 
        raise TypeError('improper parameter!')

def dot(a: GeVec3d, b: GeVec3d)->float: #矢量点积
    '''
    two vectors dot product
    '''
    if isinstance(a,GeVec2d) and isinstance(b,GeVec2d):
        return a.x*b.x + a.y*b.y
    elif isinstance(a,GeVec3d) and isinstance(b,GeVec3d):
        return a.x*b.x + a.y*b.y + a.z*b.z
    else:
        raise TypeError('improper parameter!')

def cross(a: GeVec3d, b: GeVec3d)->GeVec3d: #矢量叉积
    '''
    two vectors cross product
    '''
    if isinstance(a,GeVec2d) and isinstance(b,GeVec2d):
        return GeVec3d(0, 0, a.x*b.y-a.y*b.x)
    elif isinstance(a,GeVec3d) and isinstance(b,GeVec3d):
        return GeVec3d(a.y*b.z-a.z*b.y, a.z*b.x-a.x*b.z, a.x*b.y-a.y*b.x)
    else:
        raise TypeError('improper parameter!')

def scale(*args)->GeTransform: # 缩放矩阵
    '''
    Genetate a scale zoom matrix
    '''
    if len(args) == 1 :
        if isinstance(args[0],(int,float)):
            return GeTransform([[args[0], 0, 0, 0], [0, args[0], 0, 0], [0, 0, args[0], 0]])
        elif len(args[0])==3 and isinstance(args[0],(list,tuple)) and is_num(args[0]):
            return GeTransform([[args[0][0], 0, 0, 0], [0, args[0][1], 0, 0], [0, 0, args[0][2], 0]])
        elif len(args[0])==2 and isinstance(args[0],(list,tuple)) and is_num(args[0]):
            return GeTransform([[args[0][0], 0, 0, 0], [0, args[0][1], 0, 0], [0, 0, 1, 0]])
        else: raise ValueError('improper parameter!')
    elif len(args) == 2 and is_num(args):
        return GeTransform([[args[0], 0, 0, 0], [0, args[1], 0, 0], [0, 0, 1, 0]])
    elif len(args) == 3 and is_num(args):
        return GeTransform([[args[0], 0, 0, 0], [0, args[1], 0, 0], [0, 0, args[2], 0]])
    else: raise ValueError('improper parameter!')

def translate(*args)->GeTransform: # 平移矩阵
    '''
    Genetate a translation matrix
    '''
    if len(args) == 1 :
        if isinstance(args[0],GeVec3d): 
            return GeTransform([[1, 0, 0, args[0].x], [0, 1, 0, args[0].y], [0, 0, 1, args[0].z]])
        elif isinstance(args[0],GeVec2d): 
            return GeTransform([[1, 0, 0, args[0].x], [0, 1, 0, args[0].y], [0, 0, 1, 0]])
        elif len(args[0])==3 and isinstance(args[0],(list,tuple)) and is_num(args[0]):
            return GeTransform([[1, 0, 0, args[0][0]], [0, 1, 0, args[0][1]], [0, 0, 1, args[0][2]]])
        elif len(args[0])==2 and isinstance(args[0],(list,tuple)) and is_num(args[0]):
            return GeTransform([[1, 0, 0, args[0][0]], [0, 1, 0, args[0][1]], [0, 0, 1, 0]])
        else: raise ValueError('improper parameter!')
    elif len(args) == 2 and is_num(args): 
        return GeTransform([[1, 0, 0, args[0]], [0, 1, 0, args[1]], [0, 0, 1, 0]])
    elif len(args) == 3 and is_num(args): 
        return GeTransform([[1, 0, 0, args[0]], [0, 1, 0, args[1]], [0, 0, 1, args[2]]])
    else: raise ValueError('improper parameter!')

def rotate(*args)->GeTransform: # 轴角表示法的旋转矩阵
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

def arbitrary_rotate(point:GeVec3d, vector:GeVec3d, theta)->GeTransform: # 绕过点q的矢量f,旋转theta弧度
    '''
    appoint point and vector to rotate
    '''
    return translate(point)*rotate(vector,theta)*translate(-point)

def rotx(theta)->GeTransform: # 基本旋转矩阵
    return GeTransform([[1,0,0,0],[0,cos(theta),-sin(theta),0],[0,sin(theta),cos(theta),0]])

def roty(theta)->GeTransform:
    return GeTransform([[cos(theta),0,sin(theta),0],[0,1,0,0],[-sin(theta),0,cos(theta),0]])

def rotz(theta)->GeTransform:
    return GeTransform([[cos(theta),-sin(theta),0,0],[sin(theta),cos(theta),0,0],[0,0,1,0]])

def rot(axis, theta)->GeTransform:
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
        else: # 旋转矩阵
            f=unitize(axis)
            c, s = cos(theta), sin(theta)
            T=GeTransform([[f.x*f.x*(1-c)+c,f.x*f.y*(1-c)-f.z*s,f.x*f.z*(1-c)+f.y*s,0],
                            [f.x*f.y*(1-c)+f.z*s,f.y*f.y*(1-c)+c,f.y*f.z*(1-c)-f.x*s,0],
                            [f.x*f.z*(1-c)-f.y*s,f.y*f.z*(1-c)+f.x*s,f.z*f.z*(1-c)+c,0]])
            return T
    else:
        raise TypeError('Must assign coord axis rotate!')

def reflect(*arg)->GeTransform: # 镜像反射矩阵
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

def shear(axis, * ,x=0, y=0, z=0)->GeTransform: # 三维错切矩阵
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

def set_matrix_by_column_vectors(vecX, vecY, vecZ, p=GeVec3d(0,0,0))->GeTransform: #通过列矢量创建旋转矩阵
    matrix=GeTransform([[vecX.x, vecY.x, vecZ.x, p.x],
                        [vecX.y, vecY.y, vecZ.y, p.y],
                        [vecX.z, vecY.z, vecZ.z, p.z]])
    return matrix

def set_matrix_by_rot_trans(rot:GeTransform, vec:GeVec3d)->GeTransform: #通过旋转和平移创建矩阵
    return translate(vec)*rot

def transpose(M:GeTransform)->GeTransform: #获取矩阵M的转置（纯姿态矩阵，位置参数清零）
    matrix=GeTransform([[M._mat[0][0],M._mat[1][0],M._mat[2][0],0*M._mat[0][3]],
                        [M._mat[0][1],M._mat[1][1],M._mat[2][1],0*M._mat[1][3]],
                        [M._mat[0][2],M._mat[1][2],M._mat[2][2],0*M._mat[2][3]]])
    return matrix

def inverse_std(M:GeTransform)->GeTransform: #刚性（rot+trans）变换矩阵的逆矩阵
    rotM=get_rot_matrix(M)
    transP=get_translate_para(M)
    return transpose(rotM)*translate(-transP)

def inverse(M:GeTransform)->GeTransform: #计算GeTransform的逆矩阵
    '''
    generate a inverse matrix of the input GeTransform matrix
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
    M_adj=GeTransform([[b11,-b21,b31,0], # been transpose matrix
                    [-b12,b22,-b32,0],
                    [b13,-b23,b33,0]])
    return (1/M_det)*M_adj*T_inv

def get_rot_matrix(m:GeTransform)->GeTransform: #获取矩阵的旋转部分，平移参数置零
    matrix=GeTransform([[m._mat[0][0],m._mat[0][1],m._mat[0][2],0],
                        [m._mat[1][0],m._mat[1][1],m._mat[1][2],0],
                        [m._mat[2][0],m._mat[2][1],m._mat[2][2],0]])
    return matrix

def get_rot_matrix_theta(m:GeTransform)->tuple: #获取(单位)旋转矩阵的逆变换(ZYZ欧拉角)
    nx=m._mat[0][0]
    ny=m._mat[1][0]
    nz=m._mat[2][0]
    # ox=m._mat[0][1]
    # oy=m._mat[1][1]
    oz=m._mat[2][1]
    ax=m._mat[0][2]
    ay=m._mat[1][2]
    az=m._mat[2][2]
    # theta2=atan2(-sqrt(nz**2+oz**2),az) #两组解中的一组
    theta2=atan2(sqrt(nz**2+oz**2),az)
    if abs(theta2)<1e-10:
        theta1=atan2(ny,nx)
        theta3=0
    else:
        s5=sin(theta2)
        theta3=atan2(oz/s5,-nz/s5)
        theta1=atan2(ay/s5,ax/s5)
    return (theta1,theta2,theta3)

def get_translate_para(m:GeTransform)->GeVec3d: # 获取矩阵的平移参数
    return GeVec3d(m._mat[0][3],m._mat[1][3],m._mat[2][3])

def get_translate_matrix(m:GeTransform)->GeTransform: # 获取矩阵的平移矩阵
    para=get_translate_para(m)
    return translate(para)

def get_scale_para(m:GeTransform)->tuple: # 获取矩阵的缩放参数
    a=sqrt(m._mat[0][0]**2+m._mat[1][0]**2+m._mat[2][0]**2)
    b=sqrt(m._mat[0][1]**2+m._mat[1][1]**2+m._mat[2][1]**2)
    c=sqrt(m._mat[0][2]**2+m._mat[1][2]**2+m._mat[2][2]**2)
    return (a,b,c)

def get_scale_matrix(m:GeTransform)->GeTransform:# 获取矩阵的缩放矩阵
    coef=get_scale_para(m)
    return scale(coef)

def get_matrix_axisx(m:GeTransform)->GeVec3d:
    vectorX=GeVec3d(m._mat[0][0], m._mat[1][0], m._mat[2][0])
    return unitize(vectorX)
def get_matrix_axisy(m:GeTransform)->GeVec3d:
    vectorY=GeVec3d(m._mat[0][1], m._mat[1][1], m._mat[2][1])
    return unitize(vectorY)
def get_matrix_axisz(m:GeTransform)->GeVec3d: #获取矩阵Z方向法向量（已单位化）
    vectorZ=GeVec3d(m._mat[0][2], m._mat[1][2], m._mat[2][2])
    return unitize(vectorZ)

def print_matrix(m:GeTransform)->None: # print 3x4 矩阵，测试专用
    print("↓---------------------- the GeTransform matrix ----------------------↓")
    print([near_zero(m._mat[0][0]), near_zero(m._mat[0][1]), near_zero(m._mat[0][2]), near_zero(m._mat[0][3])])
    print([near_zero(m._mat[1][0]), near_zero(m._mat[1][1]), near_zero(m._mat[1][2]), near_zero(m._mat[1][3])])
    print([near_zero(m._mat[2][0]), near_zero(m._mat[2][1]), near_zero(m._mat[2][2]), near_zero(m._mat[2][3])])
    print("↑--------------------------------------------------------------------↑")
    print()

def get_rotz_theta(m:GeTransform)->float:
    # vectorX=GeVec3d(m._mat[0][0], m._mat[1][0], m._mat[2][0])
    return atan2(m._mat[1][0],m._mat[0][0])

def parallel_shadow(pointQ=GeVec3d(0,0,0), vectorN=GeVec3d(0,0,1), uLight=GeVec3d(0,0,1)): #平行投影矩阵
    N=unitize(vectorN)
    u=unitize(uLight)
    k=1/dot(u, N)
    M=GeTransform([[N.x*u.x, N.x*u.y, N.x*u.z, 0],
                    [N.y*u.x, N.y*u.y, N.y*u.z, 0],
                    [N.z*u.x, N.z*u.y, N.z*u.z, 0]])
    I_M=GeTransform()-k*M
    kq=dot(pointQ,vectorN)/dot(uLight,vectorN)
    return translate(kq*uLight)*I_M

def vector_shadow(n:GeVec3d)->GeTransform: #arbitrary_shadow 矢量正投影
    # two dimensional foil matrix
    matrix=GeTransform([[1-n.x**2, -n.x*n.y, -n.x*n.z, 0],
                        [-n.x*n.y, 1-n.y**2, -n.y*n.z, 0],
                        [-n.x*n.z, -n.y*n.z, 1-n.z**2, 0]])
    return matrix



