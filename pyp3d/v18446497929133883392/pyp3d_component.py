# Copyright (C), 2019-2028, Beijing GLory PKPM Tech. Co., Ltd.
# Brief: PKPM-BIMBase Python二次开发SDK与参数化组件功能。
# Author: YouQi akingse
# Date: 2021/08/07
from .pyp3d_convention import *
from .pyp3d_data import *
from .pyp3d_matrix import *
from .pyp3d_calculation import *
import copy, math, sys, time
from math import *
set_global_variable('is_script_to_josn', False)

class Style(Noumenon):
    def __init__(self):
        Noumenon.__init__(self)
        self.transformation = GeTransform()
        self.version = '0'
        self.representation = 'Style'
    @property
    def representation(self):
        return self[PARACMPT_KEYWORD_REPRESENTATION]
    @representation.setter
    def representation(self, name):
        if not isinstance(name, str): raise TypeError('improper type!')
        self[PARACMPT_KEYWORD_REPRESENTATION] = name
    @property
    def version(self):
        return self[PARACMPT_KEYWORD_REPRESENTATION]
    @version.setter
    def version(self, name):
        if not isinstance(name, str): raise TypeError('improper type!')
        self[PARACMPT_STYLE_VERSION] = name

class Symbology(Style):
    def __init__(self, color=P3DColorDef(0.5,0.5,0.5,1.0)):
        Style.__init__(self)
        self.representation = 'Symbology'
        self.color = color
    @property
    def color(self):
        return self[PARACMPT_SYMBOLOGY_COLOR]
    @color.setter
    def color(self, clr):
        self[PARACMPT_SYMBOLOGY_COLOR] = clr

class Material(Style):
    def __init__(self, name=''):
        Style.__init__(self)
        self.representation = 'Material'
        self.name = name
    @property
    def name(self):
        return self[PARACMPT_MATERIAL_NAME]
    @name.setter
    def name(self, name):
        self[PARACMPT_MATERIAL_NAME] = name

class Font(Style):
    def __init__(self):
        Style.__init__(self)
        self.representation = 'Font'
        self.size = 1
        self.horzscale = 1
        self.vertscale = 1
    @property
    def size(self):
        return self[PARACMPT_FONT_SIZE]
    @size.setter
    def size(self, size):
        self[PARACMPT_FONT_SIZE] = float(size)
    @property
    def horzscale(self):
        return self[PARACMPT_FONT_HORZ_SCALE]
    @horzscale.setter
    def horzscale(self, size):
        self[PARACMPT_FONT_HORZ_SCALE] = float(size)
    @property
    def vertscale(self):
        return self[PARACMPT_FONT_VERT_SCALE]
    @vertscale.setter
    def vertscale(self, size):
        self[PARACMPT_FONT_VERT_SCALE] = float(size)
    @property
    def font_name(self):
        return self[PARACMPT_FONT_NAME]
    @font_name.setter
    def font_name(self, name):
        self[PARACMPT_FONT_NAME] = str(name)
        self[PARACMPT_FONT_TYPE] = "TrueType"

class Graphics(Noumenon):
    def __init__(self):
        Noumenon.__init__(self)
        self.transformation = GeTransform()
        self[PARACMPT_KEYWORD_TAIJI] = True
        self.representation = 'Graphics'
    def __rmul__(self, a):
        if not isinstance(a, GeTransform): raise TypeError('improper type!')
        c = copy.deepcopy(self)
        c.transformation = a * self.transformation
        return c
    def __neg__(self):
        c = copy.deepcopy(self)
        c[PARACMPT_KEYWORD_TAIJI] = not self[PARACMPT_KEYWORD_TAIJI]
        return c
    def __abs__(self):
        c = copy.deepcopy(self)
        c[PARACMPT_KEYWORD_TAIJI] = True
        return c
    def __add__(self, other): return other.__radd__(self)
    def __radd__(self, other): return Fusion(copy.deepcopy(other), copy.deepcopy(self))
    def __sub__(self, other): return other.__rsub__(self)
    def __rsub__(self, other): return Fusion(copy.deepcopy(other), -copy.deepcopy(self))
    @property
    def representation(self):
        return self[PARACMPT_KEYWORD_REPRESENTATION]
    @representation.setter
    def representation(self, name):
        if not isinstance(name, str): raise TypeError('improper type!')
        self[PARACMPT_KEYWORD_REPRESENTATION] = name
    @property
    def transformation(self):
        return self[PARACMPT_KEYWORD_TRANSFORMATION]
    @transformation.setter
    def transformation(self, val):
        if not isinstance(val, GeTransform): raise TypeError('improper type!')
        self[PARACMPT_KEYWORD_TRANSFORMATION] = Attr(val)

