# Copyright (C), 2019-2028, Beijing GLory PKPM Tech. Co., Ltd.
# Brief: PKPM-BIMBase Python二次开发SDK与参数化组件功能。
# 纯数学计算类函数
# Author: YouQi, akingse
# Date: 2021/10

from .pyp3d_data import *
from .pyp3d_matrix import *
from math import *

def lean_section(pointY, pointX, theta):
    # todo
    return rotate(GeVec3d(0,0,1),atan2(pointY.y-pointX.y,pointY.x-pointX.x)+theta)

def lean_segment(seg, theta):
    return rotate(GeVec3d(0,0,1),atan2(seg[1].y-seg[0].y,seg[1].x-seg[0].x)+theta)

def to_vec2(*args): #Vec3强转Vec2，删除z值
    # list return list, GeVec3d return GeVec2d
    if len(args)==0:
        raise ValueError('parameter cannot be empty!')
    elif len(args)==1 and isinstance(args[0],(list,tuple)):
        args = list(args[0])
    elif len(args)==1 and isinstance(args[0],GeVec2d):
        return args[0]
    elif len(args)==1 and isinstance(args[0],GeVec3d):
        return GeVec2d(args[0].x, args[0].y)
    else:
        args = list(args)
    for i in range(len(args)):
        if isinstance(args[i],GeVec3d):
            args[i]=GeVec2d(args[i].x, args[i].y) # or using recursion
    return args

def to_vec3(*args): #Vec2强转Vec3，z值置零
    # list return list, GeVec2d return GeVec3d
    if len(args)==0:
        raise ValueError('parameter cannot be empty!')
    elif len(args)==1 and isinstance(args[0],(list,tuple)):
        args = list(args[0])
    elif len(args)==1 and isinstance(args[0],GeVec3d):
        return args[0]
    elif len(args)==1 and isinstance(args[0],GeVec2d):
        return GeVec3d(args[0].x, args[0].y, 0)
    else:
        args = list(args)
    for i in range(len(args)):
        if isinstance(args[i],GeVec2d):
            args[i]=GeVec3d(args[i].x, args[i].y, 0)
    return args

def remove_coincident_point(points:list)->list: # 三维点相邻点去重
    lonePoints=[points[0]]
    j=1
    for i in range(1,len(points)):
        if norm(points[i]-lonePoints[j-1]) > 1e-10:
            lonePoints.append(points[i])
            j=j+1
    return lonePoints

def is_points_collinear(points:list)->bool: #判断不重合的点是否共线
    points=remove_coincident_point(points)
    if len(points)<3:
        raise ValueError('please input more than 3 points!')
    vectorA=points[1]-points[0]
    normA=norm(vectorA)
    for i in range(2,len(points)):
        vectorI=points[i]-points[0]
        if abs(abs(dot(vectorA,vectorI))-normA*norm(vectorI))>1e-10:
            return False
    return True

def judge_points_plane(*args)->str: #判断所在坐标系平面
    # plane='XY' # default plane
    if len(args)==0:
        raise ValueError('parameter cannot be empty!')
    elif len(args)==1 and isinstance(args[0],(list,tuple)):
        args = list(args[0])
    else:
        args = list(args)
    if len(args)<3:
        raise ValueError('points isnot enough to judge the locate plane!')
    pointA=args[0]
    xSum=ySum=zSum=0
    for pointI in args:
        xSum+=abs((pointI-pointA).x)
        ySum+=abs((pointI-pointA).y)
        zSum+=abs((pointI-pointA).z)
    if abs(xSum)<1e-10 and abs(ySum)>1e-10 and abs(zSum)>1e-10:
        return 'YZ'
    elif abs(ySum)<1e-10 and abs(xSum)>1e-10 and abs(zSum)>1e-10:
        return 'ZX'
    elif abs(zSum)<1e-10 and abs(xSum)>1e-10 and abs(ySum)>1e-10:
        return 'XY'
    else:
        raise ValueError('cannot judge the locate plane!')

def judge_polygon_surface(points:list)->float: #通过面积判断二维多边形方向
    '''
    return the truly surface area, anti-clockwise, surface>0
    '''
    lenP=len(points)
    Surfacex2=0
    for i in range(lenP-1):
        Surfacex2+=points[i].x *points[i+1].y-points[i+1].x*points[i].y
    Surfacex2+=points[lenP-1].x *points[0].y-points[0].x *points[lenP-1].y
    if abs(Surfacex2)<=1e-10:
        return 0 #raise ValueError('please donot make all collinear points!')
    else:
        return Surfacex2/2

