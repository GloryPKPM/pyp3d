#################################################################
#                       1.0 兼容接口                            #
#################################################################
# Copyright (C), 2019-2028, Beijing GLory PKPM Tech. Co., Ltd.
# Brief: PKPM-BIMBase Python二次开发SDK与参数化组件功能。
# Author: YanYinji, akingse, YouQi
# Date: 2021/08/07

from .pyp3d_data import *
from .pyp3d_matrix import *
from .pyp3d_calculation import *
from .pyp3d_component import *
from .pyp3d_geometry import *
from math import *

# pyp3d_data
Vec3 = GeVec3d
Vec2 = GeVec2d
# pyp3d_component
combine = Combine
LineString = Line
# PointString = Point
# pyp3d_matrix
rotation = rotate
translation = translate

# pyp3d_geometry
to_section = points_to_section
vector_to_angle = get_angle_of_two_vectors
BPParametricComponent = UnifiedModule(PARACMPT_PARAMETRIC_COMPONENT)
# --------------------------------------------------------------------
class P3DData(Component):
    '''
    "obvious";			// 显示的
    "pivotal";			// 关键属性，触发replace
    "readonly";			// 只读
    "show";				// 几何体显示
    "group";			// 分组
    "description";	    // 描述
    '''
    def __init__(self, data=dict()):
        Component.__init__(self)
        self.name = Attr('', obvious=True)
        for k,v in data.items():
            self[k]=v
    def __setitem__(self, key, value):
        # Combine geometry in the list, using recursion
        def combineList(geo):
            for i in geo:
                if not (isinstance(i, list) or issubclass(type(i),Graphics)):
                    raise TypeError('Combine\'s parameter must be "Graphics"!')
                if isinstance(i, list):
                    combineList(i)
            geo=Combine(*geo)
            return geo
        if isinstance(value, list) :
            if len(value)>=1:
                if issubclass(type(value[0]),Graphics): #Primitives
                    value = combineList(value)
                    # value = Combine(value)
        Noumenon.__setitem__(self, key, value)
    def setup(self, key, **args):
        if key not in self:
            self[key] = Attr()
        for k, v in args.items():
            self.at(key)[k] = v
    def view(self, value):
        if isinstance(value, GeTransform):
            self[PARACMPT_KEYWORD_PREVIEW_VIEW] = value
        else:
            raise TypeError('unsupported type!')
    def set_view(self, az, el):
        '''
        az: orientation\n
        el: elevation\n
        '''
        self[PARACMPT_KEYWORD_PREVIEW_VIEW] = rotate(GeVec3d(1, 0, 0), -el) * rotate(GeVec3d(0, 1, 0), -az) * \
            rotate(GeVec3d(0, 0, 1), pi) * rotate(GeVec3d(0, 1, 0), pi) * rotate(GeVec3d(1, 0, 0), pi/2)
    def interact(self, context):
        if context['action']=='right down':
            print(1)
        elif context['action']=='left down':
            print(2)
        elif context['action']=='mouse movement':
            print(3)
        else:...

def unite(*args):
    return Fusion(*args)

def substract(a, b):
    if isinstance(a,list):
        a=Combine(*a)
    if isinstance(b,list):
        b=Combine(*b)
    return Fusion(a, -b)

def intersection(*args): # 当参数为combine时，处理为unite
    # return Intersect(*args)
    if isinstance(args[0], Combine):
        A=args[0].parts[0]
        for i in range(1,len(args[0].parts)):
            A=unite(A,args[0].parts[i])
    else:
        A=args[0]
    if isinstance(args[1], Combine):
        B=args[1].parts[0]
        for i in range(1,len(args[1].parts)):
            B=unite(B,args[1].parts[i])
    else:
        B=args[1]
    return Intersect(A,B)

def create_bsplinepoints(controlPoints:list, curveOrder:int, discreteNum:int)->list:#创建B样条线点集
    '''
    using control points,  return BsplinePoints points
    '''
    if curveOrder > len(controlPoints):
        raise ValueError('curveOrder\'s parameter is the count of max control-points,  please input proper parameter!')
    else:
        return UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_CREATE_BSPLINEPOINTS)(controlPoints, curveOrder, discreteNum)