class Component(Graphics):
    def __init__(self):
        Graphics.__init__(self)
        self[PARACMPT_KEYWORD_SOURCE] = ''
        self.schemaName, self.className, self.representation = 'PBM_CoreModel', 'BPGraphicElementParametricComponent', 'Component'
    def replace(self):
        if not PARACMPT_KEYWORD_REPLACE in self:
            return
        if isinstance(self[PARACMPT_KEYWORD_REPLACE], UnifiedFunction): 
            self[PARACMPT_KEYWORD_REPLACE].call(self)
        elif isinstance(self[PARACMPT_KEYWORD_REPLACE], FunctionType):
            self[PARACMPT_KEYWORD_REPLACE](self)
        else:
            raise TypeError('Type Error!')
    def interact(self):...
    @property
    def schemaName(self):
        return self[PARACMPT_KEYWORD_SCHEMA_NAME]
    @schemaName.setter
    def schemaName(self, val):
        self[PARACMPT_KEYWORD_SCHEMA_NAME] = val
    @property
    def className(self):
        return self[PARACMPT_KEYWORD_CLASS_NAME]
    @className.setter
    def className(self, val):
        self[PARACMPT_KEYWORD_CLASS_NAME] = val
    @property
    def name(self):
        return self[PARACMPT_KEYWORD_NAME]
    @name.setter
    def name(self, val):
        self[PARACMPT_KEYWORD_NAME] = val

class Primitives(Graphics):
    def __init__(self):
        Graphics.__init__(self)
        self[PARACMPT_KEYWORD_STYLE], self.extractGraphics, self.representation = Symbology(), UnifiedFunction('',''), 'Primitives'
    def material(self,name):
        self[PARACMPT_KEYWORD_STYLE] = Material(name)
    def color(self, *args):
        if len(args)==0 :
            color = P3DColorDef(0.5,0.5,0.5,1)
        elif len(args)==1 and isinstance(args[0],(list,tuple)):
            if len(args[0])==4:
                color = P3DColorDef(args[0][0],args[0][1],args[0][2],args[0][3])
            elif len(args[0])==3:
                color = P3DColorDef(args[0][0],args[0][1],args[0][2],1)
        elif len(args)==2 and isinstance(args[0],(list,tuple)) and isinstance(args[1],(int,float)):
            color = P3DColorDef(args[0][0],args[0][1],args[0][2],args[1])
        elif len(args)==3 and isinstance(args[0]+args[1]+args[2],(int,float)):
            color = P3DColorDef(args[0],args[1],args[2],1)
        elif len(args)==4 and isinstance(args[0]+args[1]+args[2]+args[3],(int,float)):
            color = P3DColorDef(args[0],args[1],args[2],args[3])
        else:
            TypeError('please input proper RGBA value!')
        self[PARACMPT_KEYWORD_STYLE].color = color
        return self
    @property
    def extractGraphics(self):
        return self[PARACMPT_KEYWORD_EXTRACT_GRAPHICS]
    @extractGraphics.setter
    def extractGraphics(self, val):
        if not isinstance(val, UnifiedFunction): raise TypeError('improper type!')
        self[PARACMPT_KEYWORD_EXTRACT_GRAPHICS] = val

