# Copyright (C), 2019-2028, Beijing GLory PKPM Tech. Co., Ltd.
# Brief: PKPM-BIMBase Python二次开发SDK与参数化组件功能。
# Author: YouQi, akingse
# Date: 2021/10

from .pyp3d_data import *
from .pyp3d_matrix import *
from .pyp3d_calculation import *
from .pyp3d_component import *
from math import *

def create_geometry1(noumenon:Noumenon):#在全局坐标系的原点创建一个几何体
    return UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT,  PARACMPT_CREATE_GEOMETRY)(noumenon)

# -------------------------------------------------------------------------------

def points_to_section(*args)->Section: #多点(>=3)生成一个二维Section面，已变换到3维
    '''
    many points (>=3) generate a section in 2-dimension, been translated to 3-dimension already
    '''
    if len(args)==0:
        raise ValueError('parameter cannot be empty!')
    elif len(args)==1 and isinstance(args[0],(list,tuple)):
        points = list(args[0])
    else:
        points = list(args)
    if all(isinstance(i,GeVec2d) for i in points):
        return Section(points)
    #when to_section() call this fuction, args only inclued GeVec3d points
    if not all(isinstance(i,GeVec3d) for i in points):
        raise ValueError('please input points!')
    ptt=points_to_trans(points)
    transM=ptt[0]
    invM=ptt[1]
    section = transM*Section()
    for i in range(len(points)):    
        # point=invM*(points[i]-points[0])
        point=invM*points[i]
        point=to_vec2(point)
        section.append(point)
    return section

def arc_of_three_points(*args)->Arc: #3点画圆
    # args:list, isFull=False
    if len(args)==1 and isinstance(args[0],(list,tuple)):
        args = list(args[0])
        isFull=False
    elif len(args)==2 and isinstance(args[0],(list,tuple)) and isinstance(args[0],bool):
        args = list(args[0])
        isFull=args[1]
    elif len(args)==3 and is_all_vec(args):
        args = list(args[0])
        isFull=False
    elif len(args)==4 and is_all_vec([args[0],args[1],args[2]]):
        args = [args[0],args[1],args[2]]
        isFull=args[3]
    else:
        raise ValueError('parameters error!')
    # generate arc
    if norm(args[2]-args[0])<1e-10 and norm(args[1]-args[0])>1e-10:# 3点直径画圆，默认XoY平面
        R=norm(args[1]-args[0])/2
        mat=translate(0.5*(args[0]+args[1]))*scale(R)
        return mat*Arc()
    else:
        if is_all_vec2(args):
            args=to_vec3(args)
        ptt=points_to_trans(args)
        transM=ptt[0]
        invM=ptt[1]
        point1=invM*args[1]
        point2=invM*args[2]
        x1=0 #points[0].x
        y1=0 #points[0].y
        x2=point1.x
        y2=point1.y
        x3=point2.x
        y3=point2.y
        yc=((x3-x2)*(x3**2+y3**2-x1**2-y1**2)-(x3-x1)*(x3**2+y3**2-x2**2-y2**2)) / (2*(x3-x2)*(y3-y1)-2*(x3-x1)*(y3-y2))
        xc=((y3-y2)*(x3**2+y3**2-x1**2-y1**2)-(y3-y1)*(x3**2+y3**2-x2**2-y2**2)) / (2*(y3-y2)*(x3-x1)-2*(y3-y1)*(x3-x2))
        R=sqrt((xc-x1)**2+(yc-y1)**2)
        mat=transM*translate(xc,yc)*scale(R)*rotate(atanp(y1-yc,x1-xc))
        if isFull:  #是否为满圆
            scope=2*pi
        else:
            scope=posi(atanp(y3-yc,x3-xc)-atanp(y1-yc,x1-xc))
        return mat*Arc(scope)

def arc_of_center_points(centerP:GeVec3d, startP:GeVec3d, endP:GeVec3d, isForw=True)->Arc: # 圆心-起点-终点
    # if isForw, startP->endP, else endP->startP
    R1=norm(startP-centerP)
    R2=norm(endP-centerP)
    if abs(R1-R2)>1e-10 or abs(R1)<1e-10: 
        raise TypeError('itis not a circle arc!')
    if norm(startP-endP)<1e-10:
        return translate(centerP)*scale(R1)*Arc() #返回逆时针整圆
    if is_same_direction(centerP-startP,centerP-endP)==-1: #3点共线，则默认在XoY面
        if isinstance(centerP,GeVec2d) and isinstance(startP,GeVec2d) and isinstance(endP,GeVec2d):
            vecStart=startP-centerP
            mat=translate(centerP)*scale(R1)*rotz(atan2(vecStart.y,vecStart.x))
            return mat*Arc((2*int(isForw)-1)*pi)
        else:
            raise TypeError('cant judge arc locate plane!')   
    ptt=points_to_trans(centerP,startP,endP) #三维转二维
    transM=ptt[0]
    invM=ptt[1]
    isTop=ptt[2]
    # point0=GeVec2d(0,0)
    point1=to_vec2(invM*startP)
    point2=to_vec2(invM*endP)
    scope=get_angle_of_two_vectors(point1,point2)
    if isTop: #正视图 viewport
        if isForw:
            if scope<0:
                scope=2*pi+scope
        else:
            if scope>=0:
                scope=scope-2*pi
    else: #俯视图 viewport
        if isForw:
            if scope>=0:
                scope=scope-2*pi
        else:
            if scope<0:
                scope=2*pi+scope
    mat=scale(R1)*rotz(atan2(point1.y,point1.x))
    return transM*mat*Arc(scope)

