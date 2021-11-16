# Copyright (C), 2019-2028, Beijing GLory PKPM Tech. Co., Ltd.
# Brief: PKPM-BIMBase Python二次开发SDK与参数化组件功能。
# Author: YouQi, ZhangHan
# Date: 2021/08/07
from ..ParametricComponentConvention import *
from ..p3d_type import *
from ..dll import *
import copy, math, sys, time
from math import *
from math import tan,atan,atan2,sqrt,cos,acos,sin,asin,pi

class Attr(BufferStackBase):
    '''
    Attribute database, multi-fork tree structure with main node,to load parameter component attribute database
    '''
    def __init__(self, this = None, **kw): self._this, self._attr = this, { k:v if isinstance(v, Attr) else Attr(v) for k,v in kw.items()}
    def __getitem__(self, key): return self._attr[key].this
    def __setitem__(self, key, value): self._attr[key] = value if isinstance(value, Attr) else Attr(value)
    def __delitem__(self, key): del self._noumenon_data[key]
    def __contains__(self, item): return item in self._attr
    def __str__(self): return '{0}#{{{1}}}'.format(self._this, ', '.join(['{0}={1}'.format(k,v) for k,v in self._attr.items()]))
    def _push_to(self, bs:BufferStack)->None: 
        for k, v in self._attr.items(): 
            bs.push(v, k)
        bs.push(Size_t(len(self._attr)), self._this)
    def _pop_from(self, bs:BufferStack)->None: 
        self._this, size, self._attr = bs.pop(), bs.pop(), {}
        for _ in range(size):
            k, v = bs.pop(), bs.pop()
            self._attr[k] = v
    def at(self, key): return self._attr[key]
    def setup(self, **args):
        for k, v in args.items():
            self._attr[k] = v if isinstance(v, Attr) else Attr(v)
    @property
    def this(self): return self._this
    @this.setter
    def this(self, value): self._this = value

class Noumenon(BufferStackBase): #  本体数据
    '''
    Noumenon database
    '''
    def __init__(self):
        self._noumenon_data = {}
        self._noumenon_order = []
    def __str__(self): return '\n'.join(['{0}={1}'.format(key, self._noumenon_data[key]) for key in self._noumenon_order])
    def __getitem__(self, key):
        if isinstance(key, int): return self._noumenon_data[self._noumenon_order[key]].this
        elif isinstance(key, str): return self._noumenon_data[key].this
        else: raise TypeError()
    def __setitem__(self, key, value):
        if isinstance(key, str):...
        elif isinstance(key, int):
            if not key < len(self._noumenon_order): raise IndexError('OrderedDictionary index out of range')
            key = self._noumenon_order[key]
        else: raise TypeError()
        if key in self._noumenon_data: 
            if isinstance(value, Attr): 
                self._noumenon_data[key] = value
            elif isinstance(value, FunctionType):
                self._noumenon_data[key].this = UnifiedFunction(value)
                self._noumenon_data[key]['member'] = True
            else: 
                self._noumenon_data[key].this = value
        else:
            if isinstance(value, Attr):
                self._noumenon_data[key] = value
            elif isinstance(value, FunctionType):
                self._noumenon_data[key] = Attr(UnifiedFunction(value), member=True)
            else:
                self._noumenon_data[key] = Attr(value)
            self._noumenon_order.append(key)
    def __delitem__(self, key):
        if isinstance(key, int):
            if not key < len(self._noumenon_order): raise IndexError('OrderedDictionary index out of range')
            del self._noumenon_data[self._noumenon_order[key]]
            self._noumenon_order.remove(key)
        elif isinstance(key, str):
            del self._noumenon_data[key]
            self._noumenon_order.remove(key)
        else: raise TypeError()
    def at(self, key)->Attr: return self._noumenon_data[key]
    def __mul__(self, other):
        if not issubclass(type(other), Noumenon): raise TypeError('object not inherited form Noumenon')
        c = copy.deepcopy(other)
        for k, v in self.items():
            c[k] = v
        return c
    def __len__(self): return len(self._noumenon_order)
    def __iter__(self):
        self._iter = 0
        return self
    def __next__(self):
        if self._iter >= len(self._noumenon_order): raise StopIteration
        key = self._noumenon_order[self._iter]
        self._iter += 1
        return self._noumenon_data[key]
    def __contains__(self, item): return item in self._noumenon_data
    def keys(self): return self._noumenon_order
    def values(self): return [self._noumenon_data[i] for i in self._noumenon_order]
    def items(self): return [(i,self._noumenon_data[i]) for i in self._noumenon_order]
    def insert(self, key, value, position=None):
        if not isinstance(key, str): raise TypeError()
        self.set_object(key, value if isinstance(value, Attr) else Attr(value))
        if position is None: return
        self.adjust(key, position)
    def adjust(self, index, position):
        if isinstance(index, int):...
        elif isinstance(index, str): index = self._noumenon_order.index(index)
        else: raise TypeError()
        if isinstance(position, int):...
        elif isinstance(position, str): position = self._noumenon_order.index(position)
        else: raise TypeError()
        if not(index < len(self._noumenon_order) and position <= len(self._noumenon_order)): raise IndexError('OrderedDictionary index out of range')
        if index == position: return
        key = self._noumenon_order[index]
        del self._noumenon_order[index]
        self._noumenon_order.insert(position if position < index else position - 1, key)
    def _push_to(self, bs:BufferStack)->None:
        # 自动装载表象名
        if not runtime_is_service() and issubclass(type(self), Component) and type(self).__name__ != 'Component': 
            self.at(PARACMPT_KEYWORD_SOURCE).setup(obvious=False, readonly=True)
            self.at(PARACMPT_KEYWORD_REPRESENTATION).setup(obvious=False, readonly=True)
            self[PARACMPT_KEYWORD_SOURCE] = get_core_source()
            self[PARACMPT_KEYWORD_REPRESENTATION] = '{0}.{1}'.format(os.path.splitext(os.path.split(sys.argv[0])[1])[0], type(self).__name__)
        # 导出函数UF化
        for methodName in get_export_method('{0}.{1}'.format(type(self).__module__, type(self).__name__)):
            self[methodName] = Attr(UnifiedFunction(getattr(type(self), methodName)), member=True)
        for key in self._noumenon_order[::-1]: bs.push(self._noumenon_data[key], key)
        bs.push(Size_t(len(self._noumenon_order)))
    def _pop_from(self, bs:BufferStack)->None:
        element = [bs.pop() for _ in range(bs.pop()*2)]
        data = dict(zip(element[0::2], element[1::2]))
        order = list(element[0::2])
        if not PARACMPT_KEYWORD_REPRESENTATION in order: 
            self._noumenon_data = data
            self._noumenon_order = order
            return
        temp = os.path.splitext(data[PARACMPT_KEYWORD_REPRESENTATION].this)
        if temp[1] == '':
            cla = eval(temp[0])
        else:
            import_module(temp[0], True)
            cla = getattr_from(temp[0], temp[1][1:])
        if cla is None: return
        obj = cla()
        obj._noumenon_data = data
        obj._noumenon_order = order
        return obj

enrol(0x141762724222207, Attr)
enrol(0x260975554222207, Noumenon)
set_global_variable('is_script_to_josn', False)

def place(noumenon:Noumenon): #通过布置工具放置组件
    if get_global_variable('is_script_to_josn'):
        set_global_variable('script_to_josn', noumenon)
    else:
        UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_PLACE_INSTANCE)(noumenon)

def get_data(noumenon:Noumenon): #获取launchData数据
    UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_GETDATA_INSTANCE)(noumenon)

def place_data(noumenon:Noumenon): #重新放置data数据
    UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_PLACEDATA_INSTANCE)(noumenon)