def points_to_trans(*args)->tuple: #三点确定一个平面的变换矩阵(包括姿态逆矩阵，及单位法向Z轴)
    '''
    more than 3 points, that enable generate only one plane
    exclude points that, collinear points, coincident points
    while ccw, axis Z is straight up, right hand rule.
    '''
    if len(args)==0:
        raise ValueError('parameter cannot be empty!')
    elif len(args)==1 and isinstance(args[0],(list,tuple)):
        args = list(args[0])
    else:
        args = list(args)
    if all(isinstance(i, GeVec2d) for i in args):
        transM=GeTransform()
        # transM=translate(args[0])
        # invM=translate(-args[0])
        return (transM,transM,True)
    points=remove_coincident_point(args)
    points=to_vec3(points)
    lenP=len(points)
    if lenP <=2:
        raise ValueError('parameter number error!')
    pointA=points[0]
    pointB=points[1]
    if is_points_collinear(points):
        raise ValueError('please donot make all collinear points!')
    for i in range(2,lenP): # discrete points qualified to compose a triangle
        if not is_points_collinear([pointA,pointB,points[i]]):
            pointC=points[i]
            break
    vectorX=unitize(pointB - pointA)
    vectorZ=unitize(cross(vectorX , pointC - pointA))
    vectorY=cross(vectorZ , vectorX)
    if get_angle_of_two_vectors(vectorX,vectorY)>0: #3点矩阵z方向
        isTop=True
    else:
        isTop=False
    for i in range(3,lenP):
        vectorD = points[i] - pointA
        if abs(dot(vectorZ,vectorD)) > 1e-10:
            raise ValueError('some points isnot in same plane!')
    # the transform matrix
    transM=set_matrix_by_column_vectors(vectorX,vectorY,vectorZ,pointA)
    invM=inverse_std(transM)
    # transM=GeTransform([[vectorX.x, vectorY.x, vectorZ.x, pointA.x],
    #                     [vectorX.y, vectorY.y, vectorZ.y, pointA.y],
    #                     [vectorX.z, vectorY.z, vectorZ.z, pointA.z]])
    # invM=GeTransform([[vectorX.x, vectorX.y, vectorX.z, -pointA.x],
    #                 [vectorY.x, vectorY.y, vectorY.z, -pointA.y],
    #                 [vectorZ.x, vectorZ.y, vectorZ.z, -pointA.z]])
    return (transM,invM,isTop)

def points_to_matrix(centerA: GeVec3d,centerB: GeVec3d)->GeTransform: # 两个点确定一个位姿变换矩阵
    '''
    two points generate a transform matrix
    '''
    vectorA=centerB-centerA
    if  not isinstance(vectorA,GeVec3d):
        raise TypeError('please input proper "GeVec3d" type!')
    elif norm(vectorA)<1e-10:
        return GeTransform() #the norm of two point cannot equal zero
    else:
        vectorZ=vectorA*(1/norm(vectorA))
        if abs(abs(vectorZ.y)-1)<1e-10:
            vectorX=GeVec3d(1,0,0)
        elif vectorZ.x*vectorZ.z>0:
            vectorX=GeVec3d(sqrt(vectorZ.z**2/(vectorZ.x**2+vectorZ.z**2)),0,-sqrt(vectorZ.x**2/(vectorZ.x**2+vectorZ.z**2)))
        elif vectorZ.x*vectorZ.z<=0:
            vectorX=GeVec3d(sqrt(vectorZ.z**2/(vectorZ.x**2+vectorZ.z**2)),0,sqrt(vectorZ.x**2/(vectorZ.x**2+vectorZ.z**2)))
        vectorY = cross(vectorZ , vectorX)
        transM=set_matrix_by_column_vectors(vectorX,vectorY,vectorZ,centerA)
        # transM=GeTransform([[vectorX.x, vectorY.x, vectorZ.x, centerA.x],
        #                     [vectorX.y, vectorY.y, vectorZ.y, centerA.y],
        #                     [vectorX.z, vectorY.z, vectorZ.z, centerA.z]])
        return transM