class Point(Primitives):
    def __init__(self, *args):
        Primitives.__init__(self)
        self.representation = 'Point'
        self.extractGraphics = UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_POINT_TO_GRAPHICS)
        if len(args) == 0:
            self.x = 0
            self.y = 0
            self.z = 0
        elif len(args) == 1 and is_num(args):
            if len(args[0]) == 2:
                self.x = args[0][0]
                self.y = args[0][1]
                self.z = 0
            elif len(args[0]) == 3:
                self.x = args[0][0]
                self.y = args[0][1]
                self.z = args[0][2]
            else:
                raise ValueError('Point parameter error!')
        elif len(args) == 2 and is_num(args):
            self.x =float(args[0])
            self.y =float(args[1])
        elif len(args) == 3 and is_num(args):
            self.x =float(args[0])
            self.y =float(args[1])
            self.z =float(args[2])
        else:
            raise ValueError('Point parameter error!')
    @property
    def x(self): return self[PARACMPT_KEYWORD_TRANSFORMATION]._mat[0][3]
    @x.setter
    def x(self, val): self[PARACMPT_KEYWORD_TRANSFORMATION]._mat[0][3] = float(val)
    @property
    def y(self): return self[PARACMPT_KEYWORD_TRANSFORMATION]._mat[1][3]
    @y.setter
    def y(self, val): self[PARACMPT_KEYWORD_TRANSFORMATION]._mat[1][3] = float(val)
    @property
    def z(self): return self[PARACMPT_KEYWORD_TRANSFORMATION]._mat[2][3]
    @z.setter
    def z(self, val): self[PARACMPT_KEYWORD_TRANSFORMATION]._mat[2][3] = float(val)

class Arc(Primitives):
    def __init__(self, *args):
        Primitives.__init__(self)
        self.representation = 'Arc'
        self.extractGraphics = UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_ARC_TO_GRAPHICS)
        if len(args) == 0:
            self.scope = 2.0 * pi
        elif len(args) == 1 and is_num(args):
            self.scope = float(args[0])
        elif len(args) == 3 and is_all_vec(args):
            # self.pointStart=args[0]
            # self.pointEnd=args[2]
            if norm(args[2]-args[0])<1e-10 and norm(args[1]-args[0])>1e-10:# 3点直径画圆，默认XoY平面
                self.scope = 2*pi
                R=norm(args[1]-args[0])/2
                self.transformation=translate(0.5*(args[0]+args[1]))*scale(R) #nonsupport division
            else:
                if is_all_vec2(args):
                    args=to_vec3(args)
                ptt=points_to_trans(args)
                transM=ptt[0]
                invM=ptt[1]
                point1=invM*(args[1]-args[0])
                point2=invM*(args[2]-args[0])
                x1=0 #points[0].x
                y1=0 #points[0].y
                x2=point1.x
                y2=point1.y
                x3=point2.x
                y3=point2.y
                yc=((x3-x2)*(x3**2+y3**2-x1**2-y1**2)-(x3-x1)*(x3**2+y3**2-x2**2-y2**2)) / (2*(x3-x2)*(y3-y1)-2*(x3-x1)*(y3-y2))
                xc=((y3-y2)*(x3**2+y3**2-x1**2-y1**2)-(y3-y1)*(x3**2+y3**2-x2**2-y2**2)) / (2*(y3-y2)*(x3-x1)-2*(y3-y1)*(x3-x2))
                R=sqrt((xc-x1)**2+(yc-y1)**2)
                self.transformation=transM*translate(xc,yc)*scale(R)*rotate(atanp(y1-yc,x1-xc))
                inAngle=posi(atanp(y3-yc,x3-xc)-atanp(y1-yc,x1-xc))
                self.scope = inAngle
        else:
            raise ValueError('improper parameters!')
        # if is_same_direction(GeVec3d(self.transformation._mat[0][2],self.transformation._mat[1][2],self.transformation._mat[2][2]), GeVec3d(0, 0, 1)):
        #     self.ccw=True #is arc counter clockwise, only in XoY plane work
        # else:
        #     self.ccw=False
    @property
    def scope(self):
        return self[PARACMPT_ARC_SCOPE]
    @scope.setter
    def scope(self, val):
        self[PARACMPT_ARC_SCOPE] = float(val)
    @property
    def pointCenter(self):
        return get_translate_para(self.transformation)
    @property
    def pointStart(self):
        return self.transformation*GeVec3d(1, 0, 0)
    @property
    def pointEnd(self):
        return self.transformation*GeVec3d(cos(self.scope), sin(self.scope), 0)
    @property
    def vectorNormal(self): #圆弧法向量
        vectorN=GeVec3d(self.transformation._mat[0][2],self.transformation._mat[1][2],self.transformation._mat[2][2])
        return unitize(vectorN)
    @property
    def vectorTangents(self): #起点切向量
        vectorZ=self.vectorNormal
        vectorStart=unitize(self.pointStart-self.pointCenter)
        vectorTs=cross(vectorZ, vectorStart)
        return unitize(vectorTs)
    @property
    def vectorTangente(self): #终点切向量
        vectorZ=self.vectorNormal
        vectorEnd=unitize(self.pointEnd-self.pointCenter)
        vectorTe=cross(vectorZ, vectorEnd)
        return unitize(vectorTe)