def place_to(noumenon:Noumenon, transform:GeTransform):
    '''
    appoint position where geometry place to
    '''
    UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_PLACE_INSTANCE_TO)(noumenon, transform)

def create_bsplinepoints(controlPoints:list,curveOrder:int,discreteNum:int)->list:
    '''
    using control points, return BsplinePoints points
    '''
    # for i in controlPoints:
    #     if not isinstance(i,GeVec2d):
    #         raise ValueError('Bspline control points must in XoY plane!')
    if curveOrder > len(controlPoints):
        raise ValueError('curveOrder\'s parameter is the count of max control-points, please input proper parameter!')
    else:
        return UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT,PARACMPT_CREATE_BSPLINEPOINTS)(controlPoints,curveOrder,discreteNum)

def delete_entity(**kwargs)->list:

    '''
    delete all "entity" in present project which meet the condition
    '''
    if len(kwargs)==0:
        raise ValueError('please input the range of "entityid"!\n')
    UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT,PARACMPT_DELETE_ENTITY)(kwargs)

def get_entity_property(**kwargs)->list: #返回包含当前工程符合条件的entityid的列表
    '''
    return list of "entityid" in present project which meet the condition
    '''
    res = UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT,PARACMPT_GET_ENTITY_PROPERTY)(kwargs)
    if len(res)==0:
        raise ValueError('there is no proper "entity", please revise the condition\n')
        # return res
    else:
        return res

def set_entity_property(**kwargs)->list: #把当前工程符合条件的所有entity的属性修改为传入的属性
    '''
    '''
    for k,v in kwargs.items():
        if k == 'schemaname' or k =='classname':
            raise TypeError('you can not change "schemaname" and "classname"!\n')
    UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT,PARACMPT_SET_ENTITY_PROPERTY)(kwargs)

def create_instance_instancekey(schemaName:str,className:str)->P3DInstanceKey:
    '''
    通过schemaname和classname生成instance并返回instancekey
    '''
    if not(isinstance(schemaName, str) or isinstance(className,str)):
         raise TypeError('输入类型错误，请输入字符串类型：')
    return UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT,PARACMPT_CREATE_INSTANCE_INSTANCEKEY)(schemaName,className)

def delete_instance_byinstancekey(instancekey:P3DInstanceKey):
    '''
    删除Instance,通过instancekey
    '''
    if not isinstance(instancekey, P3DInstanceKey):
         raise TypeError('输入类型错误，请输入P3DInstanceKey类型：')
    UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT,PARACMPT_DELETE_INSTANCE_BYINSTANCEKEY)(instancekey)

def bind_entity_instance(entityid:P3DEntityId,instancekey:P3DInstanceKey):
    '''
    绑定Entity和Instance
    '''
    if not (isinstance(entityid, P3DEntityId) or isinstance(instancekey,P3DInstanceKey)):
         raise TypeError('输入类型错误，请_P3DInstanceKey类型：')
    UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT,PARACMPT_BIND_ENTITY_INSTANCE)(entityid,instancekey)

def removebind_entity_instance(entityid:P3DEntityId,instancekey:P3DInstanceKey):
    '''
    解除绑定Entity和Instance
    '''
    if not (isinstance(entityid, P3DEntityId) or isinstance(instancekey,P3DInstanceKey)):
         raise TypeError('输入类型错误，请输入_P3DEntityId和_P3DInstanceKey类型：')
    UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT,PARACMPT_REMOVEBIND_ENTITY_INSTANCE)(entityid,instancekey)

def get_allbinding_entity_from_instance(instancekey:P3DInstanceKey):
    '''
    查询instance绑定的所有entity
    '''
    if not isinstance(instancekey,P3DInstanceKey):
        raise TypeError('输入类型错误，请输入P3DInstanceKey类型：')
    return UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT,PARACMPT_GET_ALLBINDING_ENTITY_FROM_INSTANCE)(instancekey)  
def get_all_instancekey()->list:
    '''
    查询当前工程中所有的instance,返回P3DInstanceKey的列表
    '''
    return UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT,PARACMPT_GET_ALL_INSTANCEKEY)()  
def get_modelid_from_instance(instancekey:P3DInstanceKey)->P3DModelId:
    '''
    获取P3DInstance关联Entity所在的Model的modelid
    '''
    if not isinstance(instancekey,P3DInstanceKey):
        raise TypeError('输入类型错误，请输入P3DInstanceKey类型：')
    return UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT,PARACMPT_GET_MODELID_FROM_INSTANCE)(instancekey) 
def get_instancekey_from_entity(entityid:P3DEntityId)->P3DInstanceKey:
    '''
    获取与Entity关联的P3DInstancekey
    '''
    if not isinstance(entityid,P3DEntityId):
        raise TypeError('输入类型错误，请输入P3DEntityId类型：')
    return UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT,PARACMPT_GET_INSTANCEKEY_FROM_ENTITY)(entityid)   





def get_modelid_entityid_relation()->dict:
    '''
    return the relationship of modelid and entityid, relationship of ModelInfo_modelid and AssociateModel_modelid, in present project
    '''
    res = UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT,PARACMPT_GET_MODELID_ENTITYID_RELATION)()
    return {'ModelInfo_modelid_AssociateModel_modelid':res[0],
            'ModelInfo_modelid_entityid':res[1],
            'AssociateModel_modelid_entityid':res[2]}  
    # entitylist = []
    # for j in range(len(res[6])):
    #     entitylist.append({
    #     'model_id:':res[6][j].model_id,
    #     'entity_id:':res[6][j].entity_id,
    #     'entity_color:':res[6][j].entity_color,
    #     'entity_weight:':res[6][j].entity_weight,
    #     'entity_style:':res[6][j].entity_style,
    #     'schemaname:':res[6][j].schemaname,
    #     'classname:':res[6][j].classname,
    #     'levelname:':res[6][j].levelname})
    

    # for i in range(len(res)):
    #     res[i] = list(set(res[i]))
    # return {'schemaname':res[0],'classname':res[1],'levelname':res[2],'colorname':res[3],'weightname':res[4],'stylename':res[5],'entitylist':entitylist,'entityidlist':res[7]}  
def create_geometry(noumenon:Noumenon):
    return UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_CREATE_GEOMETRY)(noumenon)

def create_material(name, **kw):
    kw['Name'] = name
    mat = P3DMaterial(kw)
    UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_CREATE_MATERIAL)(mat)
    return mat

def exit_tool():
    UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMTP_PLACE_TOOL_EXIT)()

def get_all_entityproperty(): #返回包含当前工程所有entity的列表
    '''
    return list of all entity in current project
    '''
    return UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_GET_ALL_ENTITYPROPERTY)()
    
def dynamic_preview(noumenon:Noumenon): #动态预览
    UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMTP_PLACE_TOOL_DYNAMIC)(noumenon)