def vector_to_matrix(vectorA: GeVec3d)->GeTransform: #一个矢量确定一个姿态变换矩阵
    '''
    one vector generate a transform matrix
    '''
    if  not isinstance(vectorA,GeVec3d):
        raise TypeError('please input proper "GeVec3d" type!')
    elif norm(vectorA)<1e-10:
        return GeTransform([[1, 0, 0, 0],[0, 1, 0, 0],[0, 0, 1, 0]])
    else:
        vectorZ=vectorA*(1/norm(vectorA))
        if abs(abs(vectorZ.y)-1)<1e-10:
            vectorX=GeVec3d(1,0,0)
        elif vectorZ.x*vectorZ.z>0:
            vectorX=GeVec3d(sqrt(vectorZ.z**2/(vectorZ.x**2+vectorZ.z**2)),0,-sqrt(vectorZ.x**2/(vectorZ.x**2+vectorZ.z**2)))
        elif vectorZ.x*vectorZ.z<=0:
            vectorX=GeVec3d(sqrt(vectorZ.z**2/(vectorZ.x**2+vectorZ.z**2)),0,sqrt(vectorZ.x**2/(vectorZ.x**2+vectorZ.z**2)))
        vectorY = cross(vectorZ , vectorX)
        transM=set_matrix_by_column_vectors(vectorX,vectorY,vectorZ)
        # transM=GeTransform([[vectorX.x, vectorY.x, vectorZ.x, 0],
        #                     [vectorX.y, vectorY.y, vectorZ.y, 0],
        #                     [vectorX.z, vectorY.z, vectorZ.z, 0]])
        return transM

def points_to_segments(points:list, close=False)->list: # 将points转换为segment的list
    points=remove_coincident_point(points)
    lenP=len(points)
    segmentList=[] 
    for i in range(lenP-1):
        segmentList.append([points[i],points[i+1]])
    if close:
        if norm(points[lenP-1]-points[0])>1e-10:
            segmentList.append([points[lenP-1],points[0]])
        return segmentList
    else:
        return segmentList

def get_distance_of_point_line(point:GeVec3d, line:list): #计算点到直线的距离（支持三维点）
    p0=to_vec3(point)
    p1=to_vec3(line[0])
    p2=to_vec3(line[1])
    if norm(p0-p1)<1e-10 or norm(p0-p2)<1e-10: #端点重合
        return 0
    if is_same_direction(p0-p1, p0-p2): #共线
        return 0
    invM=points_to_trans(p0,p1,p2)[1] #三点一面
    # p1=to_vec2(invM*(p1-p0))
    # p2=to_vec2(invM*(p2-p0))
    p1=to_vec2(invM*p1)
    p2=to_vec2(invM*p2)
    p0=GeVec2d(0,0)
    x1=p1.x
    y1=p1.y
    x2=p2.x
    y2=p2.y
    if abs(x1-x2)<1e-10: #直线竖直
        return abs(x1)
    else:
        d=abs(-y2*(x1-x2)+x2*(y1-y2))/sqrt((y1-y2)**2+(x1-x2)**2)
        return d

def is_point_in_segment(point:GeVec3d, line:list): #判断点与线段的关系
    # 点在线段内 = 1
    # 点在线段延长线上 = -1
    # 点不在线段上 = 0
    # 点与线段端点重合 = 2
    if norm(point-line[0])<1e-10 or norm(point-line[1])<1e-10 :
        return 2
    if abs(get_distance_of_point_line(point,line))<1e-10: #点在直线上
        if is_same_direction(point-line[0],point-line[1])==-1:
            return 1
        else:
            return -1
    else:
        return 0

def is_two_segments_intersect(line1:list,line2:list)->int: #判断（二维）线段关系
    '''
    if two lines intersect, return 1, two lines separate, return 0;
    else if two lines only parallel, return 2, colineation return 3;
    else if two lines joined like Y, return -1, joined like V, return -2;
    '''
    # 平行=2，重合=3
    # V形相接=-1，Y形相接=-2
    # 相交=1，相离=0
    if (not isinstance(line1, list)) and (not isinstance(line2, list)):
        raise TypeError('parameters error!')
    if len(line1)!=2 or len(line2)!=2:
        raise TypeError('parameters number error!')
    line1=to_vec2(line1)
    line2=to_vec2(line2)
    vec1=line1[1]-line1[0]
    vec2=line2[1]-line2[0]
    #parallel
    if is_same_direction(vec1,vec2): 
        if abs(get_distance_of_point_line(line1[0],line2))<1e-10:
            return 3 #colineation
        else:
            return 2 #only parallel
    # connect 4 cases
    # case1
    coef=is_point_in_segment(line1[0],line2)
    if coef==1:
        return -2 # Y
    elif coef==2:
        return -1 # V
    # case2
    coef=is_point_in_segment(line1[1],line2)
    if coef==1:
        return -2 # Y
    elif coef==2:
        return -1 # V
    # case3
    coef=is_point_in_segment(line2[0],line1)
    if coef==1:
        return -2 # Y
    elif coef==2:
        return -1 # V
    # case4
    coef=is_point_in_segment(line2[1],line1)
    if coef==1:
        return -2 # Y
    elif coef==2:
        return -1 # V
    # line1
    x1=line1[0].x  #A
    y1=line1[0].y
    x2=line1[1].x  #B
    y2=line1[1].y
    # line2
    x3=line2[0].x  #C
    y3=line2[0].y
    x4=line2[1].x  #D
    y4=line2[1].y
    # CD is beside line1
    A1=-(y2-y1)
    B1=(x2-x1)
    C1=x1*y2-x2*y1
    sideC=A1*x3+B1*y3+C1
    sideD=A1*x4+B1*y4+C1
    if sideC*sideD < 0:
        twoSides1=True
    else:
        twoSides1=False
    # AB is beside line2
    A2=-(y4-y3)
    B2=(x4-x3)
    C2=x3*y4-x4*y3
    sideA=A2*x1+B2*y1+C2
    sideB=A2*x2+B2*y2+C2
    if sideA*sideB < 0:
        twoSides2=True
    else:
        twoSides1=False
    # two lines intersect, return True
    if twoSides1 and twoSides2:
        return 1
    else:
        return 0

