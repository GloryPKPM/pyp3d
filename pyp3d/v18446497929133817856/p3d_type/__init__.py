# Copyright (C), 2019-2028, Beijing GLory PKPM Tech. Co., Ltd.
# Brief: 
# Author: YouQi
# Date: 2021/05/06
from ..ParametricComponentConvention import *
import copy

class P3DEntityId(BufferStackBase):
    def __init__(self): self._ModelId, self._ElementId = 0, 0
    def _push_to(self, bs): 
        bs.push(self._ModelId, self._ElementId)
    def _pop_from(self, bs): self._ElementId, self._ModelId = bs.pop(), bs.pop()

class P3DModelId(BufferStackBase):
    def __init__(self): self._ModelId =  0
    def _push_to(self, bs): 
        bs.push(self._ModelId)
    def _pop_from(self, bs):  self._ModelId =  bs.pop()  

class P3DInstanceKey(BufferStackBase):
    def __init__(self): self._PClassId, self._P3DInstanceId = 0, 0
    def _push_to(self, bs): bs.push(self._PClassId, self._P3DInstanceId)
    def _pop_from(self, bs): self._P3DInstanceId, self._PClassId = bs.pop(), bs.pop()
    


class GeTransform(BufferStackBase):
    def __init__(self, mat = [[1,0,0,0],[0,1,0,0],[0,0,1,0]]): 
        self._mat = [[float(mat[i][ii]) for ii in range(4)] for i in range(3)]
    def __str__(self): return str(self._mat)
    def __mul__(self, b): 
        if isinstance(b, list) or isinstance(b, tuple): return [self * i for i in b]
        else: return b.__rmul__(self)
    def __rmul__(self, a):
        if isinstance(a, GeTransform):
            return GeTransform([[sum([a._mat[k][i]*self._mat[i][j] for i in range(3)]) + (a._mat[k][3] if j==3 else 0.0) for j in range(4)] for k in range(3)])
        elif isinstance(a, int) or isinstance(a, float):
            return GeTransform([[a*self._mat[j][i] for i in range(4)] for j in range(3)])
        else:
            raise TypeError('__mul__ error type!')
    def _push_to(self, buf:BufferStack): [[buf.push(self._mat[2-i][3-j]) for j in range(4)] for i in range(3)]
    def _pop_from(self, buf:BufferStack): self._mat = [[buf.pop() for _ in range(4)] for _ in range(3)]

class GeVec3d(BufferStackBase):
    def __init__(self,*args): 
        if len(args)==0:
            self.x, self.y, self.z = 0,0,0
        elif len(args)==3:
            self.x, self.y, self.z = args[0], args[1], args[2]
        elif len(args)==2:
            self.x, self.y, self.z = args[0], args[1], 0
        elif len(args)==1 and (isinstance(args[0],list) or isinstance(args[0],tuple)) and len(args[0])==3:
            self.x, self.y, self.z = args[0][0], args[0][1], args[0][2]
        elif len(args)==1 and (isinstance(args[0],list) or isinstance(args[0],tuple)) and len(args[0])==2:
            self.x, self.y, self.z = args[0][0], args[0][1], 0
        else:
            raise TypeError('improper parameter!')
    def __str__(self): return '({0}, {1}, {2})'.format(self.x,self.y,self.z)
    def __rmul__(self, a):
        if isinstance(a, GeTransform): return GeVec3d(*[a._mat[i][0]*self.x + a._mat[i][1]*self.y + a._mat[i][2]*self.z + a._mat[i][3] for i in range(3)])
        elif isinstance(a, float) or isinstance(a, int): return GeVec3d(a*self.x, a*self.y, a*self.z)
        else: raise TypeError('input error type!')
    def __neg__(self):
        c = copy.deepcopy(self)
        c.x, c.y, c.z = -self.x, -self.y, -self.z
        return c
    def __mul__(self, b):
        if isinstance(b, float) or isinstance(b, int):return GeVec3d(self.x * b,self.y * b,self.z * b) 
        else: raise TypeError('improper parameter!')
    def __add__(self, b):
        if isinstance(b, GeVec3d): return GeVec3d(self.x+b.x, self.y+b.y, self.z+b.z) 
        else: raise TypeError('improper parameter!')
    def __radd__(self, a):
        if isinstance(a, GeVec3d): return GeVec3d(a.x+self.x, a.y+self.y, a.z+self.z)  
        else: raise TypeError('improper parameter!')
    def __sub__(self, b):
        if isinstance(b, GeVec3d): return GeVec3d(self.x-b.x, self.y-b.y, self.z-b.z)  
        else: raise TypeError('improper parameter!')
    def __rsub__(self, a):
        if isinstance(a, GeVec3d): return GeVec3d(a.x-self.x, a.y-self.y, a.z-self.z)
        else: raise TypeError('improper parameter!')
    def _push_to(self, buf:BufferStack): buf.push(self.x, self.y, self.z)
    def _pop_from(self, buf:BufferStack): self.z, self.y, self.x = buf.pop(), buf.pop(), buf.pop()
    @property
    def x(self): return self._x
    @x.setter
    def x(self, val): self._x = float(val)
    @property
    def y(self): return self._y
    @y.setter
    def y(self, val): self._y = float(val)
    @property
    def z(self): return self._z
    @z.setter
    def z(self, val): self._z = float(val)