def pack_to_bfa(path:str, noumenon:Noumenon, files:list=[]): #打包bfa文件
    UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_PACK_BFA)(path, noumenon, files)

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
        elif len(args)==1 and (isinstance(args[0],list) or isinstance(args[0],tuple)):
            if len(args[0])==4:
                color = P3DColorDef(args[0][0],args[0][1],args[0][2],args[0][3])
            elif len(args[0])==3:
                color = P3DColorDef(args[0][0],args[0][1],args[0][2],1)
        elif len(args)==2 and (isinstance(args[0],list) or isinstance(args[0],tuple)) and (isinstance(args[1],int) or isinstance(args[1],float)):
            color = P3DColorDef(args[0][0],args[0][1],args[0][2],args[1])
        elif len(args)==3 and (isinstance(args[0]+args[1]+args[2],int) or isinstance(args[0]+args[1]+args[2],float)):
            color = P3DColorDef(args[0],args[1],args[2],1)
        elif len(args)==4 and (isinstance(args[0]+args[1]+args[2]+args[3],int) or isinstance(args[0]+args[1]+args[2]+args[3],float)):
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
            self.scope = args[0]
        elif len(args) == 3:
            atanp = lambda y,x:atan2(y,x) if atan2(y,x) >=0 else atan2(y,x)+2*pi
            posi = lambda theta: theta+2*pi if theta<0 else theta
            if isinstance(args[0],GeVec3d) and isinstance(args[1],GeVec3d) and isinstance(args[1],GeVec3d):
                sec=_points_become_section(args)
            elif isinstance(args[0],GeVec2d) and isinstance(args[1],GeVec2d) and isinstance(args[1],GeVec2d): #using function judge legal points
                sec=_points_become_section([GeVec3d(args[0].x,args[0].y,0),GeVec3d(args[1].x,args[1].y,0),GeVec3d(args[2].x,args[2].y,0)])
            else:
                raise ValueError('improper parameters!')
            points=sec.parts
            x1=points[0].x
            y1=points[0].y
            x2=points[1].x
            y2=points[1].y
            x3=points[2].x
            y3=points[2].y
            yc=((x3-x2)*(x3**2+y3**2-x1**2-y1**2)-(x3-x1)*(x3**2+y3**2-x2**2-y2**2)) / (2*(x3-x2)*(y3-y1)-2*(x3-x1)*(y3-y2))
            xc=((y3-y2)*(x3**2+y3**2-x1**2-y1**2)-(y3-y1)*(x3**2+y3**2-x2**2-y2**2)) / (2*(y3-y2)*(x3-x1)-2*(y3-y1)*(x3-x2))
            R=sqrt((xc-x1)**2+(yc-y1)**2)
            self.transformation=sec.transformation*translate(xc,yc)*scale(R)*rotate(atanp(y1-yc,x1-xc))
            inAngle=posi(atanp(y3-yc,x3-xc)-atanp(y1-yc,x1-xc))
            self.scope = inAngle
        # elif len(args) == 5 and is_num(args):
        #     ellipse=Ellipse(args[0], args[1], args[2], args[3], args[4])
        #     self.transformation=ellipse.transformation
        #     self.scope = args[4]
        else:
            raise ValueError('improper parameters!')
    @property
    def scope(self):
        return self[PARACMPT_ARC_SCOPE]
    @scope.setter
    def scope(self, val):
        self[PARACMPT_ARC_SCOPE] = val#float(val)

class Line(Primitives):
    def __init__(self, *args):
        Primitives.__init__(self)
        self.representation = 'Line'
        self.extractGraphics = UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_LINE_TO_GRAPHICS)
        self.dimension = True #dimension judge, 2-dimension==True, 3-dimension==False
        if len(args)==1 and (isinstance(args[0], list) or isinstance(args[0], tuple)): 
            self.parts = list(args[0])
        else:
            self.parts = list(args)
        for value in self.parts:
            if isinstance(value, GeVec2d):
                continue
            elif isinstance(value, Arc) or isinstance(value, Ellipse):
                axisZi=GeVec3d(value.transformation._mat[0][2],value.transformation._mat[1][2],value.transformation._mat[2][2])
                if abs(value.transformation._mat[2][3])>1e-10 or abs(abs(dot(unitize(axisZi),GeVec3d(0,0,1)))-1)>1e-10:
                    self.dimension = False
                    break
            elif isinstance(value, GeVec3d):
                if abs(value.z)>1e-10:
                    self.dimension = False
                    break
            elif isinstance(value, Line):
                if not value.dimension:
                    self.dimension = False
            else:
                raise TypeError('Line parameter error!')
    def append(self, value):
        if isinstance(value, GeVec2d):
            pass
        elif isinstance(value, Arc) or isinstance(value, Ellipse):
            axisZi=GeVec3d(value.transformation._mat[0][2],value.transformation._mat[1][2],value.transformation._mat[2][2])
            if abs(value.transformation._mat[2][3])>1e-10 or abs(abs(dot(unitize(axisZi),GeVec3d(0,0,1)))-1)>1e-10:
                self.dimension = False
        elif isinstance(value, GeVec3d):
            if abs(value.z)>1e-10:
                self.dimension = False
        elif isinstance(value, Line):
            if not value.dimension:
                self.dimension = False
        else:
            raise TypeError('Line parameter error!')
        # self.parts.append(value)
        self[PARACMPT_LINE_PARTS].append(value)
    @property
    def parts(self):
        return self[PARACMPT_LINE_PARTS]
    @parts.setter
    def parts(self, val):
        if not isinstance(val, list): raise TypeError('Line parameter error!')
        idf = lambda x: isinstance(x, GeVec2d) or isinstance(x, GeVec3d) or (isinstance(x, Noumenon) and PARACMPT_KEYWORD_TRANSFORMATION in x)
        if not all(map(idf, val)): raise TypeError('Line parameter error!')
        self[PARACMPT_LINE_PARTS] = val
        