def arc_of_radius_points(pStart:GeVec2d, pEnd:GeVec2d, R:float): # 起点-终点-半径
    # 仅限二维平面内
    if not (isinstance(pStart,GeVec2d) and isinstance(pEnd,GeVec2d)):
        raise TypeError('parameters must in XoY plane!')
    p1=pStart
    p2=pEnd
    d=norm(p2-p1)
    if abs(2*R)<d: #R过小，无法形成圆
        raise TypeError('R too small !')
    thetaRela=atan2(p2.y-p1.y, p2.x-p1.x)
    thetaScope=asin(d/2/R)
    transM=translate(p1)*rotz(thetaRela)
    pCenter=transM*GeVec3d(d/2,R*cos(thetaScope),0)
    theta=atan2(p1.y-pCenter.y,p1.x-pCenter.x)
    # if R<0: #asin()函数自动处理正负角
    #     thetaScope=-thetaScope
    return translate(pCenter)*scale(abs(R))*rotz(theta)*Arc(2*thetaScope)

def arc_of_tangent_radius(posVec:list,R:float,scope:float)->Arc: # 位矢-半径-角度
    # 当前XoY平面内，scope>0 左侧逆时针
    pos=posVec[0] #位置点
    vec=posVec[1] #切线方向
    if not (isinstance(pos,GeVec2d) and isinstance(vec,GeVec2d)):
        raise TypeError('posVec must in XoY plane!')
    theta=atan2(vec.y, vec.x)
    # xc=pos.x-R*sin(theta) 
    # yc=pos.y+R*cos(theta)
    pCenter=GeVec3d(pos.x-R*sin(theta),pos.y+R*cos(theta),0)#R>0: #圆心在矢量左侧
    # if R<0: #规定，scope>0为逆时针
    #     scope=-scope
    return translate(pCenter)*scale(abs(R))*rotz(atanp(pos.y-pCenter.y,pos.x-pCenter.x))*Arc(scope)

def spline_curve(pList:list, k:int, num:int, typeB=0)->list: #样条曲线函数
    n=len(pList)-1
    points=[]
    P=[[],[]] #矩阵形式的控制点
    for i in range(n+1):
        P[0].append(pList[i].x)
        P[1].append(pList[i].y)
    nik=[0]*(n+1)
    
    if typeB==0:
        n=n+1
        for i in range(num):
            u=i/num
            point=spline_de_casteljau_function(n, pList, u) # deCasteljau递推算法
            points.append(GeVec2d(point.x,point.y))
    elif typeB==1:
        node=spline_uniform_node_vector(n,k) #均匀B样条
        for u in linspace(k/(n+k+1),(n+1)/(n+k+1),num):
            for i in range(n+1):
                nik[i]=spline_base_function(i, k, u, node)
            x,y=0,0
            for j in range(n+1):
                x+=P[0][j]*nik[j]
                y+=P[1][j]*nik[j]
            points.append(GeVec2d(x,y))
    elif typeB==2:
        if not n+1-k>=0:
            raise TypeError('len(point_control) cannot equal k!')
        node=spline_quasi_node_vector(n,k) #准均匀B样条
        for u in linspace(0,1-1/num,num):
            for i in range(n+1):
                nik[i]=spline_base_function(i, k, u, node)
            x,y=0,0
            for j in range(n+1):
                x+=P[0][j]*nik[j]
                y+=P[1][j]*nik[j]
            points.append(GeVec2d(x,y))
    elif typeB==3:
        if n%k!=0:
            raise ValueError('piecewise parameter error!')
        node=spline_piecewise_node_vector(n,k) #分段B样条
        for u in linspace(0,1-1/num,num):
            for i in range(n+1):
                nik[i]=spline_base_function(i, k, u, node)
            x,y=0,0
            for j in range(n+1):
                x+=P[0][j]*nik[j]
                y+=P[1][j]*nik[j]
            points.append(GeVec2d(x,y))
    return Line(points)

def get_plane_of_contourline(OuterContourparts)->str: #判断所在坐标系平面
    # plane='XY' # default plane
    for part in OuterContourparts:
        if isinstance(part,Arc):
            vecotrA=GeVec3d(part.transformation._mat[0][0],part.transformation._mat[1][0],part.transformation._mat[2][0])
            vecotrB=GeVec3d(part.transformation._mat[0][1],part.transformation._mat[1][1],part.transformation._mat[2][1])
            vecotrC=cross(vecotrA,vecotrB)
            if abs(vecotrC.x)>1e-8 and abs(vecotrC.z)+abs(vecotrC.y)<1e-8:
                return 'YZ'
            elif abs(vecotrC.y)>1e-8 and abs(vecotrC.z)+abs(vecotrC.x)<1e-8:
                return 'ZX'
            elif abs(vecotrC.z)>1e-8 and abs(vecotrC.y)+abs(vecotrC.x)<1e-8:
                return 'XY'
            else:
                raise ValueError('cannot judge the locate plane!')
    points=[] #take out all point in Line()
    for part in OuterContourparts:
        if isinstance(part,Line):
            for i in range(len(part.parts)):
                points.append(part.parts[i])
    pointA=points[0]
    sumX=sumY=sumZ=0
    for pointi in points:
        sumX+=abs((pointi-pointA).x)
        sumY+=abs((pointi-pointA).y)
        sumZ+=abs((pointi-pointA).z)
    if abs(sumX)<1e-10 and abs(sumY)>1e-10 and abs(sumZ)>1e-10:
        return 'YZ'
    elif abs(sumY)<1e-10 and abs(sumX)>1e-10 and abs(sumZ)>1e-10:
        return 'ZX'
    elif abs(sumZ)<1e-10 and abs(sumX)>1e-10 and abs(sumY)>1e-10:
        return 'XY'
    else:
        raise ValueError('cannot judge the locate plane!')

def get_line_from_nesting_line(line:Line)->list: #递归解析嵌套line，用于判断闭合
    #using recursion extract all args in line
    lines=[]
    for i in line.parts:
        if not isinstance(i, Line):
            lines.append(i)
        else:
            lineR=extract_line(i)
            for j in lineR:
                lines.append(j)
    return lines