# ---------------------------------------------------------------
class Ellipse(Arc): #椭圆 2.0
    def __init__(self, center=GeVec3d(0,0,0), vector0=GeVec3d(1,0,0), vector90=GeVec3d(0,1,0), start=0, sweep=2*pi):
        Arc.__init__(self)
        self.representation = 'Ellipse'
        # vectorC=cross(vector0,vector90)*(1/norm(cross(vector0,vector90)))
        vectorC=unitize(cross(vector0,vector90))
        axisZ=GeVec3d(0,0,1)
        vertex=GeVec3d(1,1,1)
        if abs(vectorC.x)+abs(vectorC.y)<1e-10 and abs(vectorC.z)>1e-10: # plane='XY'
            if vectorC.z<0:
                start=-start
                axisZ=-axisZ
            vectorV=vectorC
            axisAngle=GeTransform()
        elif abs(vectorC.z)+abs(vectorC.y)<1e-10 and abs(vectorC.x)>1e-10: # plane='YZ'
            if vectorC.x<0:
                start=-start
                axisZ=-axisZ
            vector0=rotate(vertex,-2*pi/3)*vector0
            vector90=rotate(vertex,-2*pi/3)*vector90
            vectorV=rotate(vertex,-2*pi/3)*vectorC
            axisAngle=rotate(vertex,2*pi/3)
        elif abs(vectorC.x)+abs(vectorC.z)<1e-10 and abs(vectorC.y)>1e-10: # plane='ZX'
            if vectorC.y<0:
                start=-start
                axisZ=-axisZ
            vector0=rotate(vertex,2*pi/3)*vector0
            vector90=rotate(vertex,2*pi/3)*vector90
            vectorV=rotate(vertex,2*pi/3)*vectorC
            axisAngle=rotate(vertex,-2*pi/3)
        else:
            raise ValueError('cannot judge "Ellipse" locate plane!')
        rotz=rotate(axisZ,start)
        trans=translate(center)
        oblate=GeTransform([[vector0.x, vector90.x, vectorV.x, 0],
                            [vector0.y, vector90.y, vectorV.y, 0],
                            [vector0.z, vector90.z, vectorV.z, 0]])
        self.transformation=trans*axisAngle*oblate*rotz
        self.scope = sweep

class ContourLine(Line): #轮廓线（包含多线段和椭圆） 2.0
    def __init__(self, *args):
        Line.__init__(self)
        self.representation = 'ContourLine'
        if len(args)==1 and (isinstance(args[0], list) or isinstance(args[0], tuple)): 
            self.parts = list(args[0])
        else: 
            self.parts = list(args)

class Cone(Loft): #圆台体
    def __init__(self, centerA=GeVec3d(0, 0, 0), centerB=GeVec3d(0, 0, 1), radiusA=1.0, radiusB=None):
        Loft.__init__(self)
        if radiusB is None:
            radiusB = radiusA
        self.representation = 'Cone'
        transA=points_to_matrix(centerA, centerB)
        section_a = transA * scale(radiusA) * Section(Arc())
        transB=translate(centerB-centerA) * transA
        section_b = transB * scale(radiusB) * Section(Arc())
        self.parts = [section_a, section_b]

class Box(Loft): #四棱台 2.0
    def __init__(self, baseOrigin=GeVec3d(0,0,0) , topOrigin=GeVec3d(0,0,1), vectorX=GeVec3d(1,0,0), vectorY=GeVec3d(0,1,0),
                    baseX=1.0, baseY=1.0, topX=1.0, topY=1.0):
        Loft.__init__(self)
        self.representation = 'Box'
        vectorZ = topOrigin - baseOrigin
        self.transformation = GeTransform([[vectorX.x, vectorY.x, vectorZ.x, baseOrigin.x],
                                           [vectorX.y, vectorY.y, vectorZ.y, baseOrigin.y],
                                           [vectorX.z, vectorY.z, vectorZ.z, baseOrigin.z]])
        section_a = Section(GeVec2d(0,0), GeVec2d(baseX,0), GeVec2d(baseX,baseY), GeVec2d(0,baseY))
        section_b = translate(0,0,1) * Section(GeVec2d(0,0), GeVec2d(topX,0), GeVec2d(topX,topY), GeVec2d(0,topY))
        self.parts = [section_a,section_b]

class RuledSweep(Loft): #直纹扫描
    def __init__(self, points1=[GeVec3d(0,0,0),GeVec3d(0,1,0),GeVec3d(2,0,0)], \
                    points2 = [GeVec3d(0,0,2),GeVec3d(0,2,1),GeVec3d(2,0,1)]):
        Loft.__init__(self)
        self._name = 'RuledSweep'
        if len(points1)!=len(points2):
            raise TypeError('the points number of two Section must be equal!')
        points1 = points_to_offset(points1)
        points2 = points_to_offset(points2)
        section_a = points_to_section(points1)
        section_b = points_to_section(points2)
        self.parts = [section_a,section_b]