class Section(Primitives):
    def __init__(self, *args):
        Primitives.__init__(self)
        self.representation = 'Section'
        self.extractGraphics = UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_SECTION_TO_GRAPHICS)
        if len(args)==1 and (isinstance(args[0], list) or isinstance(args[0], tuple)): 
            self.parts = list(args[0])
        else:
            self.parts = list(args)
        self.close = True
        for value in self.parts:
            if isinstance(value, GeVec2d):
                continue
            elif isinstance(value, Arc) or isinstance(value, Ellipse):
                axisZi=GeVec3d(value.transformation._mat[0][2],value.transformation._mat[1][2],value.transformation._mat[2][2])
                if abs(value.transformation._mat[2][3])>1e-10 or (is_same_direction(axisZi,GeVec3d(0,0,1))==False):
                    raise TypeError('Section parameter error!')
            elif isinstance(value, GeVec3d):
                if abs(value.z)>1e-10:
                    raise TypeError('Section parameter error!')
            elif isinstance(value, Line):
                if value.dimension:
                    continue
                else:
                    raise TypeError('Section parameter error!')
            else:
                raise TypeError('Section parameter error!')
    def append(self, value):
        if isinstance(value, GeVec2d):
            pass
        elif isinstance(value, Arc) or isinstance(value, Ellipse):
            axisZi=GeVec3d(value.transformation._mat[0][2],value.transformation._mat[1][2],value.transformation._mat[2][2])
            if abs(value.transformation._mat[2][3])>1e-10 or abs(abs(dot(unitize(axisZi),GeVec3d(0,0,1)))-1)>1e-10:
                raise TypeError('Section parameter error!')
        elif isinstance(value, GeVec3d):
            if abs(value.z)>1e-10:
                raise TypeError('Section parameter error!')
        elif isinstance(value, Line):
            if not value.dimension:
                raise TypeError('Section parameter error!')
        else:
            raise TypeError('Section parameter error!')
        self[PARACMPT_SECTION_PARTS].append(value)
    @property
    def parts(self):
        return self[PARACMPT_SECTION_PARTS]
    @parts.setter
    def parts(self, val):
        if not isinstance(val, list): raise TypeError('Section parameter error!')
        idf = lambda x: isinstance(x, GeVec2d) or isinstance(x, GeVec3d) or (isinstance(x, Noumenon) and PARACMPT_KEYWORD_TRANSFORMATION in x)
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
        self.parts = list(args)
        self.smooth = False
    @property
    def parts(self):
        return self[PARACMPT_LOFT_PARTS]
    @parts.setter
    def parts(self, val):
        if not isinstance(val, list): raise TypeError('')
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
            if(isinstance(args[0], int) or isinstance(args[0], float)):
                self.horzscale = float(args[0])
            elif isinstance(args[0], str):
                self.font_name = args[0]
            else:
                raise ValueError('the input value isnot number or "fontName" isnot string')
        elif len(args)==2 and((isinstance(args[0], int) or isinstance(args[0], float)) and (isinstance(args[1], int) or isinstance(args[1], float))):
            self.horzscale = float(args[0])
            self.vertscale = float(args[1])
        elif len(args)==3 and((isinstance(args[0], int) or isinstance(args[0], float)) and (isinstance(args[1], int) or isinstance(args[1], float))) and isinstance(args[2], str):
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
            if isinstance(args[i],list):
                args[i]=Combine(*args[i]) # attention recursion
            elif not issubclass(type(args[i]),Graphics): #Primitives
                raise TypeError('please input proper "Combine(Graphics)"')
        self.parts = list(args)
    def color(self, *argscolor):
        if len(argscolor)==0 :
            color = P3DColorDef(0.5,0.5,0.5,1)
        elif len(argscolor)==1 and (isinstance(argscolor[0],list) or isinstance(argscolor[0],tuple)):
            if len(argscolor[0])==4:
                color = P3DColorDef(argscolor[0][0],argscolor[0][1],argscolor[0][2],argscolor[0][3])
            elif len(argscolor[0])==3:
                color = P3DColorDef(argscolor[0][0],argscolor[0][1],argscolor[0][2],1)
        elif len(argscolor)==2 and (isinstance(argscolor[0],list) or isinstance(argscolor[0],tuple)) and (isinstance(argscolor[1],int) or isinstance(argscolor[1],float)):
            color = P3DColorDef(argscolor[0][0],argscolor[0][1],argscolor[0][2],argscolor[1])
        elif len(argscolor)==3 and (isinstance(argscolor[0]+argscolor[1]+argscolor[2],int) or isinstance(argscolor[0]+argscolor[1]+argscolor[2],float)):
            color = P3DColorDef(argscolor[0],argscolor[1],argscolor[2],1)
        elif len(argscolor)==4 and (isinstance(argscolor[0]+argscolor[1]+argscolor[2]+argscolor[3],int) or isinstance(argscolor[0]+argscolor[1]+argscolor[2]+argscolor[3],float)):
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
            if isinstance(args[i],list):
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
        if len(val)>=1:
            if isinstance(val[0],Section):
                datam=val[0].transformation._mat
                vectorZ=GeVec3d(datam[0][2],datam[1][2],datam[2][2])
                for i in range(1,len(val)):
                    matrix=val[i].transformation._mat
                    vectorZi=GeVec3d(matrix[0][2],matrix[1][2],matrix[2][2])
                    parallel=abs(abs(dot(vectorZ,vectorZi))-norm(vectorZ)*norm(vectorZi))
                    vectorD=GeVec3d(matrix[0][3]-datam[0][3],matrix[1][3]-datam[1][3],matrix[2][3]-datam[2][3])
                    # if norm(vectorD)<1e-10 and parallel<1e-10: # 
                    #     continue
                    if abs(dot(vectorZ,vectorD))<1e-10 and parallel<1e-10:
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
            if isinstance(args[i],list):
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


#################################################################
#                       1.0 兼容接口                            #
#################################################################
# Copyright (C), 2019-2028, Beijing GLory PKPM Tech. Co., Ltd.
# Brief: PKPM-BIMBase Python二次开发SDK与参数化组件功能。
# Author: YanYinji, akingse, YouQi
# Date: 2021/08/07
   
def _points_become_section(*agrs): #多点(>=3)生成一个二维Section面，已变换到3维
    '''
    many point (>=3) generate a section in 2-dimension, been translated to 3-dimension already
    '''
    points=list(agrs) # using original calculation
    if len(points)==1 and (isinstance(points[0], list) or isinstance(points[0], tuple)):
        points=list(points[0])
    for i in points:
        if not isinstance(i,GeVec3d):
            raise ValueError('to_section\'s parameter must be "GeVec3d"!')
    lengP=len(points)
    if  lengP<=2:
        raise ValueError('please input 3 points at least, to compose one plane！')
    else:
        pointA=points[0] #
        for i in range(1,lengP):
            pointB=points[i]
            if norm(pointB - pointA)>=1e-10:
                break
            elif i==lengP-1:
                raise ValueError('please donot make all coincident points!')
            else:
                continue
        # vectorX= (pointB- pointA) * (1/norm(pointB - pointA) )
        vectorX=unitize(pointB - pointA)
        for i in range(2,lengP):
            pointC=points[i]
            vectorZ=cross(vectorX,pointC - pointA) #vectorAC=pointC-pointA
            if norm(vectorZ) > 1e-10:
                break
            elif i==lengP-1:
                raise ValueError('please donot make all collinear points!')
            else:
                continue
        # vectorZ=vectorZ*(1/norm(vectorZ))
        vectorZ=unitize(cross(vectorX,pointC - pointA))
        vectorY=cross(vectorZ , vectorX)
        for i in range(3,lengP):
            vectorD = points[i] - pointA
            dotpro=dot(vectorZ,vectorD)
            if abs(dotpro) < 1e-10:
                continue
            else:
                raise ValueError('please donot make all coincident points!')
        # the transform matrix
        transA=GeTransform([[vectorX.x, vectorY.x, vectorZ.x, pointA.x],
                            [vectorX.y, vectorY.y, vectorZ.y, pointA.y],
                            [vectorX.z, vectorY.z, vectorZ.z, pointA.z]])
        invA=GeTransform([[vectorX.x, vectorX.y, vectorX.z, 0],
                        [vectorY.x, vectorY.y, vectorY.z, 0],
                        [vectorZ.x, vectorZ.y, vectorZ.z, 0]]) 
        section = transA*Section()
        for i in range(lengP):    
            pointI3d=invA*(points[i]-points[0])
            pointI2d=GeVec2d(pointI3d.x,pointI3d.y)
            section.append(pointI2d)
    return section

def _points_become_matrix(centerA: GeVec3d,centerB: GeVec3d): # 两个点确定一个位姿变换矩阵
    '''
    two points generate a transform matrix
    '''
    vectorA=centerB-centerA
    if  not isinstance(vectorA,GeVec3d):
        raise TypeError('please input proper "GeVec3d" type!')
    elif norm(vectorA)<1e-10:
        return GeTransform( ) #the norm of two point cannot equal zero
    else:
        vectorZ=vectorA*(1/norm(vectorA))
        if abs(abs(vectorZ.y)-1)<1e-10:
            vectorX=GeVec3d(1,0,0)
        elif vectorZ.x*vectorZ.z>0:
            vectorX=GeVec3d(sqrt(vectorZ.z**2/(vectorZ.x**2+vectorZ.z**2)),0,-sqrt(vectorZ.x**2/(vectorZ.x**2+vectorZ.z**2)))
        elif vectorZ.x*vectorZ.z<=0:
            vectorX=GeVec3d(sqrt(vectorZ.z**2/(vectorZ.x**2+vectorZ.z**2)),0,sqrt(vectorZ.x**2/(vectorZ.x**2+vectorZ.z**2)))
        vectorY = cross(vectorZ , vectorX)
        transA=GeTransform([[vectorX.x, vectorY.x, vectorZ.x, centerA.x],
                            [vectorX.y, vectorY.y, vectorZ.y, centerA.y],
                            [vectorX.z, vectorY.z, vectorZ.z, centerA.z]])
        return transA

def _vector_become_matrix(vectorA: GeVec3d): #一个矢量确定一个姿态变换矩阵
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
        transA=GeTransform([[vectorX.x, vectorY.x, vectorZ.x, 0],
                            [vectorX.y, vectorY.y, vectorZ.y, 0],
                            [vectorX.z, vectorY.z, vectorZ.z, 0]])
        return transA