def is_line_close(line:Line)->bool: #判断Line是否闭合
    if not isinstance(line,Line):
        raise ValueError('improper parameters!')
    lenP=len(line.parts)
    if lenP==0:
        raise ValueError('empty parameter!')
    line=Line(extract_line(line)) # all component basic class surppot list/tuple args
    if isinstance(line.parts[0],(GeVec2d,GeVec3d)):
        pointStart=line.parts[0]
    elif isinstance(line.parts[0],Arc):
        pointStart=line.parts[0].pointStart
        if lenP==1 and abs(line.parts[0].scope-2*pi)<1e-10:
            return True
        if lenP>1 and abs(line.parts[0].scope-2*pi)<1e-10:
            raise ValueError('improper parameters!')
    if isinstance(line.parts[-1],(GeVec2d,GeVec3d)):
        pointEnd=line.parts[-1]
    elif isinstance(line.parts[-1],Arc):
        pointEnd=line.parts[-1].pointEnd
    if norm(pointEnd-pointStart)<1e-10:
        return True
    else:
        return False

def is_two_dimensional(*args)->bool: #判断Line Arc在XoY二维面或三维空间
    '''
    dimension judge, 2-dimension==True, 3-dimension==False
    it means, if locate in XoY plane return True
    else locate return False
    '''
    if len(args)==0:
        raise ValueError('parameter cannot be empty!')
    elif len(args)==1 and isinstance(args[0],(list,tuple)):
        args = list(args[0])
    else:
        args = list(args)
    dimension = True
    for value in args:
        if isinstance(value, GeVec2d):
            continue
        elif isinstance(value, Arc): 
            axisZi=value.vectorNormal
            # GeVec3d(value.transformation._mat[0][2],value.transformation._mat[1][2],value.transformation._mat[2][2])
            # if abs(value.transformation._mat[2][3])>1e-10 or abs(abs(dot(unitize(axisZi),GeVec3d(0,0,1)))-1)>1e-10:
            if abs(value.transformation._mat[2][3])>1e-10 or is_same_direction(axisZi,GeVec3d(0,0,1))==0:
                dimension = False
                break
        elif isinstance(value, GeVec3d):
            if abs(value.z)>1e-10:
                dimension = False
                break
        elif isinstance(value, Line):
            dimension = is_two_dimensional(value.parts) # recursion
        else:
            raise TypeError('Line parameter error!')
    return dimension

def is_point_locate_plane(point:GeVec3d, section:Section)->bool: #判断点是否在平面上
    point=to_vec3(point)
    pointA=section.transformation*to_vec3(section.parts[0])
    vectorZ=get_matrix_axisz(section.transformation)
    vectorD = point - pointA
    if abs(dot(vectorZ,vectorD)) < 1e-10:
        return True #point is in same plane
    else:
        return False

def is_point_in_polygon(point:GeVec3d, section:Section)->bool: #判断点是否在多边形内
    if not is_point_locate_plane(point, section):
        return False
    point=inverse(section.transformation)*point #转至XoY二维平面处理
    rangeP=get_range_of_section(section,True)
    if point.x<rangeP[0] or point.x>rangeP[1] or point.y<rangeP[2] or point.y>rangeP[3]: #超出边界
        return False
    # ray-crossing 引射线法: 从point点出发（向右）引一条射线，射线与多边形所有边的交点数目，若为奇数则在内部
    polygon=get_discrete_points_from_line(Line(section.parts),100)# 二维section，离散化为多边形
    segments=points_to_segments(polygon, close=True)
    isIn=False
    x=point.x
    y=point.y
    for p in segments:
        if is_point_in_segment(point,p)==1 or is_point_in_segment(point,p)==2:
            return True
        if (p[0].y<=y and y<p[1].y) or (p[1].y<=y and y<p[0].y) and \
            x-p[0].x<(p[1].x-p[0].x)*(y-p[0].y)/(p[1].y-p[0].y):
            isIn=bool(1-isIn) #布尔取反
    return isIn


# 别名
judge_locate_plane=get_plane_of_contourline
extract_line=get_line_from_nesting_line
get_segments_from_points=points_to_segments

# -------------------------------------------------------------------------------
# 