class RuledSweepPlus(Loft): #直纹扫描+
    def __init__(self, contours =[[GeVec3d(0,0,0),GeVec3d(0,1,0),GeVec3d(1,0,0)],\
                                [GeVec3d(0,0,1),GeVec3d(0,1/2,1),GeVec3d(1/2,0,1)],\
                                [GeVec3d(0,0,2),GeVec3d(0,1,2),GeVec3d(1,0,2)]]):
        Loft.__init__(self)
        self._name = 'RuledSweepPlus'
        self.smooth = True
        self.parts = []
        for i in range(len(contours)):
            section = points_to_section(contours[i])
            self.parts.append(section)

class TorusPipe(Sweep): # 环形管 2.0
    def __init__(self, center=GeVec3d(0,0,0), vectorX=GeVec3d(1,0,0), vectorY= GeVec3d(0,1,0), 
                  torusRadius=5, pipeRadius=1, sweepAngle=2*pi):
        Sweep.__init__(self)
        self.representation = 'TorusPipe'
        arcSection = translate(torusRadius,0,0)*scale(pipeRadius) * Arc()
        section = rotate(GeVec3d(1,0,0),pi/2)*Section(arcSection)
        arcTraject = scale(torusRadius) * Arc()
        arcTraject.scope = sweepAngle
        line = Line(arcTraject)
        vectorZ = cross(vectorX , vectorY)
        self.transformation=GeTransform([[vectorX.x, vectorY.x, vectorZ.x, center.x],
                                        [vectorX.y, vectorY.y, vectorZ.y, center.y],
                                        [vectorX.z, vectorY.z, vectorZ.z, center.z]])
        self.section = section
        self.trajectory = line

class RotationalSweep(Sweep): # 旋转扫描 (圆弧放样) 2.0
    def __init__(self, points=[GeVec3d(2,0,0),GeVec3d(3,0,0),GeVec3d(2,1,0)],\
        center=GeVec3d(0,0,0), axis=GeVec3d(0,1,0), sweepAngle=1.5*pi):
        Sweep.__init__(self)
        self.representation = 'RotationalSweep'
        if all(isinstance(i,GeVec3d) for i in points):
            section = points_to_section(points)
        elif len(points)==1 and isinstance(points[0],Arc):
            section = Section(points[0])
        else:
            raise TypeError('parameters error!')
        arc = vector_to_matrix(axis) * Arc()
        arc.scope = sweepAngle
        line = translate(center)* Line(arc)
        self.section = section
        self.trajectory = line

class Extrusion(Sweep): # 拉伸体 (直线放样) 2.0
    def __init__(self, points=[GeVec3d(1,0,0), GeVec3d(3,0,0),GeVec3d(3,2,0),GeVec3d(0,2,0)], extrusionVector=GeVec3d(1,0,1)):
        Sweep.__init__(self)
        self.representation = 'Extrusion'
        section = points_to_section(points)
        line = Line(points[0],points[0] + extrusionVector)
        self.section = section
        self.trajectory = line