def _judge_plane(OuterContourparts):
    # plane='XY' # default plane
    for part in OuterContourparts:
        if isinstance(part,Ellipse):
            vecotrA=GeVec3d(part.transformation._mat[0][0],part.transformation._mat[1][0],part.transformation._mat[2][0])
            vecotrB=GeVec3d(part.transformation._mat[0][1],part.transformation._mat[1][1],part.transformation._mat[2][1])
            vecotrC=cross(vecotrA,vecotrB)
            if abs(vecotrC.x)>1e-8 and abs(vecotrC.z)+abs(vecotrC.y)<1e-8:
                plane='YZ'
                return plane
            elif abs(vecotrC.y)>1e-8 and abs(vecotrC.z)+abs(vecotrC.x)<1e-8:
                plane='ZX'
                return plane
            elif abs(vecotrC.z)>1e-8 and abs(vecotrC.y)+abs(vecotrC.x)<1e-8:
                plane='XY'
                return plane
            else:
                raise ValueError('cannot judge the locate plane!')
    points=[] #take out all point in Line()
    for part in OuterContourparts:
        if isinstance(part,Line):
            for i in range(len(part.parts)):
                points.append(part.parts[i])
    pointA=points[0]
    lxl=lyl=lzl=0
    for pointi in points:
        lxl+=abs((pointi-pointA).x)
        lyl+=abs((pointi-pointA).y)
        lzl+=abs((pointi-pointA).z)
    if abs(lxl)<1e-10 and abs(lyl)>1e-10 and abs(lzl)>1e-10:
        plane='YZ'
        return plane
    elif abs(lyl)<1e-10 and abs(lxl)>1e-10 and abs(lzl)>1e-10:
        plane='ZX'
        return plane
    elif abs(lzl)<1e-10 and abs(lxl)>1e-10 and abs(lyl)>1e-10:
        plane='XY'
        return plane
    else:
        raise ValueError('cannot judge the locate plane!')

def _two_line_intersect(line1:list,line2:list):
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
    # judgeZero=lambda x: 0 if abs(x) < 1e-10 else x
    is_zero=lambda x: True if abs(x) < 1e-10 else False
    A1=-(y2-y1)
    B1=(x2-x1)
    C1=x1*y2-x2*y1
    sideC=A1*x3+B1*y3+C1
    if is_zero(sideC) and (y2-y1)**2+(x2-x1)**2 >= max((y4-y1)**2+(x4-x1)**2,(y4-y2)**2+(x4-x2)**2):
        raise ValueError('some back-lines in polygon!')
    sideD=A1*x4+B1*y4+C1
    if is_zero(sideD) and (y2-y1)**2+(x2-x1)**2 >= max((y3-y1)**2+(x3-x1)**2,(y3-y2)**2+(x3-x2)**2):
        raise ValueError('some back-lines in polygon!')
    if sideC*sideD < 0:
        twoSides1=True
    else:
        twoSides1=False
    #AB is beside line2
    A2=-(y4-y3)
    B2=(x4-x3)
    C2=x3*y4-x4*y3
    sideA=A2*x1+B2*y1+C2
    if is_zero(sideA) and (y4-y3)**2+(x4-x3)**2 >= max((y1-y3)**2+(x1-x3)**2,(y1-y4)**2+(x1-x4)**2):
        raise ValueError('some back-line in polygon!')
    sideB=A2*x2+B2*y2+C2
    if is_zero(sideB) and (y4-y3)**2+(x4-x3)**2 >= max((y2-y3)**2+(x2-x3)**2,(y2-y4)**2+(x2-x4)**2):
        raise ValueError('some back-line in polygon!')
    if sideA*sideB < 0:
        twoSides2=True
    else:
        twoSides1=False
    # two lines intersect, return True
    return twoSides1 and twoSides2

def _judge_polygon_diretion(points:list):
    '''
    anti-clockwise return True
    clockwise return False
    '''
    lenP=len(points)
    Surfacex2=0
    for i in range(lenP-1):
        Surfacex2+=points[i].x *points[i+1].y-points[i+1].x*points[i].y
    Surfacex2+=points[lenP-1].x *points[0].y-points[0].x *points[lenP-1].y
    if abs(Surfacex2)<=1e-10:
        raise ValueError('some collinear points!')
    else:
        if Surfacex2>0:
            return True
        else:
            return False

def _polygon_side_judge(points:list):
    for i in points:
        if not isinstance(i,GeVec2d):
            return points
    if  len(points) < 3:
        raise ValueError('please input 3 points at least, to compose one plane！')
    pointList=[points[0]] 
    for i in range(1,len(points)):
        if (points[i].x-pointList[len(pointList)-1].x)**2+(points[i].y-pointList[len(pointList)-1].y)**2 > 1e-10:
            pointList.append(points[i])
    if (points[-1].x-pointList[0].x)**2+(points[-1].y-pointList[0].y)**2 > 1e-10:
        pointList.append(points[0])
    lineList=[] #close lines list
    for i in range(len(pointList)-1):
        lineList.append([pointList[i],pointList[i+1]])
    lengL=len(lineList)
    for i in range(2,lengL-1):  
        if _two_line_intersect(lineList[0],lineList[i]):
            raise ValueError('some lines self-intersect in polygon!')
    for i in range(1,lengL):
        for j in range(i+2,lengL):  
            if _two_line_intersect(lineList[i],lineList[j]):
                raise ValueError('some lines self-intersect in polygon!')
    if _judge_polygon_diretion(pointList):
        return points
    else:
        points.reverse()
        return points
    # Surfacex2=0
    # lengP=lengL+1
    # for i in range(lengP-1):
    #     Surfacex2+=pointList[i].x *pointList[i+1].y-pointList[i+1].x*pointList[i].y
    # Surfacex2+=pointList[lengP-1].x *pointList[0].y-pointList[0].x *pointList[lengP-1].y
    # if abs(Surfacex2)<=1e-10:
    #     raise ValueError('points or in one line')
    # else:
    #     if Surfacex2>0:
    #         return points
    #     else:
    #         points.reverse()
    #         return points

def _point_offset(points:list): #当RuledSweep中的两点重合，自动将第二个点错开一个微小偏移
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

def _vector_to_angle(SegmentA, SegmentB): # 求两个线段之间的夹角，vectorA->vectorB满足右手定则，夹角为正
    vectorA=SegmentA[1]-SegmentA[0]
    vectorB=SegmentB[1]-SegmentB[0]
    if norm(vectorA)*norm(vectorB) < 1e-10:
        raise ValueError('two vector cannot be zero-length!')
    theta=acos(dot(vectorA,vectorB)/(norm(vectorA)*norm(vectorB)))
    vectorZ=cross(vectorA,vectorB)
    if vectorZ.z<0:
        theta=-theta
    return theta

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

class Cone(Loft):
    def __init__(self, centerA=GeVec3d(0, 0, 0), centerB=GeVec3d(0, 0, 1), radiusA=1.0, radiusB=None):
        Loft.__init__(self)
        if radiusB is None:
            radiusB = radiusA
        self.representation = 'Cone'
        transA=_points_become_matrix(centerA, centerB)
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
        section_a = Section()
        section_a.parts = [GeVec2d(0,0), GeVec2d(baseX,0), GeVec2d(baseX,baseY), GeVec2d(0,baseY)]
        section_b = translate(0,0,1) * Section()
        section_b.parts = [GeVec2d(0,0), GeVec2d(topX,0), GeVec2d(topX,topY), GeVec2d(0,topY)]
        self.parts = [section_a,section_b]