def get_trajectory_from_line(line:Line, close=False)->list: #从Line获取分段轨迹线（返回三维参数）
    if not isinstance(line,Line):
        TypeError('parameter must be Line')
    line=copy.deepcopy(line)
    parts=line.parts
    for i in range(len(parts)):
        if isinstance(parts[i],GeVec2d):
            parts[i]=to_vec3(parts[i])
        parts[i]=line.transformation*parts[i]
    trajectory = []
    for i in range(len(parts)-1):
        if isinstance(parts[i],(GeVec2d,GeVec3d)) and isinstance(parts[i+1],(GeVec2d,GeVec3d)):
            if norm(to_vec3(parts[i])-to_vec3(parts[i+1]))>1e-10: #去重
                trajectory.append([to_vec3(parts[i]),to_vec3(parts[i+1])])
        elif (isinstance(parts[i],(GeVec2d,GeVec3d))) and isinstance(parts[i+1],Arc):
            # startP=GeTransform(parts[i+1].transformation._mat)*GeVec3d(1, 0, 0)
            startP=parts[i+1].pointStart
            if norm(to_vec3(parts[i])-startP)>1e-10:
                trajectory.append([to_vec3(parts[i]),startP])
        elif isinstance(parts[i],Arc) and (isinstance(parts[i+1],(GeVec2d,GeVec3d))):
            trajectory.append(parts[i])
            # endP=GeTransform(parts[i].transformation._mat)*GeVec3d(cos(parts[i].scope), sin(parts[i].scope), 0)
            endP=parts[i+1].pointEnd
            if norm(endP-to_vec3(parts[i+1]))>1e-10:
                trajectory.append([endP,to_vec3(parts[i+1])])
        elif isinstance(parts[i],Arc) and isinstance(parts[i+1],Arc):
            trajectory.append(parts[i])
    if isinstance(parts[len(parts)-1],Arc):
        trajectory.append(parts[len(parts)-1])
    #判断闭合 close
    if close:
        I=len(parts)-1
        if isinstance(parts[I],(GeVec2d,GeVec3d)) and isinstance(parts[0],(GeVec2d,GeVec3d)):
            if norm(to_vec3(parts[I])-to_vec3(parts[0]))>1e-10:
                trajectory.append([to_vec3(parts[I]),to_vec3(parts[0])])
        elif (isinstance(parts[I],(GeVec2d,GeVec3d))) and isinstance(parts[0],Arc):
            # startP=GeTransform(parts[0].transformation._mat)*GeVec3d(1, 0, 0)
            startP=parts[0].pointStart
            if norm(to_vec3(parts[I])-startP)>1e-10:
                trajectory.append([to_vec3(parts[I]),startP])
        elif isinstance(parts[I],Arc) and (isinstance(parts[0],(GeVec2d,GeVec3d))):
            # endP=GeTransform(parts[I].transformation._mat)*GeVec3d(cos(parts[I].scope), sin(parts[I].scope), 0)
            endP=parts[I].pointEnd
            if norm(endP-to_vec3(parts[0]))>1e-10:
                trajectory.append([endP,to_vec3(parts[0])])
        elif isinstance(parts[I],Arc) and isinstance(parts[0],Arc):
            # startP=GeTransform(parts[I].transformation._mat)*GeVec3d(cos(parts[I].scope), sin(parts[I].scope), 0)
            startP=parts[I].pointEnd
            # endP=GeTransform(parts[0].transformation._mat)*GeVec3d(1, 0, 0)
            endP=parts[0].pointStart
            if norm(startP-endP)>1e-10:
                trajectory.append([startP,endP])
    return trajectory

def get_perimeter_of_arc(circle:Arc)->float: #椭圆周长(近似值)
    a=get_scale_para(circle.transformation)[0] #x方向长轴
    b=get_scale_para(circle.transformation)[1] #y方向短轴
    if abs(a-b)<1e-10: #圆
        return circle.scope*a
    else:
        lamda=(a-b)/(a+b)
        perimeter=pi*(a+b)*(1+(3*lamda**2)/(10+sqrt(4-3*lamda**2)))# Ramanujan近似公式
        return circle.scope/(2*pi)*perimeter

def get_points_from_line(line:Line, num=None, onlyCurve=True, autoStep=True, close=False)->list: # 离散化line为GeVec3d列表
    line=copy.deepcopy(line) #deepcopy, to avoid refresh imput value
    if not isinstance(line, Line):
        raise TypeError('function parameter error!')
    if num is None:#isinstance(num, None):
        autoStep=True   # return line.parts
    else:
        autoStep=False
    # if all(isinstance(i, (GeVec2d,GeVec3d)) for i in line.parts):
    #     return line.parts #纯多段线不支持离散，请使用 linspace()
    trajectory=get_trajectory_from_line(line,close)
    length=0 
    discretePoints=[]
    if onlyCurve:
        for i in trajectory:
            if isinstance(i, Arc):
                length=length+get_perimeter_of_arc(i) #弧线长度（累加）
        # 离散，以直代曲
        if autoStep:
            stepL=0.1 #自动步长，suitable screen resolution
        else:
            stepL=length/num #步长=距离/离散数
        mat=line.transformation
        for j in line.parts:
            if isinstance(j, (GeVec2d,GeVec3d)):
                discretePoints.append(mat*to_vec3(j))
            elif isinstance(j, Arc):
                lengthJ=get_perimeter_of_arc(j)
                numJ=ceil(lengthJ/stepL) #int(lengthJ/stepL) #弧度步长-个数(向上取整)
                for k in range(numJ+1):
                    pointJ=GeVec3d(cos(k/numJ*j.scope),sin(k/numJ*j.scope),0)
                    discretePoints.append(mat*j.transformation*pointJ) #复合矩阵
        return discretePoints
    else: # 直线也离散
        for i in trajectory:
            if isinstance(i, Arc):
                length=length+get_perimeter_of_arc(i) #弧线长度（累加）
            elif isinstance(i, list):
                length=length+norm(i[1]-i[0]) #线段长度（累加）
        # 离散，以直代曲
        if autoStep:
            stepL=0.1 #自动步长，suitable screen resolution
        else:
            stepL=length/num #步长=距离/离散数
        mat=GeTransform() #trajectory已作用line.transformation
        for j in trajectory:
            if isinstance(j, Arc):
                lengthJ=get_perimeter_of_arc(j)
                numJ=ceil(lengthJ/stepL)
                for k in range(numJ+1):
                    pointJ=GeVec3d(cos(k/numJ*j.scope),sin(k/numJ*j.scope),0)
                    discretePoints.append(mat*j.transformation*pointJ) #复合矩阵
            elif isinstance(j, list):
                lengthJ=norm(j[1]-j[0])
                numJ=ceil(lengthJ/stepL) #弧度步长-个数
                pointL=linspace(j[0],j[1],numJ)
                for k in range(numJ):
                    discretePoints.append(mat*to_vec3(pointL[k]))
        return discretePoints
get_discrete_points_from_line=get_points_from_line

def get_points_from_section(sec:Section, num=None, onlyCurve=True, close=False): #获取section中的三维点（已离散）list列表
    line=sec.transformation*Line(sec.parts)
    points=get_points_from_line(line,num,onlyCurve,False,close)
    return points