class GeVec2d(BufferStackBase):
    def __init__(self,*args): #self.x, self.y = x, y
        if len(args)==0:
            self.x, self.y = 0,0
        elif len(args)==2:
            self.x, self.y = args[0], args[1]
        elif len(args)==1 and (isinstance(args[0],list) or isinstance(args[0],tuple)) and len(args[0])==2:
            self.x, self.y = args[0][0], args[0][1]
        else:
            raise TypeError('improper parameter!')
    def __str__(self): return '({0}, {1})'.format(self.x,self.y)
    def __rmul__(self, a):
        if isinstance(a, GeTransform): return GeVec2d(*[a._mat[i][0]*self.x + a._mat[i][1]*self.y + a._mat[i][3] for i in range(2)])
        elif isinstance(a, float) or isinstance(a, int): return GeVec2d(a*self.x, a*self.y)
        else: raise TypeError('input error type!')
    def __neg__(self):
        c = copy.deepcopy(self)
        c.x, c.y = -self.x, -self.y
        return c
    def __mul__(self, b):
        if isinstance(b, float) or isinstance(b, int):return GeVec2d(self.x * b,self.y * b) 
        else: raise TypeError('improper parameter!')
    def __add__(self, b):
        if isinstance(b, GeVec2d): return GeVec2d(self.x+b.x, self.y+b.y) 
        else: raise TypeError('improper parameter!')
    def __radd__(self, a):
        if isinstance(a, GeVec2d): return GeVec2d(a.x+self.x, a.y+self.y)  
        else: raise TypeError('improper parameter!')
    def __sub__(self, b):
        if isinstance(b, GeVec2d): return GeVec2d(self.x-b.x, self.y-b.y)  
        else: raise TypeError('improper parameter!')
    def __rsub__(self, a):
        if isinstance(a, GeVec2d): return GeVec2d(a.x-self.x, a.y-self.y)
        else: raise TypeError('improper parameter!')
    def _push_to(self, buf:BufferStack): buf.push(self.x, self.y)
    def _pop_from(self, buf:BufferStack): self.y, self.x = buf.pop(), buf.pop()
    @property
    def x(self): return self._x
    @x.setter
    def x(self, val): self._x = float(val)
    @property
    def y(self): return self._y
    @y.setter
    def y(self, val): self._y = float(val)