class RuledSweep(Loft): #直纹扫描
    def __init__(self, points1=[GeVec3d(0,0,0),GeVec3d(0,1,0),GeVec3d(2,0,0)], \
                    points2 = [GeVec3d(0,0,2),GeVec3d(0,2,1),GeVec3d(2,0,1)]):
        Loft.__init__(self)
        self._name = 'RuledSweep'
        if len(points1)!=len(points2):
            raise TypeError('the points of two Section must be equal!')
        points1 = _point_offset(points1)
        points2 = _point_offset(points2)
        section_a = _points_become_section(points1)
        section_b = _points_become_section(points2)
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
            section = _points_become_section(contours[i])
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
        if isinstance(points[0],GeVec3d):
            section = _points_become_section(points)
        elif isinstance(points[0],Arc) and len(points)==1:
            section = Section(points[0])
        arc = _vector_become_matrix(axis) * Arc()
        arc.scope = sweepAngle
        line =translate(center)* Line(arc)
        self.section = section
        self.trajectory = line

class Extrusion(Sweep): # 拉伸体 (直线放样) 2.0
    def __init__(self, points=[GeVec3d(1,0,0), GeVec3d(3,0,0),GeVec3d(3,2,0),GeVec3d(0,2,0)], extrusionVector=GeVec3d(1,0,1)):
        Sweep.__init__(self)
        self.representation = 'Extrusion'
        section = _points_become_section(points)
        line = Line(points[0],points[0] + extrusionVector)
        self.section = section
        self.trajectory = line

class ExtrusionPlus(Sweep): # 复杂拉伸体 2.0
    def __init__(self, contourLines=[ContourLine([Line(GeVec3d(2,-2,0),GeVec3d(2,2,0),GeVec3d(-2,2,0),GeVec3d(-2,-2,0))]),\
        ContourLine([Arc()])], extrusionVector=GeVec3d(0, 0 ,4)):
        Sweep.__init__(self)
        self.representation = 'ExtrusionPlus'
        if len(contourLines) == 0 :
            raise TypeError('ExtrusionPlus() has one ContourLine at least!')
        fetchXY=lambda point:GeVec2d(point.x, point.y) #trans GeVec3d to XoY plane, sweep direction is  Z
        OuterContour=contourLines[0]
        plane=_judge_plane(OuterContour.parts)
        # first out-coutour
        if len(contourLines)>=1: 
            if plane=='XY':
                if isinstance(OuterContour.parts[0],Line):
                    transA=translate(0,0,OuterContour.parts[0].parts[0].z)
                    invA=translate(0,0,-OuterContour.parts[0].parts[0].z)
                    center=OuterContour.parts[0].parts[0]
                elif isinstance(OuterContour.parts[0],Ellipse) or isinstance(OuterContour.parts[0],Arc):
                    transA=translate(0,0,OuterContour.parts[0].transformation._mat[2][3])
                    invA=translate(0,0,-OuterContour.parts[0].transformation._mat[2][3])
                    center=GeVec3d(OuterContour.parts[0].transformation._mat[0][3],
                                    OuterContour.parts[0].transformation._mat[1][3],
                                    OuterContour.parts[0].transformation._mat[2][3])
                else:
                    raise TypeError('Line type error!')
                agrs=[]
                for coutour in OuterContour.parts:
                    if isinstance(coutour,Line):
                        for i in range(len(coutour.parts)):
                            agrs.append(fetchXY(coutour.parts[i]))
                    elif isinstance(coutour,Ellipse) or isinstance(coutour,Arc):
                        agrs.append(invA*coutour)
                    else:
                        raise TypeError('Line type error!')
                agrs=_polygon_side_judge(agrs)
                section = transA*Section(*agrs)
            elif plane=='YZ':
                if isinstance(OuterContour.parts[0],Line):
                    transA=translate(0,0,OuterContour.parts[0].parts[0].x)
                    invA=translate(0,0,-OuterContour.parts[0].parts[0].x)
                    center=OuterContour.parts[0].parts[0]
                elif isinstance(OuterContour.parts[0],Ellipse) or isinstance(OuterContour.parts[0],Arc):
                    transA=translate(0,0,OuterContour.parts[0].transformation._mat[0][3])
                    invA=translate(0,0,-OuterContour.parts[0].transformation._mat[0][3])
                    center=GeVec3d(OuterContour.parts[0].transformation._mat[0][3],
                                    OuterContour.parts[0].transformation._mat[1][3],
                                    OuterContour.parts[0].transformation._mat[2][3])
                else:
                    raise TypeError('Line type error!')
                agrs=[]
                for coutour in OuterContour.parts:
                    if isinstance(coutour,Line):
                        coutourparts=rotate(GeVec3d(1,1,1),-2*pi/3)*coutour.parts #donot renew original para
                        for i in range(len(coutourparts)):
                            agrs.append(fetchXY(coutourparts[i]))
                    elif isinstance(coutour,Ellipse) or isinstance(coutour,Arc):
                        agrs.append(invA*rotate(GeVec3d(1,1,1),-2*pi/3)*coutour)
                    else:
                        raise TypeError('Line type error!')
                agrs=_polygon_side_judge(agrs)
                section = rotate(GeVec3d(1,1,1),2*pi/3)*transA*Section(*agrs)
            elif plane=='ZX':
                if isinstance(OuterContour.parts[0],Line):
                    transA=translate(0,0,OuterContour.parts[0].parts[0].y)
                    invA=translate(0,0,-OuterContour.parts[0].parts[0].y)
                    center=OuterContour.parts[0].parts[0]
                elif isinstance(OuterContour.parts[0],Ellipse) or isinstance(OuterContour.parts[0],Arc):
                    transA=translate(0,0,OuterContour.parts[0].transformation._mat[1][3])
                    invA=translate(0,0,-OuterContour.parts[0].transformation._mat[1][3])
                    center=GeVec3d(OuterContour.parts[0].transformation._mat[0][3],
                                    OuterContour.parts[0].transformation._mat[1][3],
                                    OuterContour.parts[0].transformation._mat[2][3])
                else:
                    raise TypeError('Line type error!')
                agrs=[]
                for coutour in OuterContour.parts:
                    if isinstance(coutour,Line):
                        coutourparts=rotate(GeVec3d(1,1,1),2*pi/3)*coutour.parts
                        for i in range(len(coutourparts)):
                            agrs.append(fetchXY(coutourparts[i]))
                    elif isinstance(coutour,Ellipse) or isinstance(coutour,Arc):
                        agrs.append(invA*rotate(GeVec3d(1,1,1),2*pi/3)*coutour)
                    else:
                        raise TypeError('Line type error!')
                agrs=_polygon_side_judge(agrs)
                section = rotate(GeVec3d(1,1,1),-2*pi/3)*transA*Section(*agrs)
            line = Line(center,center+extrusionVector)
        # multi out-contour
        for j in range(1,len(contourLines)):
            InnerContour=contourLines[j] 
            if plane=='XY':
                if isinstance(InnerContour.parts[0],Line):
                    transB=translate(0,0,InnerContour.parts[0].parts[0].z)
                    invB=translate(0,0,-InnerContour.parts[0].parts[0].z)
                    center=InnerContour.parts[0].parts[0]
                elif isinstance(InnerContour.parts[0],Ellipse) or isinstance(InnerContour.parts[0],Arc):
                    transB=translate(0,0,InnerContour.parts[0].transformation._mat[2][3])
                    invB=translate(0,0,-InnerContour.parts[0].transformation._mat[2][3])
                    center=GeVec3d(InnerContour.parts[0].transformation._mat[0][3],
                                    InnerContour.parts[0].transformation._mat[1][3],
                                    InnerContour.parts[0].transformation._mat[2][3])
                else:
                    raise TypeError('Line type error!')
                agrsB=[]
                for coutour in InnerContour.parts:
                    if isinstance(coutour,Line):
                        for i in range(len(coutour.parts)):
                            agrsB.append(fetchXY(coutour.parts[i]))
                    elif isinstance(coutour,Ellipse) or isinstance(coutour,Arc):
                        agrsB.append(invB*coutour)
                    else:
                        raise TypeError('Line type error!')
                agrsB=_polygon_side_judge(agrsB)
                sectionB = transB*Section(*agrsB)
                section=section - sectionB 
            elif plane=='YZ':
                if isinstance(InnerContour.parts[0],Line):
                    transB=translate(0,0,InnerContour.parts[0].parts[0].x)
                    invB=translate(0,0,-InnerContour.parts[0].parts[0].x)
                    center=InnerContour.parts[0].parts[0]
                elif isinstance(InnerContour.parts[0],Ellipse) or isinstance(InnerContour.parts[0],Arc):
                    transB=translate(0,0,InnerContour.parts[0].transformation._mat[0][3])
                    invB=translate(0,0,-InnerContour.parts[0].transformation._mat[0][3])
                    center=GeVec3d(InnerContour.parts[0].transformation._mat[0][3],
                                    InnerContour.parts[0].transformation._mat[1][3],
                                    InnerContour.parts[0].transformation._mat[2][3])
                else:
                    raise TypeError('Line type error!')
                agrsB=[]
                for coutour in InnerContour.parts:
                    if isinstance(coutour,Line):
                        coutourparts=rotate(GeVec3d(1,1,1),-2*pi/3)*coutour.parts
                        for i in range(len(coutourparts)):
                            agrsB.append(fetchXY(coutourparts[i]))
                    elif isinstance(coutour,Ellipse) or isinstance(coutour,Arc):
                        agrsB.append(invB*rotate(GeVec3d(1,1,1),-2*pi/3)*coutour)
                    else:
                        raise TypeError('Line type error!')
                agrsB=_polygon_side_judge(agrsB)
                sectionB = rotate(GeVec3d(1,1,1),2*pi/3)*transB*Section(*agrsB)
                section=section - sectionB 
            elif plane=='ZX':
                if isinstance(InnerContour.parts[0],Line):
                    transB=translate(0,0,InnerContour.parts[0].parts[0].y)
                    invB=translate(0,0,-InnerContour.parts[0].parts[0].y)
                    center=InnerContour.parts[0].parts[0]
                elif isinstance(InnerContour.parts[0],Ellipse) or isinstance(InnerContour.parts[0],Arc):
                    transB=translate(0,0,InnerContour.parts[0].transformation._mat[1][3])
                    invB=translate(0,0,-InnerContour.parts[0].transformation._mat[1][3])
                    center=GeVec3d(InnerContour.parts[0].transformation._mat[0][3],
                                    InnerContour.parts[0].transformation._mat[1][3],
                                    InnerContour.parts[0].transformation._mat[2][3])
                else:
                    raise TypeError('Line type error!')
                agrsB=[]
                for coutour in InnerContour.parts:
                    if isinstance(coutour,Line):
                        coutourparts=rotate(GeVec3d(1,1,1),2*pi/3)*coutour.parts
                        for i in range(len(coutourparts)):
                            agrsB.append(fetchXY(coutourparts[i]))
                    elif isinstance(coutour,Ellipse) or isinstance(coutour,Arc):
                        agrsB.append(invB*rotate(GeVec3d(1,1,1),2*pi/3)*coutour)
                    else:
                        raise TypeError('Line type error!')
                agrsB=_polygon_side_judge(agrsB)
                sectionB = rotate(GeVec3d(1,1,1),-2*pi/3)*transB*Section(*agrsB)
                section=section - sectionB # 
        # compat Extrusion
        if len(contourLines)==1:
            OuterContour=contourLines[0] 
            if len(OuterContour.parts)==1 and isinstance(OuterContour.parts[0],Line):# only the point section use
                lines=OuterContour.parts[0]
                section = _points_become_section(lines.parts)
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
        leanSection = lambda pointY,pointX,theta:rotate(Vec3(0,0,1),atan2(pointY.y-pointX.y,pointY.x-pointX.x)+theta)
        lengP=len(points)
        lineList=[] # segment
        for i in range(lengP-1):
            lineList.append([points[i],points[i+1]])
        sectionList=[translate(points[0])*leanSection(points[1],points[0],0)*section]
        for i in range(1,lengP-1):
            theta=_vector_to_angle(lineList[i-1],lineList[i])/2
            matrix=GeTransform([[1/cos(theta),0,0,0],
                                [0,1/cos(theta),0,0],
                                [0,0,1,0]])
            sectioni=translate(points[i])*matrix*leanSection(points[i],points[i-1],theta)*section
            sectionList.append(sectioni)
        sectionList.append(translate(points[lengP-1])*leanSection(points[lengP-1],points[lengP-2],0)*section)
        self.parts = [*sectionList]

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