def get_range_of_section(section:Section, onlyParts=False)->tuple: #离散法，获取截面值域(视图框)
    '''
    # onlyParts，仅section中的二维参数，return ( Xleft, Xright, Ydown, Yup )
    # 三维平面中，离散后的points可能会限定在一个立方体空间中
    '''
    if onlyParts:
        points=get_discrete_points_from_line(Line(section.parts))
        points=to_vec3(points)
    else:
        points=get_points_from_section(section,100)
    xMin=xMax=points[0].x
    yMin=yMax=points[0].y
    zMin=zMax=points[0].z
    for i in points:
        if i.x>xMax:
            xMax=i.x
        if i.x<xMin:
            xMin=i.x
        if i.y>yMax:
            yMax=i.y
        if i.y<yMin:
            yMin=i.y
        if i.z>zMax:
            zMax=i.z
        if i.z<zMin:
            zMin=i.z
    if onlyParts:
        return (xMin,xMax,yMin,yMax)
    else:
        return (xMin,xMax,yMin,yMax,zMin,zMax) 

def get_angle_of_line_arc(line:list, arc:Arc, Forward=True)->float: #获取直线和圆弧的夹角（正负：右手定则)
    vectorL=unitize(line[1]-line[0]) 
    vectorT=arc.vectorTangents# Arc切向量 tangent vector
    theta=get_angle_of_two_vectors(vectorL, vectorT)
    if Forward:
        return theta
    else:
        return -theta

def get_intersect_point_of_line_section(para1, para2)->GeVec3d: #直线与平面的交点
    if isinstance(para1,list) and isinstance(para2,Section):
        line=para1
        sec=para2
    elif isinstance(para2,list) and isinstance(para1,Section):
        line=para2
        sec=para1
    else:
        raise TypeError('parameters error!')
    # 直线
    m=line[0]
    # create_geometry1(translate(m)*Sphere())
    u=unitize(line[1]-line[0])
    # 平面
    n=get_points_from_section(sec)[0]
    n1=get_points_from_section(sec)[1]
    # n1=get_points_from_section(sec)[2]
    # n1=get_points_from_section(sec)[3]
    v=get_matrix_axisz(sec.transformation)
    deno=v.x*u.x+v.y*u.y+v.z*u.z # denomintor
    if abs(deno)<1e-10:
        return False #直线与平面平行，无交点
    else:
        t=(v.x*(n.x-m.x)+v.y*(n.y-m.y)+v.z*(n.z-m.z))/deno
    return GeVec3d(m.x+u.x*t, m.y+u.y*t, m.z+u.z*t) #参数方程形式