def polygon_to_ccw(points:list)->list: #规范直线多边形,无自相交,无回头线,逆时针
    # ccw=counter clockwise
    points=to_vec2(points) #强转二维Vec2
    for i in points: # not point, return itself
        if not isinstance(i,GeVec2d):
            return points
    points=remove_coincident_point(points)
    if len(points) < 3:
        raise ValueError('please input 3 points at least, to compose one plane！')
    segmentList=points_to_segments(points,True)
    lenL=len(segmentList)
    # 循环遍历每两条线段
    for i in range(2,lenL-1):  
        coef=is_two_segments_intersect(segmentList[0],segmentList[i])
        if coef==1 or coef==-1 or coef==-2:
            raise ValueError('some lines self-intersect in polygon!')
    for i in range(1,lenL):
        for j in range(i+2,lenL):
            coef=is_two_segments_intersect(segmentList[i],segmentList[j])
            if coef==1 or coef==-1 or coef==-2:
                raise ValueError('some lines self-intersect in polygon!')
    if judge_polygon_surface(points)>0:
        return points
    else:
        points.reverse()
        return points

def points_to_offset(points:list)->list: #当RuledSweep中的两点重合，自动将第二个点（三维点）错开一个微小偏移
    '''
    when two coincident in RuledSweep, auto offset the second point a tiny distance
    '''
    k=1e-10
    if norm(points[1]-points[0])==0:
        pointd=points[0]-points[-1]
        points[1]=GeVec3d(points[1].x+k*pointd.x,points[1].y+k*pointd.y,points[1].z+k*pointd.z)
    for i in range(1,len(points)-1):
        if norm(points[i+1]-points[i])==0:
            pointd=points[i]-points[i-1]
            points[i+1]=GeVec3d(points[i+1].x+k*pointd.x,points[i+1].y+k*pointd.y,points[i+1].z+k*pointd.z)
    return points

def rotation_to(v)->GeTransform:#旋转至与V同向
    '''
    rotate to the same direction as V
    '''
    transformation = GeTransform()  #transformation assign identity matrix
    v12_norm = norm(v)
    if v12_norm != 0.0: 
        angle_z = acos(v.z/v12_norm)
        # if angle_z == 0.0:
        if abs(angle_z) < 1e-10:
            transformation *= rotate(GeVec3d(0, 1, 0),  -pi/2)
        # elif angle_z == pi:
        elif abs(abs(angle_z)-pi) < 1e-10:
            transformation *= rotate(GeVec3d(0, 1, 0),  pi/2)
        else:
            r_xy = sqrt(v.x**2 + v.y**2)
            angle_xy = acos(v.x/r_xy)
            if v.y < 0.0:
                angle_xy = -angle_xy
            transformation *= rotate(GeVec3d(0, 0, 1),  angle_xy) * rotate(GeVec3d(0, 1, 0),  angle_z-pi/2)      
    return transformation

# -------------------------------------------------------------------------------
# B spline curve algorithm
def spline_uniform_node_vector(n,k): # 均匀B样条曲线(节点函数)
    # nodeVector=[0]*(n+k+2)
    # for i in range(n+k+2):
    #     nodeVector[i]=i/(n+k+1)
    # return nodeVector
    return linspace(0,1,n+k+2) 