class ExtrusionPlus(Sweep): # 复杂拉伸体 2.0
    def __init__(self, contourLines=[ContourLine([Line(GeVec3d(2,-2,0),GeVec3d(2,2,0),GeVec3d(-2,2,0),GeVec3d(-2,-2,0))]),\
        ContourLine([Ellipse()])], extrusionVector=GeVec3d(0, 0 ,4)):
        Sweep.__init__(self)
        self.representation = 'ExtrusionPlus'
        if len(contourLines) == 0 :
            raise TypeError('ExtrusionPlus() has one ContourLine at least!')
        OuterContour=contourLines[0]
        plane=judge_locate_plane(OuterContour.parts)
        # first out-coutour
        if len(contourLines)>=1: 
            if plane=='XY':
                if isinstance(OuterContour.parts[0],Line):
                    transA=translate(0,0,OuterContour.parts[0].parts[0].z)
                    invA=translate(0,0,-OuterContour.parts[0].parts[0].z)
                    center=OuterContour.parts[0].parts[0]
                elif isinstance(OuterContour.parts[0],(Ellipse,Arc)):
                    transA=translate(0,0,OuterContour.parts[0].transformation._mat[2][3])
                    invA=translate(0,0,-OuterContour.parts[0].transformation._mat[2][3])
                    center=GeVec3d(OuterContour.parts[0].transformation._mat[0][3],
                                    OuterContour.parts[0].transformation._mat[1][3],
                                    OuterContour.parts[0].transformation._mat[2][3])
                else:
                    raise TypeError('Line type error!')
                args=[]
                for coutour in OuterContour.parts:
                    if isinstance(coutour,Line):
                        for i in range(len(coutour.parts)):
                            args.append(to_vec2(coutour.parts[i]))
                    elif isinstance(coutour,(Ellipse,Arc)):
                        args.append(invA*coutour)
                    else:
                        raise TypeError('Line type error!')
                args=polygon_to_ccw(args)
                section = transA*Section(*args)
            elif plane=='YZ':
                if isinstance(OuterContour.parts[0],Line):
                    transA=translate(0,0,OuterContour.parts[0].parts[0].x)
                    invA=translate(0,0,-OuterContour.parts[0].parts[0].x)
                    center=OuterContour.parts[0].parts[0]
                elif isinstance(OuterContour.parts[0],(Ellipse,Arc)):
                    transA=translate(0,0,OuterContour.parts[0].transformation._mat[0][3])
                    invA=translate(0,0,-OuterContour.parts[0].transformation._mat[0][3])
                    center=GeVec3d(OuterContour.parts[0].transformation._mat[0][3],
                                    OuterContour.parts[0].transformation._mat[1][3],
                                    OuterContour.parts[0].transformation._mat[2][3])
                else:
                    raise TypeError('Line type error!')
                args=[]
                for coutour in OuterContour.parts:
                    if isinstance(coutour,Line):
                        coutourparts=rotate(GeVec3d(1,1,1),-2*pi/3)*coutour.parts #donot renew original para
                        for i in range(len(coutourparts)):
                            args.append(to_vec2(coutourparts[i]))
                    elif isinstance(coutour,(Ellipse,Arc)):
                        args.append(invA*rotate(GeVec3d(1,1,1),-2*pi/3)*coutour)
                    else:
                        raise TypeError('Line type error!')
                args=polygon_to_ccw(args)
                section = rotate(GeVec3d(1,1,1),2*pi/3)*transA*Section(*args)
            elif plane=='ZX':
                if isinstance(OuterContour.parts[0],Line):
                    transA=translate(0,0,OuterContour.parts[0].parts[0].y)
                    invA=translate(0,0,-OuterContour.parts[0].parts[0].y)
                    center=OuterContour.parts[0].parts[0]
                elif isinstance(OuterContour.parts[0],(Ellipse,Arc)):
                    transA=translate(0,0,OuterContour.parts[0].transformation._mat[1][3])
                    invA=translate(0,0,-OuterContour.parts[0].transformation._mat[1][3])
                    center=GeVec3d(OuterContour.parts[0].transformation._mat[0][3],
                                    OuterContour.parts[0].transformation._mat[1][3],
                                    OuterContour.parts[0].transformation._mat[2][3])
                else:
                    raise TypeError('Line type error!')
                args=[]
                for coutour in OuterContour.parts:
                    if isinstance(coutour,Line):
                        coutourparts=rotate(GeVec3d(1,1,1),2*pi/3)*coutour.parts
                        for i in range(len(coutourparts)):
                            args.append(to_vec2(coutourparts[i]))
                    elif isinstance(coutour,(Ellipse,Arc)):
                        args.append(invA*rotate(GeVec3d(1,1,1),2*pi/3)*coutour)
                    else:
                        raise TypeError('Line type error!')
                args=polygon_to_ccw(args)
                section = rotate(GeVec3d(1,1,1),-2*pi/3)*transA*Section(*args)
            line = Line(center,center+extrusionVector)
        # multi out-contour
        for j in range(1,len(contourLines)):
            InnerContour=contourLines[j] 
            if plane=='XY':
                if isinstance(InnerContour.parts[0],Line):
                    transB=translate(0,0,InnerContour.parts[0].parts[0].z)
                    invB=translate(0,0,-InnerContour.parts[0].parts[0].z)
                    center=InnerContour.parts[0].parts[0]
                elif isinstance(InnerContour.parts[0],(Ellipse,Arc)):
                    transB=translate(0,0,InnerContour.parts[0].transformation._mat[2][3])
                    invB=translate(0,0,-InnerContour.parts[0].transformation._mat[2][3])
                    center=GeVec3d(InnerContour.parts[0].transformation._mat[0][3],
                                    InnerContour.parts[0].transformation._mat[1][3],
                                    InnerContour.parts[0].transformation._mat[2][3])
                else:
                    raise TypeError('Line type error!')
                argsB=[]
                for coutour in InnerContour.parts:
                    if isinstance(coutour,Line):
                        for i in range(len(coutour.parts)):
                            argsB.append(to_vec2(coutour.parts[i]))
                    elif isinstance(coutour,(Ellipse,Arc)):
                        argsB.append(invB*coutour)
                    else:
                        raise TypeError('Line type error!')
                argsB=polygon_to_ccw(argsB)
                sectionB = transB*Section(*argsB)
                section=section - sectionB 
            elif plane=='YZ':
                if isinstance(InnerContour.parts[0],Line):
                    transB=translate(0,0,InnerContour.parts[0].parts[0].x)
                    invB=translate(0,0,-InnerContour.parts[0].parts[0].x)
                    center=InnerContour.parts[0].parts[0]
                elif isinstance(InnerContour.parts[0],(Ellipse,Arc)):
                    transB=translate(0,0,InnerContour.parts[0].transformation._mat[0][3])
                    invB=translate(0,0,-InnerContour.parts[0].transformation._mat[0][3])
                    center=GeVec3d(InnerContour.parts[0].transformation._mat[0][3],
                                    InnerContour.parts[0].transformation._mat[1][3],
                                    InnerContour.parts[0].transformation._mat[2][3])
                else:
                    raise TypeError('Line type error!')
                argsB=[]
                for coutour in InnerContour.parts:
                    if isinstance(coutour,Line):
                        coutourparts=rotate(GeVec3d(1,1,1),-2*pi/3)*coutour.parts
                        for i in range(len(coutourparts)):
                            argsB.append(to_vec2(coutourparts[i]))
                    elif isinstance(coutour,(Ellipse,Arc)):
                        argsB.append(invB*rotate(GeVec3d(1,1,1),-2*pi/3)*coutour)
                    else:
                        raise TypeError('Line type error!')
                argsB=polygon_to_ccw(argsB)
                sectionB = rotate(GeVec3d(1,1,1),2*pi/3)*transB*Section(*argsB)
                section=section - sectionB 
            elif plane=='ZX':
                if isinstance(InnerContour.parts[0],Line):
                    transB=translate(0,0,InnerContour.parts[0].parts[0].y)
                    invB=translate(0,0,-InnerContour.parts[0].parts[0].y)
                    center=InnerContour.parts[0].parts[0]
                elif isinstance(InnerContour.parts[0],(Ellipse,Arc)):
                    transB=translate(0,0,InnerContour.parts[0].transformation._mat[1][3])
                    invB=translate(0,0,-InnerContour.parts[0].transformation._mat[1][3])
                    center=GeVec3d(InnerContour.parts[0].transformation._mat[0][3],
                                    InnerContour.parts[0].transformation._mat[1][3],
                                    InnerContour.parts[0].transformation._mat[2][3])
                else:
                    raise TypeError('Line type error!')
                argsB=[]
                for coutour in InnerContour.parts:
                    if isinstance(coutour,Line):
                        coutourparts=rotate(GeVec3d(1,1,1),2*pi/3)*coutour.parts
                        for i in range(len(coutourparts)):
                            argsB.append(to_vec2(coutourparts[i]))
                    elif isinstance(coutour,(Ellipse,Arc)):
                        argsB.append(invB*rotate(GeVec3d(1,1,1),2*pi/3)*coutour)
                    else:
                        raise TypeError('Line type error!')
                argsB=polygon_to_ccw(argsB)
                sectionB = rotate(GeVec3d(1,1,1),-2*pi/3)*transB*Section(*argsB)
                section=section - sectionB # 
        # compat Extrusion
        if len(contourLines)==1:
            OuterContour=contourLines[0] 
            if len(OuterContour.parts)==1 and isinstance(OuterContour.parts[0],Line):# only the point section use
                lines=OuterContour.parts[0]
                section = points_to_section(lines.parts)
                line = Line(lines.parts[0],lines.parts[0] + extrusionVector)
        self.section = section
        self.trajectory = line