# For Sweep only(about_sweep)
def interlink_bool_loft(sec:Section, traj:list):
    # 转换到局部坐标系处理
    transTraj=get_trajectory_matrix(traj[0],traj[1]) #转换矩阵
    invTraj=inverse_std(transTraj)
    line=[invTraj*traj[0][0], invTraj*traj[0][1]] #局部坐标系下的line-arc
    arc=invTraj*traj[1]
    # create_geometry1(Line(*line,arc))

    # section-Z方向投影
    verctorZ=get_matrix_axisz(transTraj)
    secShadowZ=vector_shadow(verctorZ)*sec
    secShadowZO=secShadowZ #translate(traj[0][1]-traj[0][0])*
    secRelaZO=invTraj*secShadowZO
    rangeL=get_range_of_section(secRelaZO)
    if rangeL[1]>norm(traj[0][1]-traj[0][0]):
        raise TypeError('line-1 too short!')
    # create_geometry1(secRelaZO)

    # section-X方向投影
    vectorFirst=unitize(traj[0][1]-traj[0][0]) #First Vector第一个向量
    secShadow=vector_shadow(vectorFirst)*sec
    pointShadow=get_nearest_point_on_line(traj[0],GeVec3d(0,0,0))
    pointMove=traj[0][0]-pointShadow
    secShadowO=translate(pointMove)*secShadow
    secRelaO=invTraj*secShadowO #in traj coordinate, shadow section at origin point.
    angleInters=get_angle_of_two_vectors(vectorFirst,get_matrix_axisz(sec.transformation)) #此处默认sec-line1垂直
    # create_geometry1(secRelaO)

    # 边缘距离d-r
    rect=get_range_of_section(secRelaO) #rectangle
    dRight=rect[2]
    dLeft=rect[3]
    centerA=arc.pointCenter #圆弧
    startA=arc.pointStart
    R=sqrt((startA.x-centerA.x)**2+(startA.y-centerA.y)**2) #圆半径计算，暂不支持椭圆
    if abs(dLeft)>=R or abs(dRight)>=R :
        raise TypeError('d too long!')
    vectorL=unitize(line[1]-line[0])
    vectorT=arc.vectorTangents # Arc切向量 tangent vector
    angleInflect=get_angle_of_two_vectors(vectorL, vectorT) #line-arc拐角
    rotStartA=arbitrary_rotate(startA,GeVec3d(0,0,1),angleInflect)
    def shadow_inters(sec=GeTransform()):
        return scale(1/cos(angleInters),1/cos(angleInters),1)*rotz(angleInters)*sec
    rRightP=rotStartA*translate(startA)*shadow_inters()*GeVec3d(0,dRight,0)
    rLeftP=rotStartA*translate(startA)*shadow_inters()*GeVec3d(0,dLeft,0)
    rRight=R-norm(rRightP-centerA)
    rLeft=R-norm(rLeftP-centerA)
    # create_geometry1(shadow_inters(secRelaO))

    # 相交的3种情况
    if abs(angleInflect)<1e-10 or abs(angleInflect-pi)<1e-10: #同向或反向
        swLine=Sweep(sec,Line(traj[0][0],traj[0][1])) #世界坐标系
        swArc=Sweep(translate(traj[0][1]-traj[0][0])*sec,Line(traj[1]))
        return Combine(swLine, swArc)

    elif angleInflect<0: #右侧相交
        secClipO=points_to_section(GeVec3d(0,rect[2],rect[5]),GeVec3d(0,rect[3],rect[5]),GeVec3d(0,rect[3],rect[4]),GeVec3d(0,rect[2],rect[4]))
        # 等距比交点计算
        interPx=centerA.x-sqrt((R-rRight)**2-(dRight-centerA.y)**2)
        # interPy = lambda x: ((x-centerA.x)**2+centerA.y**2-R**2) / (2*centerA.y-2*R)
        interP = GeVec3d(interPx,dRight,0)
        def interPy(x): # 曲线方程
            k=dRight/rRight
            A=1-1/k**2
            B=2*R/k-2*centerA.y
            C=centerA.y**2-R**2+(x-centerA.x)**2
            return (-B+sqrt(B**2-4*A*C))/(2*A)
        def get_new_d(rLeftPi,rRightPi): #圆弧部分，获得布尔的截面比例
            k=dRight/rRight
            A=1-1/k**2
            B=2*R/k-2*centerA.y
            C=centerA.y**2-R**2
            x1=rLeftPi.x
            y1=rLeftPi.y
            x2=rRightPi.x
            y2=rRightPi.y
            if abs(y1-y2)<1e-10:
                y=y1
                x=centerA.x+sqrt(A*y**2+B*y+C)
            else:
                A1=y2-y1 #直线参数方程
                B1=x1-x2
                C1=y1*(x2-x1)-x1*(y2-y1)
                a=(x2-x1)/(y2-y1)
                b=x1-y1*(a)-centerA.x
                A2=A+a**2
                B2=B+2*a*b
                C2=C+b**2
                y=(-B2+sqrt(B2**2-4*A2*C2))/(2*A2)
                x=(-C1-B1*y)/A1
            interPi=GeVec3d(x,y,0)
            return norm(rRightPi-interPi)/norm(rRightP-startA)
        # 圆弧布尔夹角
        angleArcB=get_angle_of_two_vectors(rRightP-centerA, interP-centerA)
        rotCenterA=arbitrary_rotate(centerA,GeVec3d(0,0,1),angleArcB)
        # create_geometry1(rotCenterA*translate(startA)*rotz(angleInflect)*invTraj*sec) #直接获得-原始斜面
        # create_geometry1(translate(interP)*Sphere())
        # create_geometry1(Line(interP,centerA))
        discetNum=10
        secListL=[]
        secListA=[]
        # 离散截面
        for i in range(discetNum+1):
            # 直线部分
            x=interPx+(i/discetNum)*(startA.x-interPx)
            y=interPy(x) #等距比曲线坐标  
            if i==0:
                y=y+1e-5 #手动生成误差，使截面边的个数相等
            elif i==discetNum:
                y=y-1e-5
            # create_geometry1(translate(GeVec3d(x,y,0))*Sphere())
            secRela=translate(x,0,0)*secRelaO
            secClip=translate(x,y,0)*translate(0,dRight,0)*secClipO
            # create_geometry1(secClip)
            # create_geometry1(secRela)
            # create_geometry1(secRela-secClip)
            secListL.append(secRela-secClip)
            # 圆弧部分
            theta=(i/discetNum)*angleArcB
            # dtheta=get_angle_of_two_vectors(startA-centerA,GeVec3d(x,y,0)-centerA) #投影算法
            rotCenterA=arbitrary_rotate(centerA,GeVec3d(0,0,1),theta)
            ratio=get_new_d(rotCenterA*rLeftP, rotCenterA*rRightP)
            yr=ratio*dRight
            if i==0:
                yr=yr+1e-5
            elif i==discetNum:
                yr=yr-1e-5
            secCut=secRelaO-translate(0,-dLeft+dRight-yr,0)*secClipO #
            secEnd=rotCenterA*translate(startA)*rotz(angleInflect)*shadow_inters(secCut)
            secListA.append(secEnd)
            # create_geometry1(arot*translate(startA)*rotz(inflectAngle)*invTraj*sec)
            # create_geometry1(arot*translate(startA)*rotz(inflectAngle)*trans(secRelaO))
            # create_geometry1(arot*translate(startA)*rotz(inflectAngle)*trans(translate(0,-dLeft+y,0)*secClipO))

        # 直线
        lfLine=Loft(secListL)
        lfLine.smooth=True
        blLine= Loft(invTraj*sec, translate(interPx,0,0)*secRelaO)
        # create_geometry1(lfLine)
        # create_geometry1(blLine)

        # 圆弧
        blArc=Loft(secListA)
        blArc.smooth=True
        # create_geometry1(trans(secRelaO))
        rotCenterA=arbitrary_rotate(centerA,GeVec3d(0,0,1),angleArcB)
        newArc=rotCenterA*arc
        newArc.scope=newArc.scope-angleArcB
        swArc=rotCenterA*Sweep(translate(startA)*rotz(angleInflect)*invTraj*sec,Line(newArc))
        # create_geometry1(blArc)
        # create_geometry1(swArc)
        
        # 二角
        angleHalfI=angleInflect/2 #+pi/2-pi/2
        secCutR=secRelaO-translate(0,dRight,0)*secClipO
        secCutH=scale(1/cos(angleHalfI),1/cos(angleHalfI),1)*rotz(angleHalfI)*secCutR
        hornLine=translate(startA)*Loft(secCutR,secCutH)
        # create_geometry1(hornLine)
        # hornArcO=rotz((angleHalfI+pi/2))*reflect('xz')*rotz(-(angleHalfI+pi/2))*horn #镜像处理
        # hornArc=translate(startA)*hornArcO
        secCutH2=scale(1/cos(pi/4),1/cos(pi/4),1)*rotz(-pi)*secCutR
        hornArcT=translate(startA)*Loft(secCutH2,secCutH)
        # create_geometry1(hornArcT)
        geo=Combine(lfLine,blLine,blArc,swArc,hornLine,hornArcT)
        create_geometry1(transTraj*geo)

        return geo

    else: #左侧相交
        ...


def shadow_inters(sec=GeTransform(), angleInters=0): #放大投影矩阵
    return scale(1/cos(angleInters),1/cos(angleInters),1)*rotz(angleInters)*sec