def interact_liner(data, context): # place method
    if 'interact_status' not in context:
        context['interact_status'] = 'firstButton'
    data = copy.deepcopy(data)
    if context['action'] == 'left down':
        if context['interact_status'] == 'firstButton':
            context['interact_status'] = 'secondButton'
            context['\tplace_1'] = context['point']
        elif context['interact_status'] == 'secondButton':
            p1 = context['\tplace_1']
            p2 = context['point']
            v12 = p2 - p1
            v12_norm = norm(v12)
            if v12_norm != 0.0:
                angle_z = acos(v12.z/v12_norm)
                # if angle_z == 0.0:
                if abs(angle_z) < 1e-10:
                    data.transformation *= rotate(GeVec3d(0,1,0), -pi/2)
                # elif angle_z == pi:
                elif abs(abs(angle_z)-pi) < 1e-10:
                    data.transformation *= rotate(GeVec3d(0,1,0), pi/2)
                else:
                    r_xy = sqrt(v12.x**2 + v12.y**2)
                    angle_xy = acos(v12.x/r_xy)
                    if v12.y < 0.0:
                        angle_xy = -angle_xy
                    data.transformation *= rotate(GeVec3d(0,0,1), angle_xy) * rotate(GeVec3d(0,1,0), angle_z-pi/2)
            data[data['LinearComponentLengthKey']] = v12_norm
            data.replace()
            place_to(data, translate(context['\tplace_1']))
            context['interact_status'] = 'firstButton'
        else:
            pass
    elif context['action'] == 'right down':
        exit_tool()
    elif context['action'] == 'mouse movement':
        if context['interact_status'] == 'firstButton':
            dynamic_preview(translate(context['point']) * data)
        elif context['interact_status'] == 'secondButton':
            dynamic_preview(Line(context['\tplace_1'],context['point']))
        else:
            pass
    else:
        print(context)
    return context

def rotation_to(v):
    '''
    旋转至与V同向
    '''
    transformation = GeTransform()  #transformation assign identity matrix
    v12_norm = norm(v)
    if v12_norm != 0.0: 
        angle_z = acos(v.z/v12_norm)
        # if angle_z == 0.0:
        if abs(angle_z) < 1e-10:
            transformation *= rotate(GeVec3d(0,1,0), -pi/2)
        # elif angle_z == pi:
        elif abs(abs(angle_z)-pi) < 1e-10:
            transformation *= rotate(GeVec3d(0,1,0), pi/2)
        else:
            r_xy = sqrt(v.x**2 + v.y**2)
            angle_xy = acos(v.x/r_xy)
            if v.y < 0.0:
                angle_xy = -angle_xy
            transformation *= rotate(GeVec3d(0,0,1), angle_xy) * rotate(GeVec3d(0,1,0), angle_z-pi/2)      
    return transformation