def spline_quasi_node_vector(n,k): # 准均匀B样条曲线(节点函数)
    nodeVector=[0]*(n+k+2)
    piecewise=n-k+1
    if n+1==k:
        raise TypeError('len(point_control) cannot equal k!')
    if piecewise==1:
        for i in range(n+1,n+k+2):
            nodeVector[i]=1
    else:
        flag=1
        while flag!=piecewise:
            nodeVector[k+flag]=nodeVector[k-1+flag]+1/piecewise
            flag+=1
        for i in range(n+1,n+k+2): #range取值[a,b)
            nodeVector[i]=1
    return nodeVector

def spline_piecewise_node_vector(n,k): # 分段B样条曲线(节点函数)
    '''限定条件，控制点-1等于次数的倍数，n/k=int'''
    if n%k != 0:
        raise ValueError('piecewise parameter error!')
    nodeVector=[0]*(n+k+2)
    for i in range(n+1,n+k+2):
        nodeVector[i]=1
    piecewise=n/k
    flag=0
    if piecewise>1:
        for i in range(1,int(piecewise)):
            for j in range(k):
                nodeVector[k+1+flag*k+j]=i/piecewise
            flag+=1
    return nodeVector

def spline_base_function(i, k, u, nodeVector): #B样条曲线标准迭代函数
    if k==0:
        if u>=nodeVector[i] and u<nodeVector[i+1]:
            niku=1
        else:
            niku=0
    else:# python and matlab, index is different
        if abs(nodeVector[i+k]-nodeVector[i])<1e-10:
            coef1=0
        else:
            coef1=(u-nodeVector[i])/(nodeVector[i+k]-nodeVector[i])
        if abs(nodeVector[i+k+1]-nodeVector[i+1])<1e-10:
            coef2=0
        else:
            coef2=(nodeVector[i+k+1]-u)/(nodeVector[i+k+1]-nodeVector[i+1])
        niku=coef1*spline_base_function(i,k-1,u,nodeVector) + coef2*spline_base_function(i+1,k-1,u,nodeVector)
    return niku

def spline_de_casteljau_function(n,pList,u): #多项式递归算法
    '''
    n: number of control
    pointSet: list of list of int [[x0,y0],[x1,y1],]
    '''
    # P=pList #浅拷，将修改入参
    P=copy.deepcopy(pList) #深拷
    while(n):
        for i in range(n-1):
            P[i].x=(1-u)*P[i].x+u*P[i+1].x
            P[i].y=(1-u)*P[i].y+u*P[i+1].y
        n=n-1
    return P[0]

# -------------------------------------------------------------------------------
# For RealSweep

def get_angle_of_two_vectors(paraA, paraB)->float: # 求两个矢量之间的夹角，vectorA->vectorB右手定则，夹角为正
    # 入参类型，支持segment和Gevec3d
    if isinstance(paraA,list) and isinstance(paraB,list) and len(paraA)==2 and len(paraB)==2:
        if (isinstance(paraA[0],GeVec3d) and isinstance(paraA[1],GeVec3d)) or\
            (isinstance(paraB[0],GeVec2d) and isinstance(paraB[1],GeVec2d)):
            vectorA=paraA[1]-paraA[0]
            vectorB=paraB[1]-paraB[0]
        else:
            raise ValueError('parameters error!')
    elif (isinstance(paraA,GeVec3d) and isinstance(paraB,GeVec3d)) or \
        (isinstance(paraA,GeVec2d) and isinstance(paraB,GeVec2d)) :
        vectorA=paraA
        vectorB=paraB
    else:
        raise ValueError('parameters error!')
    if norm(vectorA)*norm(vectorB) < 1e-10: # 两向量均不为零
        raise ValueError('the norm of two vectors cannot be zero!')
    # 夹角计算（0->pi / -pi->0）
    theta=acos(dot(vectorA,vectorB)/(norm(vectorA)*norm(vectorB))) #acos值域0->pi
    vectorZ=cross(vectorA,vectorB)
    if vectorZ.z<0:
        theta=-theta
    return theta

def get_nearest_point_on_line(line:list,point:GeVec3d)->GeVec3d:
    # 三维空间内，直线上一点，到指定点的距离最近
    if abs(get_distance_of_point_line(point,line))<1e-10: #若点在直线上
        return point
    ptt=points_to_trans(point,line[0],line[1]) # 三维转二维
    transM=ptt[0]
    invM=ptt[1]
    point1=invM*(line[0])
    point2=invM*(line[1])
    x0=0 #point.x
    y0=0 #point.y
    x1=point1.x
    y1=point1.y
    x2=point2.x
    y2=point2.y
    t=((x0-x1)*(x2-x1)+(y0-y1)*(y2-y1)) / ((y2-y1)**2+(x2-x1)**2)
    x=x1+(x2-x1)*t
    y=y1+(y2-y1)*t
    return transM*GeVec3d(x,y,0)