def get_edge_points(sec):
    points=get_points_from_section(sec,100) 
    #sweep专用，相对坐标系下，在T_trajc-Z轴方向投影的上下边缘顶点；
    pLeft=pRight=points[0]
    for i in points:
        if i.y>pLeft.y:
            pLeft=i
        if i.y<pRight.y:
            pRight=i
    return (pRight,pLeft)


def simple_sweep(sec:Section, traj:list): #一种简易的处理圆弧-直线脊线sweep的方法
    # 转换到局部坐标系处理
    transTraj=get_trajectory_matrix(traj[0],traj[1])
    invTraj=inverse_std(transTraj)
    # new line in relative coordinate
    line=[invTraj*traj[0][0], invTraj*traj[0][1]]
    vectorL=unitize(line[1]-line[0])
    # new arc in relative coordinate
    arc=invTraj*traj[1]
    centerA=arc.pointCenter
    startA=arc.pointStart
    vectorT=arc.vectorTangents # Arc切向量 tangent vector
    angleInflect=get_angle_of_two_vectors(vectorL, vectorT) # traj拐角
    # rotInflect=arbitrary_rotate(startA,GeVec3d(0,0,1),angleInflect) #先平移后旋转 专用

    # section-Z方向投影（获取顶点）
    secShadowZ=vector_shadow(GeVec3d(0,0,1))*invTraj*sec
    rangeL=get_range_of_section(secShadowZ)
    rect=get_edge_points(secShadowZ) #初始截面的顶点
    pRight=rect[0]
    pLeft=rect[1]
    rRight=translate(startA)*rotz(angleInflect)*pRight #圆弧位置的顶点
    rLeft=translate(startA)*rotz(angleInflect)*pLeft
    if rangeL[1]>norm(traj[0][1]-traj[0][0]):
        raise TypeError('line-1 too short!')
    # create_geometry1(secRelaZO)

    #section-X方向投影（获取投影截面）
    secShadowX=vector_shadow(GeVec3d(1,0,0))*invTraj*sec
    # create_geometry1(secShadowX)
    rect=get_range_of_section(secShadowX) #rectangle,上下顶点y坐标
    dRight=rect[2]
    dLeft=rect[3]
    R=sqrt((startA.x-centerA.x)**2+(startA.y-centerA.y)**2) #圆半径计算，暂不支持椭圆
    if abs(dLeft)>=R or abs(dRight)>=R :
        raise TypeError('d too long!')
    
    
    # 相交的3种情况
    if abs(angleInflect)<1e-10 or abs(angleInflect-pi)<1e-10: #同向或反向
        # swLine=transTraj*Loft(invTraj*sec,translate(line[1])*secRelaO)
        swLine=Sweep(sec,Line(traj[0][0],traj[0][1])) #世界坐标系
        # create_geometry1(swLine)
        # swArc=transTraj*Sweep(translate(line[1])*secRelaO,Line(arc)) #涉及投影面，在相对坐标系内处理
        swArc=Sweep(translate(traj[0][1]-traj[0][0])*sec,Line(traj[1]))
        # create_geometry1(swArc)
        return Combine(swLine, swArc)

    elif angleInflect<0: #右侧相交
        # 等距比交点
        # interPx=centerA.x-sqrt((R+rRight.y)**2-(dRight-centerA.y)**2) #v1
        # interPx=centerA.x-sqrt(R**2-centerA.y**2+2*pRight.y*centerA.y-2*R*pRight.y) #v2
        interPx=centerA.x-sqrt(R**2+pRight.x**2-centerA.y**2+2*pRight.y*centerA.y-2*R*pRight.y) #v3
        interP = GeVec3d(interPx,dRight,0)
        # interP = transTraj*GeVec3d(interPx,dRight,0)
        # create_geometry1(translate(interP)*Sphere())

        # 圆弧Sweep
        angleBroken=get_angle_of_two_vectors(rRight-centerA, interP-centerA) #broken sword
        rotBroken=arbitrary_rotate(centerA,GeVec3d(0,0,1),angleBroken)
        arcBroken=rotBroken*arc
        arcBroken.scope=arcBroken.scope-angleBroken
        swArc=rotBroken*Sweep(translate(startA)*rotz(angleInflect)*invTraj*sec,Line(arcBroken))
        
        # 倾斜角Line
        angleBevel=get_angle_of_two_vectors(GeVec3d(1,0,0),startA-interP)
        angleBevel=angleBevel-pi/2
        secBevel=scale(1/cos(angleBevel),1/cos(angleBevel),1)*rotz(angleBevel)*secShadowX #缩放倾斜面
        lfLine=Loft(invTraj*sec,translate(startA)*secBevel)
        # hornLine=translate(startA)*horn
        # create_geometry1(hornLine)
        
        # 倾斜角Arc
        secBroken=rotBroken*translate(startA)*rotz(angleInflect)*invTraj*sec
        hornArc=Loft(translate(startA)*secBevel, secBroken)
        # create_geometry1(hornArcT)

        geo=transTraj*Combine(lfLine,hornArc,swArc)
        geo=Combine(lfLine,hornArc,swArc)
        # create_geometry1(geo)
        return geo

    else: #左侧相交
        pass

    
     