class Line(Primitives):
    def __init__(self, *args):
        Primitives.__init__(self)
        self.representation = 'Line'
        self.extractGraphics = UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_LINE_TO_GRAPHICS)
        if len(args)==1 and isinstance(args[0], (list,tuple)): 
            self.parts = list(args[0])
        else:
            self.parts = list(args)
    def append(self, value):
        self[PARACMPT_LINE_PARTS].append(value)
    @property
    def parts(self):
        return self[PARACMPT_LINE_PARTS]
    @parts.setter
    def parts(self, val):
        if not isinstance(val, list): raise TypeError('Line parameter error!')
        idf = lambda x: isinstance(x, (GeVec2d,GeVec3d)) or (isinstance(x, Noumenon)and PARACMPT_KEYWORD_TRANSFORMATION in x)
        if not all(map(idf, val)): raise TypeError('Line parameter error!')
        self[PARACMPT_LINE_PARTS] = val

class Section(Primitives):
    def __init__(self, *args):
        Primitives.__init__(self)
        self.representation = 'Section'
        self.extractGraphics = UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_SECTION_TO_GRAPHICS)
        if len(args)==1 and isinstance(args[0], (list, tuple)): 
            self.parts = list(args[0])
        else:
            self.parts = list(args)
        self.close = True
        for value in self.parts:
            if isinstance(value, GeVec2d):
                continue
            elif isinstance(value, Arc): 
                # axisZi=GeVec3d(value.transformation._mat[0][2],value.transformation._mat[1][2],value.transformation._mat[2][2])
                axisZi=get_matrix_axisz(value.transformation)
                if abs(value.transformation._mat[2][3])>1e-10 or (is_same_direction(axisZi,GeVec3d(0,0,1))==False):
                    raise TypeError('Section parts arc error!')
            elif isinstance(value, GeVec3d):
                if abs(value.z)>1e-10:
                    raise TypeError('Section parts vec3 error!')
            elif isinstance(value, Line):
                if not self.is_two_dimensional(value):
                    raise TypeError('Section parts line error!')
            else:
                raise TypeError('Section parts parameter error!')
    def append(self, value):
        t=type(value)
        if isinstance(value, GeVec2d):
            pass
        elif isinstance(value, Arc): 
            # axisZi=GeVec3d(value.transformation._mat[0][2],value.transformation._mat[1][2],value.transformation._mat[2][2])
            axisZi=get_matrix_axisz(value.transformation)
            if abs(value.transformation._mat[2][3])>1e-10 or abs(abs(dot(unitize(axisZi),GeVec3d(0,0,1)))-1)>1e-10:
                raise TypeError('Section append arc error!')
        elif isinstance(value, GeVec3d):
            if abs(value.z)>1e-10:
                raise TypeError('Section append vec3 error!')
        elif isinstance(value, Line):
            if not self.is_two_dimensional(value):
                raise TypeError('Section append line error!')
        else:
            raise TypeError('Section append parameter error!')
        self[PARACMPT_SECTION_PARTS].append(value)
    def is_two_dimensional(self,*args): #判断Line Arc在XoY二维面或三维空间
        '''
        dimension judge, 2-dimension==True, 3-dimension==False
        if locate in XoY plane return True
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
                axisZi=GeVec3d(value.transformation._mat[0][2],value.transformation._mat[1][2],value.transformation._mat[2][2])
                if abs(value.transformation._mat[2][3])>1e-10 or abs(abs(dot(unitize(axisZi),GeVec3d(0,0,1)))-1)>1e-10:
                    dimension = False
                    break
            elif isinstance(value, GeVec3d):
                if abs(value.z)>1e-10:
                    dimension = False
                    break
            elif isinstance(value, Line):
                dimension = self.is_two_dimensional(value.parts) # recursion
            else:
                raise TypeError('Line parameter error!')
        return dimension
    @property
    def parts(self):
        return self[PARACMPT_SECTION_PARTS]
    @parts.setter
    def parts(self, val):
        if not isinstance(val, list): raise TypeError('Section parameter error!')
        idf = lambda x: isinstance(x, (GeVec2d,GeVec3d)) or (isinstance(x, Noumenon)and PARACMPT_KEYWORD_TRANSFORMATION in x)
        if not all(map(idf, val)): raise TypeError('')
        self[PARACMPT_SECTION_PARTS] = val
    @property
    def close(self):
        return self[PARACMPT_SECTION_COLSE]
    @close.setter
    def close(self, val):
        if not isinstance(val, bool): raise TypeError('improper type!')
        self[PARACMPT_SECTION_COLSE] = val

class Sphere(Primitives):
    def __init__(self, center:GeVec3d=GeVec3d(0,0,0), radius:float=1.0):
        Primitives.__init__(self)
        self.representation = 'Sphere'
        self.extractGraphics = UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_SPHERE_TO_GRAPHICS)
        self.transformation = translate(center) * scale(radius)
        self.lower = 0.0 # zenith angle
        self.upper = pi
    @property
    def center(self):
        return GeVec3d(self.transformation._mat[0][3], self.transformation._mat[1][3], self.transformation._mat[2][3])
    @center.setter
    def center(self, value:GeVec3d):
        self.transformation._mat[0][3] = value.x
        self.transformation._mat[1][3] = value.y
        self.transformation._mat[2][3] = value.z
    @property
    def radius(self):     
        return self.transformation._mat[0][0]
    @radius.setter
    def radius(self, value):
        self.transformation._mat[0][0] = value
        self.transformation._mat[1][1] = value
        self.transformation._mat[2][2] = value
    @property
    def upper(self):
        return self[PARACMPT_SPHERE_UPPER]
    @upper.setter
    def upper(self, value):
        self[PARACMPT_SPHERE_UPPER] = float(value)
    @property
    def lower(self):
        return self[PARACMPT_SPHERE_LOWER]
    @lower.setter
    def lower(self, value):
        self[PARACMPT_SPHERE_LOWER] = float(value)

class Cube(Primitives):
    def __init__(self):
        Primitives.__init__(self)
        self.representation = 'Cube'
        self.extractGraphics = UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_CUBE_TO_GRAPHICS)

class Loft(Primitives):
    def __init__(self, *args):
        Primitives.__init__(self)
        self.representation = 'Loft'
        self.extractGraphics = UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_LOFT_TO_GRAPHICS)
        if len(args)==1 and isinstance(args[0], (list, tuple)): 
            self.parts = list(args[0])
        else:
            self.parts = list(args)
        self.smooth = False
    @property
    def parts(self):
        return self[PARACMPT_LOFT_PARTS]
    @parts.setter
    def parts(self, val):
        if not isinstance(val, list): raise TypeError('improper type!')
        # if not all(map(lambda x: isinstance(x, Section), val)): raise TypeError('')
        self[PARACMPT_LOFT_PARTS] = val
    @property
    def smooth(self):
        return self[PARACMPT_LOFT_SMOOTH]
    @smooth.setter
    def smooth(self, val):
        if not isinstance(val, bool): raise TypeError('improper type!')
        self[PARACMPT_LOFT_SMOOTH] = val

class Sweep(Primitives):
    def __init__(self, section=Section(), trajectory=Line()):
        Primitives.__init__(self)
        self.representation = 'Sweep'
        self.extractGraphics = UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_SWEEP_TO_GRAPHICS)
        self.section = section
        self.trajectory = trajectory
        self.smooth = False
    @property
    def section(self):
        return self[PARACMPT_SWEEP_SECTION]
    @section.setter
    def section(self, val):
        self[PARACMPT_SWEEP_SECTION] = val
    @property
    def trajectory(self):
        return self[PARACMPT_SWEEP_TRAJECTORY]
    @trajectory.setter
    def trajectory(self, val):
        self[PARACMPT_SWEEP_TRAJECTORY] = val
    @property
    def smooth(self):
        return self[PARACMPT_SWEEP_SMOOTH]
    @smooth.setter
    def smooth(self, val):
        if not isinstance(val, bool): raise TypeError('improper type!')
        self[PARACMPT_SWEEP_SMOOTH] = val

class Text(Primitives):
    def __init__(self, text='', *args):
        Primitives.__init__(self)
        self.representation = 'Text'
        self.extractGraphics = UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_TEXT_TO_GRAPHICS)
        self.text = text
        self.font = Font() * Symbology()
        self.font.size = 1
        if  len(args) == 0:
            self.horzscale = 1.0
            self.vertscale = 1.0
        elif len(args)==1 :
            if(isinstance(args[0], (int, float))):
                self.horzscale = float(args[0])
            elif isinstance(args[0], str):
                self.font_name = args[0]
            else:
                raise ValueError('the input value isnot number or "fontName" isnot string')
        elif len(args)==2 and (isinstance(args[0], (int,float)) and isinstance(args[1], (int,float))):
            self.horzscale = float(args[0])
            self.vertscale = float(args[1])
        elif len(args)==3 and (isinstance(args[0], (int,float))) and isinstance(args[1], (int, float)) and isinstance(args[2], str):
            self.horzscale = float(args[0])
            self.vertscale = float(args[1])
            self.font_name = str(args[2])
        else:
            raise ValueError('the input value isnot number or "fontName" isnot string')
    @property
    def text(self):
        return self[PARACMPT_TEXT_TEXT]
    @text.setter
    def text(self, val):
        self[PARACMPT_TEXT_TEXT] = val
    @property
    def font(self):
        return self[PARACMPT_KEYWORD_STYLE]
    @font.setter
    def font(self, val):
        self[PARACMPT_KEYWORD_STYLE] = val
    @property
    def size(self):
        return self.font[PARACMPT_FONT_SIZE]
    @size.setter
    def size(self, size):
        self.font[PARACMPT_FONT_SIZE] = float(size)
    @property
    def horzscale(self):
        return self.font[PARACMPT_FONT_HORZ_SCALE]
    @horzscale.setter
    def horzscale(self, size):
        self.font[PARACMPT_FONT_HORZ_SCALE] = float(size)
    @property
    def vertscale(self):
        return self.font[PARACMPT_FONT_VERT_SCALE]
    @vertscale.setter
    def vertscale(self, size):
        self.font[PARACMPT_FONT_VERT_SCALE] = float(size)
    @property
    def font_name(self):
        return self.font[PARACMPT_FONT_NAME]
    @font_name.setter
    def font_name(self, name):
        self.font[PARACMPT_FONT_NAME] = str(name)
        self.font[PARACMPT_FONT_TYPE] = "TrueType"

class Combine(Primitives):
    def __init__(self, *args):
        Primitives.__init__(self)
        self.representation = 'Combine'
        self.extractGraphics = UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_COMBINE_TO_GRAPHICS)
        args=list(args)
        for i in range(len(args)):
            if isinstance(args[i],list) or isinstance(args[i],tuple):
                args[i]=Combine(*args[i]) # using recursion
            elif not issubclass(type(args[i]),Graphics): #Primitives
                raise TypeError('please input proper "Combine(Graphics)"')
        self.parts = list(args)
    def color(self, *argscolor):
        if len(argscolor)==0 :
            color = P3DColorDef(0.5,0.5,0.5,1)
        elif len(argscolor)==1 and isinstance(argscolor[0],(list,tuple)):
            if len(argscolor[0])==4:
                color = P3DColorDef(argscolor[0][0],argscolor[0][1],argscolor[0][2],argscolor[0][3])
            elif len(argscolor[0])==3:
                color = P3DColorDef(argscolor[0][0],argscolor[0][1],argscolor[0][2],1)
        elif len(argscolor)==2 and isinstance(argscolor[0],(list,tuple)) and (isinstance(argscolor[1],(int,float))):
            color = P3DColorDef(argscolor[0][0],argscolor[0][1],argscolor[0][2],argscolor[1])
        elif len(argscolor)==3 and isinstance(argscolor[0]+argscolor[1]+argscolor[2],(int,float)):
            color = P3DColorDef(argscolor[0],argscolor[1],argscolor[2],1)
        elif len(argscolor)==4 and isinstance(argscolor[0]+argscolor[1]+argscolor[2]+argscolor[3],(int,float)):
            color = P3DColorDef(argscolor[0],argscolor[1],argscolor[2],argscolor[3])
        else:
            TypeError('please input proper RGBA value!')

        def combineColor(geo):
            if issubclass(type(geo),Primitives) and (not isinstance(geo,Combine)):
                geo[PARACMPT_KEYWORD_STYLE].color = color
            else: #elif listGeo(geo):
                for i in geo.parts:
                    combineColor(i)
        # using recursion
        for i in self.parts:
            combineColor(i) 
        return self
    @property
    def parts(self):
        return self[PARACMPT_COMBINE_PARTS]
    @parts.setter
    def parts(self, val):
        self[PARACMPT_COMBINE_PARTS] = val
    def append(self, other):
        self.parts.append(other)
    def pop(self, index: int = ...):
        self.parts.pop(index)

class Fusion(Primitives):
    def __init__(self, *args):
        Primitives.__init__(self)
        self.representation = 'Fusion'
        self.extractGraphics = UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_FUSION_TO_GRAPHICS)
        args=list(args)
        for i in range(len(args)):
            if isinstance(args[i],(list,tuple)):
                args[i]=Combine(*args[i])
        self.parts = list(args)
    def __add__(self, other):
        res = copy.deepcopy(self) 
        for i in res.parts:
            i.transformation = res.transformation * i.transformation
        res.transformation = GeTransform()
        res.parts.append(other)
        return res
    def __sub__(self, other):
        res = copy.deepcopy(self)
        for i in res.parts:
            i.transformation = res.transformation * i.transformation
        res.transformation = GeTransform()
        res.parts.append(-other)
        return res
    @property
    def parts(self):
        return self[PARACMPT_FUSION_PARTS]
    @parts.setter
    def parts(self, val):
        # limited boolean section,inclued front and back
        if len(val)>=1 and isinstance(val[0],Section):
            dataM=val[0].transformation
            vectorX=get_matrix_axisx(dataM)
            vectorY=get_matrix_axisy(dataM)
            vectorZ=get_matrix_axisz(dataM)
            for i in range(1,len(val)):
                matrix=val[i].transformation
                vectorZi=get_matrix_axisz(matrix)
                isParallel=is_same_direction(vectorZ,vectorZi)
                originRela=get_translate_para(dataM)-get_translate_para(dataM)
                if abs(dot(vectorZ,originRela))<1e-10 and isParallel:
                    continue
                if is_same_direction(cross(vectorX,vectorY),cross(vectorX,vectorZ)):
                    continue
                else:
                    raise ValueError('the boolean section must in same plane!')
        self[PARACMPT_FUSION_PARTS] = val

class Intersect(Primitives):
    def __init__(self, *args):
        Primitives.__init__(self)
        self.representation = 'Intersect'
        self.extractGraphics = UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_INTERSECT_TO_GRAPHICS)
        args=list(args)
        for i in range(len(args)):
            if isinstance(args[i],(list,tuple)):
                args[i]=Combine(*args[i])
        self.parts = list(args)
    @property
    def parts(self):
        return self[PARACMPT_INTERSECT_PARTS]
    @parts.setter
    def parts(self, val):
        self[PARACMPT_INTERSECT_PARTS] = val

class Array(Primitives):
    def __init__(self, ontology=None, *args):
        Primitives.__init__(self)
        self.representation = 'Array'
        self.extractGraphics = UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_ARRAY_TO_GRAPHICS)
        self.ontology = ontology
        self.parts = list(args)
    @property
    def ontology(self):
        return self[PARACMPT_ARRAY_ONTOLOGY]
    @ontology.setter
    def ontology(self, val):
        self[PARACMPT_ARRAY_ONTOLOGY] = val
    @property
    def parts(self):
        return self[PARACMPT_ARRAY_PARTS]
    @parts.setter
    def parts(self, val):
        if not isinstance(val, list): raise TypeError('')
        self[PARACMPT_ARRAY_PARTS] = val
    def append(self, other):
        self.parts.append(other)
    def pop(self, index: int = ...):
        self.parts.pop(index)

# new curve class
class SplineCurve(Primitives): # B Spline Curve
    def __init__(self, controlPoint:list, orderK:int, discreteNum:int, splineType='normal'):
        '''
        splineType      类型
        normal          deCasteljau递推算法
        uniform         均匀B样条
        quasi           准均匀B样条
        piecewise       分段B样条
        '''
        Primitives.__init__(self)
        self.representation = 'SplineCurve'
        self.extractGraphics = UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_SPLINECURVE_TO_GRAPHICS)
        if all(isinstance(i, GeVec3d) for i in controlPoint):
            self.transformation=points_to_trans(controlPoint)[0]
            invA=points_to_trans(controlPoint)[1]
            controlPoint_0=copy.deepcopy(controlPoint[0]) #deepcopy
            for i in range(len(controlPoint)):
                point=invA*(controlPoint[i]-controlPoint_0)
                controlPoint[i]=to_vec2(point)
        self.points=controlPoint
        self.k=orderK
        self.num=discreteNum
        self.type=splineType
        n=len(controlPoint)-1
        if splineType==2:
            if not n+1-orderK>=0:
                raise TypeError('len(controlPoint) cannot equal k!')
        if splineType==3:
            if n%orderK != 0:
                raise ValueError('piecewise parameter error!')
    @property
    def k(self):
        return self[PARACMPT_SPLINECURVE_K]
    @k.setter
    def k(self, val):
        self[PARACMPT_SPLINECURVE_K] = val
    @property
    def num(self):
        return self[PARACMPT_SPLINECURVE_NUM]
    @num.setter
    def num(self, val):
        self[PARACMPT_SPLINECURVE_NUM] = val
    @property
    def type(self):
        return self[PARACMPT_SPLINECURVE_TYPE]
    @type.setter
    def type(self, val):
        if val<0 or val>3:
            raise TypeError('SplineCurve type error!')
        self[PARACMPT_SPLINECURVE_TYPE] = val
    @property
    def points(self):
        return self[PARACMPT_SPLINECURVE_POINTS]
    @points.setter
    def points(self, val):
        if not isinstance(val, list): raise TypeError('SplineCurve parameter error!')
        if not all(isinstance(i, (GeVec2d,GeVec3d)) for i in val): 
            raise TypeError('SplineCurve parameter error!')
        self[PARACMPT_SPLINECURVE_POINTS] = val

class ParametricEquation(Primitives): # Parametric Equation
    def __init__(self, step_list:list=None):
        Primitives.__init__(self)
        self.representation = 'ParametricEquation'
        self.extractGraphics = UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_PARAMETRICEQUATION_TO_GRAPHICS)
        self.fun = UnifiedFunction()
        self.t=step_list
    @property
    def fun(self):
        return self[PARACMPT_PARAMETRICEQUATION_FUN]
    @fun.setter
    def fun(self, val):
        self[PARACMPT_PARAMETRICEQUATION_FUN] = val
    @property
    def t(self):
        return self[PARACMPT_PARAMETRICEQUATION_T]
    @t.setter
    def t(self, val):
        if not isinstance(val, list): raise TypeError('ParametricEquation parameter error!')
        if not all(isinstance(i, (int,float)) for i in val): 
            raise TypeError('ParametricEquation parameter error!')
        self[PARACMPT_PARAMETRICEQUATION_T] = val
    