class P3DColorDef(BufferStackBase):
    def __init__(self, r=0, g=0, b=0, a=0): self.r, self.g, self.b, self.a = r,g,b,a
    def _push_to(self, bs): bs.push(self.r, self.g, self.b, self.a)
    def _pop_from(self, bs): self.a, self.b, self.g, self.r = bs.pop(), bs.pop(), bs.pop(), bs.pop()
    @property
    def r(self): return self._r
    @r.setter
    def r(self, val): 
        if val<0 or val>1:
            raise ValueError('the value range of RGBA is in [0,1]!')
        self._r = float(val)
    @property
    def g(self): return self._g
    @g.setter
    def g(self, val): 
        if val<0 or val>1:
            raise ValueError('the value range of RGBA is in [0,1]!')
        self._g = float(val)
    @property
    def b(self): return self._b
    @b.setter
    def b(self, val): 
        if val<0 or val>1:
            raise ValueError('the value range of RGBA is in [0,1]!')
        self._b = float(val)
    @property
    def a(self): return self._a
    @a.setter
    def a(self, val): 
        if val<0 or val>1:
            raise ValueError('the value range of RGBA is in [0,1]!')
        self._a = float(val)

class Entityattribute(BufferStackBase):
    def __init__(self, kw={}):...
    #     self._Done = False
    #     self.model_id = kw['model_id'] if 'model_id' in kw else 0
    #     self.entity_id =kw['entity_id'] if 'entity_id' in kw else 0
    #     self.entity_color=kw['entity_color'] if 'entity_color' in kw else 0
    #     self.entity_weight=kw['entity_weight'] if 'entity_weight' in kw else 0
    #     self.entity_style=kw['entity_style'] if 'entity_style' in kw else 0
    #     self.levelname =kw['levelname'] if 'levelname' in kw else ''
    #     self.classname =kw['classname'] if 'classname' in kw else ''
    #     self.schemaname =kw['schemaname'] if 'schemaname' in kw else '' 
    #     self._Done = True
    # @property
    # def model_id(self):return self._model_id
    # @model_id.setter
    # def model_id(self, value):
    #     if not isinstance(value, int):
    #         raise TypeError('输入类型错误，建议输入整型格式:')
    #     self._model_id = value
    #     if self._Done:
    #         UnifiedFunction( PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_SET_MODEL_ENTITY)(self)
    # # @property
    # # def mapUnit(self):
    # #     return self._mapUnit
    # # @mapUnit.setter
    # # def mapUnit(self, value):
    # #     if value != 3 and value != 0 :
    # #         raise TypeError('输入类型错误，建议输入0（按比例贴图）或者3(按尺寸贴图）')
    # #     self._mapUnit = int(value)
    # #     if self._Done:
    # #         UnifiedFunction( PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_UPDATE_MATERIAL)(self)
    # @property
    # def entity_id(self):return self._entity_id
    # @entity_id.setter
    # def entity_id(self, value):
    #     if not isinstance(value, int):
    #         raise TypeError('输入类型错误，建议输入整型格式:')
    #     self._entity_id = value
    #     if self._Done:
    #         UnifiedFunction( PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_SET_MODEL_ENTITY)(self)
    # @property
    # def entity_color(self):return self._entity_color
    # @entity_color.setter
    # def entity_color(self, value):
    #     if not isinstance(value, int):
    #         raise TypeError('输入类型错误，建议输入整型格式:')
    #     self._entity_color = value
    #     if self._Done:
    #         UnifiedFunction( PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_SET_MODEL_ENTITY)(self)
    # @property
    # def entity_weight(self):return self._entity_weight
    # @entity_weight.setter
    # def entity_weight(self, value):
    #     if not isinstance(value, int):
    #         raise TypeError('输入类型错误，建议输入整型格式:')
    #     self._entity_weight = value
    #     if self._Done:
    #         UnifiedFunction( PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_SET_MODEL_ENTITY)(self)
    # @property
    # def entity_style(self):return self._entity_style
    # @entity_style.setter
    # def entity_style(self, value):
    #     if not isinstance(value, int):
    #         raise TypeError('输入类型错误，建议输入整型格式:')
    #     self._entity_style =value
    #     if self._Done:
    #         UnifiedFunction( PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_SET_MODEL_ENTITY)(self)
    # @property
    # def levelname(self):return self._levelname
    # @levelname.setter
    # def levelname(self, value):
    #     if not isinstance(value, str):
    #         raise TypeError('input error type, please input "string"!')
    #     self._levelname = value
    # @property
    # def classname(self):return self._classname
    # @classname.setter
    # def classname(self, value):
    #     if not isinstance(value, str):
    #         raise TypeError('input error type, please input "string"!')
    #     self._classname = value
    def _push_to(self, buf:BufferStack):
        buf.push(self.model_id)
        buf.push(self.entity_id)
        buf.push(self.entity_color)
        buf.push(self.entity_weight)
        buf.push(self.entity_style)
        buf.push(self.levelname)
        buf.push(self.classname)
        buf.push(self.schemaname)
    def _pop_from(self, buf:BufferStack): 
        self._Done = False
        self.schemaname = buf.pop()
        self.classname = buf.pop()
        self.levelname = buf.pop()
        self.entity_style= buf.pop()
        self.entity_weight= buf.pop()
        self.entity_color= buf.pop()
        self.entity_id= buf.pop()
        self.model_id = buf.pop()
        self._Done = True
       