def get_trajectory_matrix(para1, para2): #获取traj面所在的矩阵
    # traj(trajectory)平面，当前由[[vec3, vec3],arc]或[[vec3, vec3],[vec3, vec3]]组成
    if isinstance(para1, list) and isinstance(para2, Arc):
        vectorF=unitize(para1[1]-para1[0]) #First Vector第一个向量
        vectorN=para2.vectorNormal #traj面的法向量
        pointFirst=para1[0]
    elif isinstance(para1, list) and isinstance(para2, list):
        # and len(para2)==2 and isinstance(para2[0],(GeVec2d,GeVec3d)):
        vectorF=unitize(para1[1]-para1[0])
        mat=points_to_trans(para1[0],para1[1],para2[1]) #segment1,segment2不可共线
        vectorN=get_matrix_axisz(mat[0]) #segment1,segment2不可共线
        pointFirst=para1[0]
    elif isinstance(para1, Arc):
        vectorF=para1.vectorTangents
        vectorN=para1.vectorNormal
        pointFirst=para1.pointStart
    vectorY=cross(vectorN,vectorF)
    # # sec投影垂面,First vector作为z轴的坐标系（trajct section法向量为y轴）
    # Ttraj_vec=GeTransform([[vectorN.x,-vectorY.x,vectorF.x,0],
    #                     [vectorN.y,-vectorY.y,vectorF.y,0],
    #                     [vectorN.z,-vectorY.z,vectorF.z,0]])
    # # trajct section面所在的坐标系（First vector为x轴）
    # Ttraj_sec=GeTransform([[vectorF.x,vectorY.x,vectorN.x,0], #Y轴反向
    #                     [vectorF.y,vectorY.y,vectorN.y,0],
    #                     [vectorF.z,vectorY.z,vectorN.z,0]])
    Ttraj_sec=set_matrix_by_column_vectors(vectorF,vectorY,vectorN,pointFirst)
    return Ttraj_sec

def get_sides_of_section(sec:Section, traj:list): #获取section在traj面的上下边缘距离
    # Tsec=get_rot_matrix(sec.transformation)
    Ttraj_sec=get_trajectory_matrix(traj[0],traj[1])
    vectorF=get_matrix_axisx(Ttraj_sec)
    vectorN=get_matrix_axisz(Ttraj_sec)
    secShadow=vector_shadow(vectorF)*sec #沿Vector First的投影
    pointShadow=get_nearest_point_on_line(traj[0],GeVec3d(0,0,0))#注意区分traj
    pointMove=pointShadow-traj[0][0]
    secRela=inverse_std(translate(pointMove)*Ttraj_sec)*secShadow
    # secSides=vector_shadow(vectorN)*secShadow #TopView投影，得到一条直线
    # pointShadow=get_nearest_point_on_line(traj[0],GeVec3d(0,0,0))#注意区分traj
    # # points=get_points_from_section(secSides)
    # pointMove=traj[0][0]-pointShadow
    # coordRela=translate(pointMove)*Ttraj_sec
    # secSidesRela=inverse(coordRela)*secSides
    # points=get_points_from_section(secSidesRela)
    # rang=get_range_of_section(secSidesRela)
    return get_range_of_section(secRela)

def straight_shadow_loft(sec:Section, traj:list): #直线投影Loft部分
    vectorFirst=unitize(traj[1]-traj[0]) #First Vector第一个向量
    pointFirst=traj[0]
    # points=get_points_from_secton(sec)
    # pointSecStd=get_intersect_point_of_line_section(traj,sec)
    pointSecStd=traj[0]
    # j=is_point_locate_plane(pointSecStd,sec)
    if is_point_in_polygon(pointSecStd,sec):
    # pointSecStd=GeVec3d(get_translate_para(sec.transformation))
    # vectorMove=pointFirst-pointSecStd #记录相对点
    # sec=translate(vectorMove)*sec
    # T1=translate(traj[0])
    # T2=translate(traj[1]-traj[0])
        #由于投影面过原点，需要求出投影面与traj-line的交点，算出交点与line端点的距离
        pointShadow=get_nearest_point_on_line(traj,GeVec3d(0,0,0))
        # create_geometry1(translate(pointS)*Sphere())
        pointMove=traj[1]-pointShadow # 
        secShadow=vector_shadow(vectorFirst)*sec
        # create_geometry1(T1*secShadow)
        # create_geometry1(T2*T1*secShadow)
        return Loft(sec, translate(pointMove)*secShadow)
    else:
        raise TypeError('point not in polygon!')

# ----------------------------------------------------------
# 新模型
def get_discrete_loft(sec1, sec2):
    discrSecNum=100
    discrTrajNum=10
    secList1=get_points_from_section(sec1, discrSecNum, False) #top
    secList2=get_points_from_section(sec2, discrSecNum, False, True) #make polygon close
    secList2=remove_coincident_point(secList2)
    len1=len(secList1)
    len2=len(secList2)
    di=len2-len1
    secList2=get_points_from_section(sec2, discrSecNum-di, False, True) #make polygon close
    secList2=remove_coincident_point(secList2)
    
    # for i in range(discrSecNum):
    #     create_geometry1(scale(100)*Line(secList1[i],secList2[i]))
    
    sectionList=[]
    for i in range(discrTrajNum+1):
        pointList=[]
        for j in range(discrSecNum):
            pointJ=secList2[j]+(i/discrTrajNum)*(secList1[j]-secList2[j])
            pointList.append(pointJ)
        # sectionList.append(translate(0,0,i/2)*Section(to_vec2(pointList)))
        sectionList.append(points_to_section(pointList))
        # create_geometry1(scale(100)*points_to_section(pointList))

    # create_geometry1(scale(100)*Line(secList1))
    # create_geometry1(scale(100)*Line(secList2))
    geo=Loft(sectionList)
    geo.smooth=True
    # create_geometry1(scale(100)*geo)
    return geo



def twist_sweep(sec:Section, height:float, pitch:float, ccw=True):
    # 绕原点向上的螺旋
    discrSecNum=100
    pointList=get_points_from_section(sec, discrSecNum, False, True) #make polygon close
    secDis=points_to_section(pointList)

    secList=[]
    discretNum=floor(height)*1
    for i in range(discretNum+1):
        secList.append(translate(0,0,height*i/discretNum)*rotz(height/pitch*2*pi*i/discretNum)*secDis)
    geo=Loft(secList)
    geo.smooth=True
    # create_geometry1(geo)

    return geo