def interact_multi_point(data, context):
    if 'interact_status' not in context:
        context['interact_status'] = 'firstButton'
    data = copy.deepcopy(data)
    if context['action'] == 'left down':
        if context['interact_status'] == 'firstButton':
            context['interact_status'] = 'secondButton'
            context['MultiPointComponentKey'] = [context['point']]
            data[data['MultiPointComponentKey']] = context['MultiPointComponentKey']
        elif context['interact_status'] == 'secondButton':
            context['MultiPointComponentKey'].append(context['point'])
        else:
            pass
    elif context['action'] == 'right down':
        data[data['MultiPointComponentKey']] = context['MultiPointComponentKey']
        data.replace()
        place_to(data, GeTransform())
        exit_tool()
    elif context['action'] == 'mouse movement':
        if not data['MultiPointComponentKey'] in data:
            return context
        if not 'MultiPointComponentKey' in context:
            return context
        context['MultiPointComponentKey'].append(context['point'])
        data[data['MultiPointComponentKey']] = context['MultiPointComponentKey']
        data.replace()
        dynamic_preview(data)
        del context['MultiPointComponentKey'][-1]
        data[data['MultiPointComponentKey']] = context['MultiPointComponentKey']
    else:
        print(context)
    return context

def interact_rotate(data, context):
    if 'interact_status' not in context:
        context['interact_status'] = 'firstButton'
    data = copy.deepcopy(data)
    if context['action'] == 'left down':
        if context['interact_status'] == 'firstButton':
            context['interact_status'] = 'secondButton'
            context['\tplace_1'] = context['point']
        elif context['interact_status'] == 'secondButton':
            p1 = context['\tplace_1']
            p2 = context['point']
            v12 = p2 - p1
            v12_norm = norm(v12)
            if v12_norm != 0.0: 
                angle_z = acos(v12.z/v12_norm)
                # if angle_z == 0.0:
                if abs(angle_z) < 1e-10:
                    data.transformation *= rotate(GeVec3d(0,1,0), -pi/2)
                # elif angle_z == pi:
                elif abs(abs(angle_z)-pi) < 1e-10:
                    data.transformation *= rotate(GeVec3d(0,1,0), pi/2)
                else:
                    r_xy = sqrt(v12.x**2 + v12.y**2)
                    angle_xy = acos(v12.x/r_xy)
                    if v12.y < 0.0:
                        angle_xy = -angle_xy
                    data.transformation *= rotate(GeVec3d(0,0,1), angle_xy) * rotate(GeVec3d(0,1,0), angle_z-pi/2)
            data.replace()
            place_to(data, translate(context['\tplace_1']))
            context['interact_status'] = 'firstButton'
        else:
            pass
    elif context['action'] == 'right down':
        exit_tool()
    elif context['action'] == 'mouse movement':
        if context['interact_status'] == 'firstButton':
            dynamic_preview(translate(context['point']) * data)
        elif context['interact_status'] == 'secondButton':
            dynamic_preview(Line(context['\tplace_1'],context['point']))
        else:
            pass
    else:
        print(context)
    return context

class TwoPointPlace:
    def linearize(data, paramStr):
        data['LinearComponentLengthKey'] = paramStr
        # data[PARACMPT_KEYWORD_INTERACT] = interactLiner
        data[PARACMPT_KEYWORD_INTERACT]=Attr(UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_INTERACT_LINER), member=True)

class RotationPlace:
    def RotationFunction(data):
        data[PARACMPT_KEYWORD_INTERACT]=Attr(UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_INTERACT_ROTATE), member=True)
        # data[PARACMPT_KEYWORD_INTERACT] = interactRotate

class MultiPointPlace:
    def MultiPointFunction(data, paramStr):
        data['MultiPointComponentKey'] = paramStr
        # data[PARACMPT_KEYWORD_INTERACT] = interactMultiPoint
        data[PARACMPT_KEYWORD_INTERACT]=Attr(UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_INTERACT_MULTIPOINT), member=True)


    # @property
    # def replaceMethod(self):
    #     return self._data['replace'].value
    # @replaceMethod.setter
    # def replaceMethod(self, value):
    #     if isinstance(value, FunctionType):
    #         self['replace'] = _Property('')
    #         self['replace'].value = _Operator()
    #         self['replace'].value._methodName = value.__name__
    #         self['replace'].value._filePath = __import__(
    #             value.__module__).__file__
    #         self['replace'].value._this = self
    # @property
    # def dynamicMethod(self):
    #     return self._data['\tPLACE_TOOL_OPERATOR_DYNAMIC']
    # @dynamicMethod.setter
    # def dynamicMethod(self, value):
    #     if isinstance(value, FunctionType):
    #         self._data['\tPLACE_TOOL_OPERATOR_DYNAMIC'] = _Property('')
    #         self._data['\tPLACE_TOOL_OPERATOR_DYNAMIC'].value = _Operator()
    #         self._data['\tPLACE_TOOL_OPERATOR_DYNAMIC'].value._methodName = value.__name__
    #         self._data['\tPLACE_TOOL_OPERATOR_DYNAMIC'].value._filePath = __import__(
    #             value.__module__).__file__
    #         self._data['\tPLACE_TOOL_OPERATOR_DYNAMIC'].value._this = self
    # @property
    # def placeMethod(self):
    #     return self._data['\tPLACE_TOOL_OPERATOR_PLACE'].value
    # @placeMethod.setter
    # def placeMethod(self, value):
    #     if isinstance(value, FunctionType):
    #         self._data['\tPLACE_TOOL_OPERATOR_PLACE'] = _Property('')
    #         self._data['\tPLACE_TOOL_OPERATOR_PLACE'].value = _Operator()
    #         self._data['\tPLACE_TOOL_OPERATOR_PLACE'].value._methodName = value.__name__
    #         self._data['\tPLACE_TOOL_OPERATOR_PLACE'].value._filePath = __import__(
    #             value.__module__).__file__
    #         self._data['\tPLACE_TOOL_OPERATOR_PLACE'].value._this = self
    # @property
    # def SuspendplaceMethod(self):
    #     return self._data['\tPLACE_TOOL_OPERATOR_SUSPENDPLACE'].value
    # @SuspendplaceMethod.setter
    # def SuspendplaceMethod(self, value):
    #     if isinstance(value, FunctionType):
    #         self._data['\tPLACE_TOOL_OPERATOR_SUSPENDPLACE'] = _Property('')
    #         self._data['\tPLACE_TOOL_OPERATOR_SUSPENDPLACE'].value = _Operator()
    #         self._data['\tPLACE_TOOL_OPERATOR_SUSPENDPLACE'].value._methodName = value.__name__
    #         self._data['\tPLACE_TOOL_OPERATOR_SUSPENDPLACE'].value._filePath = __import__(
    #             value.__module__).__file__
    #         self._data['\tPLACE_TOOL_OPERATOR_SUSPENDPLACE'].value._this = self
    # @property
    # def LinearComponentLengthKey(self):
    #     if '\tLinearComponentLength' in self._data:
    #         return self._data['\tLinearComponentLength'].value
    # @LinearComponentLengthKey.setter
    # def LinearComponentLengthKey(self, value):
    #     self._data['\tLinearComponentLength'] = _Property('')
    #     self._data['\tLinearComponentLength'].value = value
    # @property
    # def MultiPointKey(self):
    #     if '\tMultiPointKey' in self._data:
    #         return self._data['\tMultiPointKey'].value
    # @MultiPointKey.setter
    # def MultiPointKey(self, value):
    #     self._data['\tMultiPointKey'] = _Property('')
    #     self._data['\tMultiPointKey'].value = value

Vec3 = GeVec3d
Vec2 = GeVec2d
combine = Combine
LineString = Line
rotation = rotate
translation = translate
launchData = place
createGeometry = create_geometry
to_section = _points_become_section
BPParametricComponent = UnifiedModule(PARACMPT_PARAMETRIC_COMPONENT)