class FilletPipe(Combine): # 圆角管
    def __init__(self, points=[GeVec3d(0,0,0),GeVec3d(100,0,0),GeVec3d(100,0,50),GeVec3d(200,0,0)], \
        filletRadius=[0,5,5,0], pipeRadius=2):
        Combine.__init__(self)
        self.representation = 'FilletPipe'
        if len(points) != len(filletRadius):
            raise ValueError('number of filletRadius, number of nodes, must be equal!')
        self.parts = []
        point_start = points[0]
        for i in range(1, len(points)-1):
            vector_front = unitize(points[i-1] - points[i])
            vector_after = unitize(points[i+1] - points[i])
            sin_theta = sqrt(0.5*(1.0-dot(vector_front, vector_after)))
            theta = asin(sin_theta)
            fillet_range = filletRadius[i] / tan(theta)
            self.parts.append(Cone(point_start, points[i] + fillet_range*vector_front, pipeRadius, pipeRadius))
            point_start = points[i] + fillet_range*vector_after
            vector_normal = vector_front + vector_after
            if norm(vector_normal) < 1e-10:
                continue
            point_center = points[i] + (filletRadius[i]/sin_theta) * unitize(vector_normal)
            vector_x = unitize(point_start-point_center)
            vector_y = unitize(cross(cross(vector_front, vector_after), vector_x))
            self.parts.append(TorusPipe(point_center, vector_x, vector_y, filletRadius[i], pipeRadius, pi-2*theta))
        self.parts.append(Cone(point_start, points[-1], pipeRadius, pipeRadius))