class P3DMaterial(BufferStackBase):
    def __init__(self, kw={}):
        self._Done = False
        self.hasAmbientFactor = True
        self.hasColor = True
        self.hasDiffuseFactor = True
        self.hasGlowColor = True
        self.hasGlowFactor = True
        self.hasMap = False
        self.hasReflectFactor = True
        self.hasRefractFactor = True
        self.hasRoughnessFactor = True
        self.hasSpecularColor = True
        self.hasSpecularFactor = True
        self.hasTransparency = True
        self.isValid = True
        self.name = kw['Name']  if 'Name' in kw else ''
        self.mapFile = kw['path'] if 'path' in kw else ''
        self.mapUnit = kw['mapUnit'] if 'mapUnit' in kw else 0
        self.mapMode = kw['mapMode'] if 'mapMode' in kw else 0
        self.uvScale = kw['uvScale'] if 'uvScale' in kw else [1.0,1.0]
        self.uvOffset = kw['uvOffset'] if 'uvOffset' in kw else [0.0,0.0]
        self.wRotation = kw['wRotation'] if 'wRotation' in kw else 0
        self.bumpFactor = kw['bumpFactor'] if 'bumpFactor' in kw else 0.0
        self.color = kw['color'] if 'color' in kw else [0,245/255,1]
        self.transparency = kw['transparency'] if 'transparency' in kw else 0.0
        self.specularColor = kw['specularColor'] if 'specularColor' in kw else [1.0,1.0,1.0]
        self.specularFactor = kw['specularFactor'] if 'specularFactor' in kw else 1.0
        self.glowColor = kw[' glowColor'] if ' glowColor' in kw else [1.0,1.0,1.0]
        self.glowFactor = kw['glowFactor'] if 'glowFactor' in kw else  55.0
        self.ambientFactor = kw['ambientFactor'] if 'ambientFactor' in kw else  0.6
        self.diffuseFactor = kw['diffuseFactor'] if 'diffuseFactor' in kw else  0.7
        self.roughnessFactor = kw['roughnessFactor'] if 'roughnessFactor' in kw else 0.4
        self.reflectFactor = kw['reflectFactor'] if 'reflectFactor' in kw else  0.4
        self.refractFactor = kw['refractFactor'] if 'refractFactor' in kw else  0.7
        self._Done = True
    @property
    def name(self):return self._name
    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise TypeError('input error type, please input "string"!')
        self._name = value
    @property
    def mapFile(self):
        return self._mapFile
    @mapFile.setter
    def mapFile(self, value):
        if value is None:
            self.hasMap = False
        else:
            if not isinstance(value, str):
                raise TypeError('input error type, please input "string"!')
            self._mapFile = value
            if self._mapFile != '':
                self.hasMap = True
        if self._Done:
            UnifiedFunction( PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_UPDATE_MATERIAL)(self)
        
    @property
    def mapUnit(self):
        return self._mapUnit
    @mapUnit.setter
    def mapUnit(self, value):
        if value != 3 and value != 0 :
            raise TypeError('input error type, input 0(mapping by scale) or 3(mapping by size)')
        self._mapUnit = int(value)
        if self._Done:
            UnifiedFunction( PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_UPDATE_MATERIAL)(self)

    @property
    def mapMode(self):
        return self._mapMode
    @mapMode.setter
    def mapMode(self, value):
        if not value in[0,2,4,5,6]:
            raise TypeError('input error type, input 0(parametric geometry projection), 2(planar projection), 4(cube projection), 5(sphere projection), 6(cone projection)')

        self._mapMode = int(value)
        if self._Done:
            UnifiedFunction( PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_UPDATE_MATERIAL)(self)
   
    @property
    def uvScale(self):
        return self._uvScale 
    @uvScale.setter
    def uvScale(self, value):
        if not(all(map(lambda x :isinstance(x, float ) or isinstance(x, int ),value))):
            raise TypeError('input error type, please input number(suggest float)!')
        self._uvScale = list(map(float,value))
        if self._Done:
            UnifiedFunction( PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_UPDATE_MATERIAL)(self)

    @property
    def uvOffset(self):
        return self._uvOffset
    @uvOffset.setter
    def uvOffset(self, value):
        if not(all(map(lambda x :isinstance(x, float ) or isinstance(x, int ),value))):
            raise TypeError('input error type, please input number(suggest float)!')
        self._uvOffset = list(map(float,value))
        if self._Done:
            UnifiedFunction( PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_UPDATE_MATERIAL)(self)

    @property
    def wRotation(self):
        return self._wRotation
    @wRotation.setter
    def wRotation(self, value):
        if not (isinstance(value, int) or isinstance(value, float)):
            raise TypeError('input error type, please input number(suggest float)!')
        self._wRotation = float(value)
        if self._Done:
            UnifiedFunction( PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_UPDATE_MATERIAL)(self)
    # @property
    # def bumpFactor(self):
    #     return self._bumpFactor 
    # @bumpFactor.setter
    # def bumpFactor(self, value):
    #     if not (isinstance(value, int) or isinstance(value, float)):
    #         raise TypeError('输入类型错误，建议输入整数或小数：')
    #     self._bumpFactor = float(value)
    #     if self._Done:
    #         UnifiedFunction( PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_UPDATE_MATERIAL)(self)
    @property
    def color(self):
        return self._color
    @color.setter
    def color(self, value):
        if value is None:
            self.hascolor = False
        else:
            if not(all(map(lambda x :isinstance(x, float ) or isinstance(x, int ),value))):
                raise TypeError('input error type, please input number(suggest float)!')
            self._color = list(map(float,value))
            self.hascolor = True
        if self._Done:
            UnifiedFunction( PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_UPDATE_MATERIAL)(self)

    @property
    def transparency(self):
        return self._transparency 
    @transparency.setter
    def transparency(self, value):
        if not(isinstance(value, int) or isinstance(value, float)):
            raise TypeError('input error type, please input number(suggest float)!')
        self._transparency = float(value)
        if self._Done:
            UnifiedFunction( PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_UPDATE_MATERIAL)(self)

    @property
    def specularColor(self):
        return self._specularColor
    @specularColor.setter
    def specularColor(self, value):
        if not(all(map(lambda x :isinstance(x, float ) or isinstance(x, int ),value))):
            raise TypeError('input error type, please input number(suggest float)!')
        self._specularColor = list(map(float,value))
        if self._Done:
            UnifiedFunction( PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_UPDATE_MATERIAL)(self)

    @property
    def specularFactor(self):
        return self._specularFactor
    @specularFactor.setter
    def specularFactor(self, value):
        
        if not(isinstance(value, int) or isinstance(value, float)):
            raise TypeError('input error type, please input number(suggest float)!')
        self._specularFactor = float(value)
        if self._Done:
            UnifiedFunction( PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_UPDATE_MATERIAL)(self)

    @property
    def glowColor(self):
        return self._glowColor
    @glowColor.setter
    def glowColor(self, value):
        if not(all(map(lambda x :isinstance(x, float ) or isinstance(x, int ),value))):
            raise TypeError('input error type, please input number(suggest float)!')
        self._glowColor = list(map(float,value))
        if self._Done:
            UnifiedFunction( PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_UPDATE_MATERIAL)(self)

    @property
    def glowFactor(self):
        return self._glowFactor
    @glowFactor.setter
    def glowFactor(self, value):
        if value < 0 or value > 100:
            raise TypeError('input error value, please input number in (0-100) or decimal!')
        self._glowFactor = float(value)
        if self._Done:
            UnifiedFunction( PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_UPDATE_MATERIAL)(self)

    @property
    def ambientFactor(self):
        return self._ambientFactor 
    @ambientFactor.setter
    def ambientFactor(self, value):
        if value < 0 or value > 1:
            raise TypeError('input error value, please input decimal in (0-1)!')
        self._ambientFactor = float(value)
        if self._Done:
            UnifiedFunction( PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_UPDATE_MATERIAL)(self)

    #待开发功能
    # @property
    # def diffuseFactor(self):
    #     return self._diffuseFactor
    # @diffuseFactor.setter
    # def diffuseFactor(self, value):
    #     if value < 0 or value > 1:
    #         raise TypeError('输入范围错误，建议输入0~1内的小数')
    #     self._diffuseFactor = float(value)
    #     if self._Done:
    #         UnifiedFunction( PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_UPDATE_MATERIAL)(self)
    # @property
    # def roughnessFactor(self):
    #     return self._roughnessFactor
    # @roughnessFactor.setter
    # def roughnessFactor(self, value):
    #     if value < 0 or value > 1:
    #         raise TypeError('输入范围错误，建议输入0~1内的小数')
    #     self._roughnessFactor = float(value)
    #     if self._Done:
    #         UnifiedFunction( PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_UPDATE_MATERIAL)(self)
    # @property
    # def reflectFactor(self):
    #     return self._reflectFactor 
    # @reflectFactor.setter
    # def reflectFactor(self, value):
    #     if value < 0 or value > 1:
    #         raise TypeError('输入范围错误，建议输入0~1内的小数')
    #     self._reflectFactor = float(value)
    #     if self._Done:
    #         UnifiedFunction( PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_UPDATE_MATERIAL)(self)
    # @property
    # def refractFactor(self):
    #     return self._refractFactor
    # @refractFactor.setter
    # def refractFactor(self, value):
    #     if value < 0 or value > 1:
    #         raise TypeError('输入范围错误，建议输入0~1内的小数')
    #     self._reflectFactor = float(value)
    #     if self._Done:
    #         UnifiedFunction( PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_UPDATE_MATERIAL)(self)

    def texture(self,path, **kw):
             # ''' 要确保第二次传的    参数全部和creatematerial一样
        self._Done = False
        self.mapFile = path
        if 'mapUnit' in kw: self.mapUnit = kw['mapUnit'] 
        if 'mapMode' in kw: self.mapMode = kw['mapMode']  
        if 'uvScale' in kw: self.uvScale = kw['uvScale'] 
        if 'uvOffset' in kw:self.uvOffset = kw['uvOffset']  
        if 'wRotation' in kw: self.wRotation = kw['wRotation'] 
        if 'bumpFactor' in kw: self.bumpFactor = kw['bumpFactor']  
        if 'color' in kw: self.color = kw['color']  
        if 'transparency' in kw: self.transparency = kw['transparency']  
        if 'specularColor' in kw: self.specularColor = kw['specularColor']  
        if 'specularFactor' in kw: self.specularFactor = kw['specularFactor']  
        if ' glowColor' in kw: self.glowColor = kw[' glowColor']  
        if 'glowFactor' in kw: self.glowFactor = kw['glowFactor'] 
        if 'ambientFactor' in kw: self.ambientFactor = kw['ambientFactor']  
        if 'diffuseFactor' in kw:  self.diffuseFactor = kw['diffuseFactor'] 
        if 'roughnessFactor' in kw: self.roughnessFactor = kw['roughnessFactor']  
        if 'reflectFactor' in kw:  self.reflectFactor = kw['reflectFactor'] 
        if 'refractFactor' in kw: self.refractFactor = kw['refractFactor']  
        self._Done = True
        UnifiedFunction( PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_UPDATE_MATERIAL)(self)
    
    def _push_to(self, buf:BufferStack):
        buf.push(self._transparency)
        buf.push(self.name)
        buf.push(self.mapFile)
        buf.push(self.mapUnit)
        buf.push(self.mapMode)
        buf.push(self.uvScale[1])
        buf.push(self.uvScale[0])
        buf.push(self.uvOffset[1])
        buf.push(self.uvOffset[0])
        buf.push(self.wRotation)
        buf.push(self.bumpFactor)
        buf.push(self.color[2])
        buf.push(self.color[1])
        buf.push(self.color[0])
        buf.push(self.transparency)
        buf.push(self.specularColor[2])
        buf.push(self.specularColor[1])
        buf.push(self.specularColor[0])
        buf.push(self.specularFactor)
        buf.push(self.glowColor[2])
        buf.push(self.glowColor[1])
        buf.push(self.glowColor[0])
        buf.push(self.glowFactor)
        buf.push(self.ambientFactor)
        buf.push(self.diffuseFactor)
        buf.push(self.roughnessFactor)
        buf.push(self.reflectFactor)
        buf.push(self.refractFactor)
        buf.push(self.hasAmbientFactor )
        buf.push(self.hasColor )
        buf.push(self.hasDiffuseFactor )
        buf.push(self.hasGlowColor )
        buf.push(self.hasGlowFactor )
        buf.push(self.hasMap )
        buf.push(self.hasReflectFactor )
        buf.push(self.hasRefractFactor)
        buf.push(self.hasRoughnessFactor )
        buf.push(self.hasSpecularColor )
        buf.push(self.hasSpecularFactor )
        buf.push(self.hasTransparency )
        buf.push(self.isValid)
    
    def _pop_from(self, buf:BufferStack): 
        self._Done = False
        self.isValid = buf.pop()
        self.hasTransparency= buf.pop()
        self.hasSpecularFactor= buf.pop()
        self.hasSpecularColor= buf.pop()
        self.hasRoughnessFactor= buf.pop()
        self.hasRefractFactor= buf.pop()
        self.hasReflectFactor= buf.pop()
        self.hasMap = buf.pop()
        self.hasGlowFactor= buf.pop()
        self.hasGlowColor= buf.pop()
        self.hasDiffuseFactor= buf.pop()
        self.hasColor= buf.pop()
        self.hasAmbientFactor= buf.pop()
        self.refractFactor = buf.pop()
        self.reflectFactor = buf.pop()
        self.roughnessFactor = buf.pop()
        self.diffuseFactor = buf.pop()
        self.ambientFactor = buf.pop()
        self.glowFactor = buf.pop()
        self.glowColor = [buf.pop(), buf.pop(), buf.pop()]
        self.specularFactor = buf.pop()
        self.specularColor=[buf.pop(),buf.pop(),buf.pop()] 
        self.transparency = buf.pop()
        self.color = [buf.pop(),buf.pop(),buf.pop()]
        self.bumpFactor = buf.pop()
        self.wRotation = buf.pop()
        self.uvOffset = [buf.pop(),buf.pop()]
        self.uvScale = [buf.pop(),buf.pop()]
        self.mapMode = buf.pop()
        self.mapUnit = buf.pop()
        self.mapFile = buf.pop()
        self.name = buf.pop()
        self._Done = True

enrol(0x1395755506582671, P3DEntityId)
enrol(0x0956146148825714, P3DModelId)
enrol(0x1395017306582671, P3DInstanceKey)

enrol(0x6239225542517109, GeTransform)
enrol(0x0005485042476852, GeVec3d)
enrol(0x0059485042476852, GeVec2d)
enrol(0x4767484556636631, P3DColorDef)
enrol(0x2624634702211655, P3DMaterial)
enrol(0x1395755514661840, Entityattribute)

# def createP3DInstance(schemaName, className, data) -> _P3DInstanceKey:
#     BPP3DApiForPython.createP3DInstance(list(geom))