class CurveLoft(Loft): # 曲线放样 2.0
    def __init__(self, outerLine=[Arc()], keypoints=[GeVec3d(0,0,0),GeVec3d(10,0,0),GeVec3d(10,10,0),GeVec3d(0,10,0)], \
        discreteNum=50, curveOrder=3):
        Loft.__init__(self)
        self.representation = 'CurveLoft'
        self.smooth = True
        section=rotate(Vec3(0,1,0),-pi/2)*Section(*outerLine)
        # section=rotate(Vec3(0,1,0),-pi/2)*to_section(outerLine)
        points=create_bsplinepoints(keypoints,curveOrder,discreteNum)
        lenP=len(points)
        lineList=[] # segment
        for i in range(lenP-1):
            lineList.append([points[i],points[i+1]])
        sectionList=[translate(points[0])*lean_section(points[1],points[0],0)*section]
        for i in range(1,lenP-1):
            theta=get_angle_of_two_vectors(lineList[i-1],lineList[i])/2
            matrix=GeTransform([[1/cos(theta),0,0,0],
                                [0,1/cos(theta),0,0],
                                [0,0,1,0]])
            sectioni=translate(points[i])*matrix*lean_section(points[i],points[i-1],theta)*section
            sectionList.append(sectioni)
        sectionList.append(translate(points[lenP-1])*lean_section(points[lenP-1],points[lenP-2],0)*section)
        self.parts = sectionList

def Area(contourLines=[ContourLine([Line(GeVec3d(2,-2,0),GeVec3d(0,2,0),GeVec3d(-2,-2,0))]),\
                        ContourLine([Ellipse()])]):
    OuterContour=contourLines[0]
    plane=judge_locate_plane(OuterContour.parts)
    # first out-coutour
    if len(contourLines)>=1: 
        if plane=='XY':
            if isinstance(OuterContour.parts[0],Line):
                transA=translate(0,0,OuterContour.parts[0].parts[0].z)
                invA=translate(0,0,-OuterContour.parts[0].parts[0].z)
            elif isinstance(OuterContour.parts[0],Ellipse):
                transA=translate(0,0,OuterContour.parts[0].transformation._mat[2][3])
                invA=translate(0,0,-OuterContour.parts[0].transformation._mat[2][3])
            else:
                raise TypeError('Line type error!')
            args=[]
            for coutour in OuterContour.parts:
                if isinstance(coutour,Line):
                    for i in range(len(coutour.parts)):
                        args.append(to_vec2(coutour.parts[i]))
                elif isinstance(coutour,Ellipse):
                    args.append(invA*coutour)
                else:
                    raise TypeError('Line type error!')
            args=polygon_to_ccw(args)
            section = transA*Section(*args)
        elif plane=='YZ':
            if isinstance(OuterContour.parts[0],Line):
                transA=translate(0,0,OuterContour.parts[0].parts[0].x)
                invA=translate(0,0,-OuterContour.parts[0].parts[0].x)
            elif isinstance(OuterContour.parts[0],Ellipse):
                transA=translate(0,0,OuterContour.parts[0].transformation._mat[0][3])
                invA=translate(0,0,-OuterContour.parts[0].transformation._mat[0][3])
            else:
                raise TypeError('Line type error!')
            args=[]
            for coutour in OuterContour.parts:
                if isinstance(coutour,Line):
                    coutourparts=rotate(GeVec3d(1,1,1),-2*pi/3)*coutour.parts #donot renew original para
                    for i in range(len(coutourparts)):
                        args.append(to_vec2(coutourparts[i]))
                elif isinstance(coutour,Ellipse):
                    args.append(invA*rotate(GeVec3d(1,1,1),-2*pi/3)*coutour)
                else:
                    raise TypeError('Line type error!')
            args=polygon_to_ccw(args)
            section = rotate(GeVec3d(1,1,1),2*pi/3)*transA*Section(*args)
        elif plane=='ZX':
            if isinstance(OuterContour.parts[0],Line):
                transA=translate(0,0,OuterContour.parts[0].parts[0].y)
                invA=translate(0,0,-OuterContour.parts[0].parts[0].y)
            elif isinstance(OuterContour.parts[0],Ellipse):
                transA=translate(0,0,OuterContour.parts[0].transformation._mat[1][3])
                invA=translate(0,0,-OuterContour.parts[0].transformation._mat[1][3])
            else:
                raise TypeError('Line type error!')
            args=[]
            for coutour in OuterContour.parts:
                if isinstance(coutour,Line):
                    coutourparts=rotate(GeVec3d(1,1,1),2*pi/3)*coutour.parts
                    for i in range(len(coutourparts)):
                        args.append(to_vec2(coutourparts[i]))
                elif isinstance(coutour,Ellipse):
                    args.append(invA*rotate(GeVec3d(1,1,1),2*pi/3)*coutour)
                else:
                    raise TypeError('Line type error!')
            args=polygon_to_ccw(args)
            section = rotate(GeVec3d(1,1,1),-2*pi/3)*transA*Section(*args)
    # multi out-contour
    for j in range(1,len(contourLines)):
        InnerContour=contourLines[j] 
        if plane=='XY':
            if isinstance(InnerContour.parts[0],Line):
                transB=translate(0,0,InnerContour.parts[0].parts[0].z)
                invB=translate(0,0,-InnerContour.parts[0].parts[0].z)
            elif isinstance(InnerContour.parts[0],Ellipse):
                transB=translate(0,0,InnerContour.parts[0].transformation._mat[2][3])
                invB=translate(0,0,-InnerContour.parts[0].transformation._mat[2][3])
            else:
                raise TypeError('Line type error!')
            argsB=[]
            for coutour in InnerContour.parts:
                if isinstance(coutour,Line):
                    for i in range(len(coutour.parts)):
                        argsB.append(to_vec2(coutour.parts[i]))
                elif isinstance(coutour,Ellipse):
                    argsB.append(invB*coutour)
                else:
                    raise TypeError('Line type error!')
            argsB=polygon_to_ccw(argsB)
            sectionB = transB*Section(*argsB)
            section=section - sectionB 
        elif plane=='YZ':
            if isinstance(InnerContour.parts[0],Line):
                transB=translate(0,0,InnerContour.parts[0].parts[0].x)
                invB=translate(0,0,-InnerContour.parts[0].parts[0].x)
            elif isinstance(InnerContour.parts[0],Ellipse):
                transB=translate(0,0,InnerContour.parts[0].transformation._mat[0][3])
                invB=translate(0,0,-InnerContour.parts[0].transformation._mat[0][3])
            else:
                raise TypeError('Line type error!')
            argsB=[]
            for coutour in InnerContour.parts:
                if isinstance(coutour,Line):
                    coutourparts=rotate(GeVec3d(1,1,1),-2*pi/3)*coutour.parts
                    for i in range(len(coutourparts)):
                        argsB.append(to_vec2(coutourparts[i]))
                elif isinstance(coutour,Ellipse) or isinstance(coutour,Arc):
                    argsB.append(invB*rotate(GeVec3d(1,1,1),-2*pi/3)*coutour)
                else:
                    raise TypeError('Line type error!')
            argsB=polygon_to_ccw(argsB)
            sectionB = rotate(GeVec3d(1,1,1),2*pi/3)*transB*Section(*argsB)
            section=section - sectionB 
        elif plane=='ZX':
            if isinstance(InnerContour.parts[0],Line):
                transB=translate(0,0,InnerContour.parts[0].parts[0].y)
                invB=translate(0,0,-InnerContour.parts[0].parts[0].y)
            elif isinstance(InnerContour.parts[0],Ellipse):
                transB=translate(0,0,InnerContour.parts[0].transformation._mat[1][3])
                invB=translate(0,0,-InnerContour.parts[0].transformation._mat[1][3])
            else:
                raise TypeError('Line type error!')
            argsB=[]
            for coutour in InnerContour.parts:
                if isinstance(coutour,Line):
                    coutourparts=rotate(GeVec3d(1,1,1),2*pi/3)*coutour.parts
                    for i in range(len(coutourparts)):
                        argsB.append(to_vec2(coutourparts[i]))
                elif isinstance(coutour,Ellipse) or isinstance(coutour,Arc):
                    argsB.append(invB*rotate(GeVec3d(1,1,1),2*pi/3)*coutour)
                else:
                    raise TypeError('Line type error!')
            argsB=polygon_to_ccw(argsB)
            sectionB = rotate(GeVec3d(1,1,1),-2*pi/3)*transB*Section(*argsB)
            section=section - sectionB # 
    return section

# -----------------------------------------------------------
class P3DData(Component):
    '''
    "obvious";			// 显示的
    "pivotal";			// 关键属性，触发replace
    "readonly";			// 只读
    "show";				// 几何体显示
    "group";			// 分组
    "description";	    // 描述
    '''
    def __init__(self, data=dict()):
        Component.__init__(self)
        self.name = Attr('', obvious=True)
        for k,v in data.items():
            self[k]=v
    def __setitem__(self, key, value):
        # Combine geometry in the list, using recursion
        def combineList(geo):
            for i in geo:
                if not (isinstance(i, list) or issubclass(type(i),Graphics)):
                    raise TypeError('Combine\'s parameter must be "Graphics"!')
                if isinstance(i, list):
                    combineList(i)
            geo=Combine(*geo)
            return geo
        if isinstance(value, list) :
            if len(value)>=1:
                if issubclass(type(value[0]),Graphics): #Primitives
                    value = combineList(value)
                    # value = Combine(value)
        Noumenon.__setitem__(self, key, value)

    def setup(self, key, **args):
        if key not in self:
            self[key] = Attr()
        for k, v in args.items():
            self.at(key)[k] = v
    def view(self, value):
        if isinstance(value, GeTransform):
            self[PARACMPT_KEYWORD_PREVIEW_VIEW] = value
        else:
            raise TypeError('unsupported type!')
    def set_view(self, az, el):
        '''
        az: orientation\n
        el: elevation\n
        '''
        self[PARACMPT_KEYWORD_PREVIEW_VIEW] = rotate(GeVec3d(1, 0, 0), -el) * rotate(GeVec3d(0, 1, 0), -az) * \
            rotate(GeVec3d(0, 0, 1), pi) * rotate(GeVec3d(0, 1, 0), pi) * rotate(GeVec3d(1, 0, 0), pi/2)
    def interact(self, context):
        if context['action']=='right down':
            print(1)
        elif context['action']=='left down':
            print(2)
        elif context['action']=='mouse movement':
            print(3)
        else:...

def gripMove(data:P3DData, currentGrip):
    offset = data["currentPos"] - data.transformation * data[currentGrip]
    data.transformation = translation(data[currentGrip] + offset) * data.transformation

def gripRotation(data:P3DData, currentGrip, axis, angle, origin = GeVec3d(0, 0, 0)):
    '''
    axis     旋转轴
    angle    旋转角度
    origin   原点
    '''
    data.transformation = data.transformation * translation(origin) * rotation(axis, angle) * translation(origin)

def gripInit(data:P3DData):
    # 查找所有item 看属性值是否为True
    for key, value in data.items():
        if 'bActive' in value._attr and value['bActive']:
            if (value['gripstyle'] == 'dots') :
                gripMove(data, key)                  
            elif (value['gripstyle'] == 'spin' and value['bPressed']== False):
                gripRotation(data, key,value['axis'], value['angle'])
            else :
                pass
            value['bActive'] = False
            value['bPressed'] = False
            data['curSelectedGrip'] = key
            break  

def straight_sweep(section:Section,line:Line): #直线扫掠 (temp function)
    lean_section = lambda pointY,pointX,theta:rotate(Vec3(0,0,1),atan2(pointY.y-pointX.y,pointY.x-pointX.x)+theta)
    section=rotate(Vec3(0,1,0),-pi/2)*section
    points=line.parts
    lengP=len(points)
    lineList=[] # segment
    for i in range(lengP-1):
        lineList.append([points[i],points[i+1]])
    sectionList=[translate(points[0])*lean_section(points[1],points[0],0)*section]
    for i in range(1,lengP-1):
        theta=get_angle_of_two_vectors(lineList[i-1],lineList[i])/2
        matrix=GeTransform([[1/cos(theta),0,0,0],
                            [0,1/cos(theta),0,0],
                            [0,0,1,0]])
        sectioni=translate(points[i])*matrix*lean_section(points[i],points[i-1],theta)*section
        sectionList.append(sectioni)
    sectionList.append(translate(points[lengP-1])*lean_section(points[lengP-1],points[lengP-2],0)*section)
    curveloft=Loft(*sectionList)
    curveloft.smooth=True
    return curveloft

