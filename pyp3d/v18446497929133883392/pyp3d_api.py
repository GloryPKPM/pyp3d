# Copyright (C),  2019-2028,  Beijing GLory PKPM Tech. Co.,  Ltd.
# Brief: PKPM-BIMBase Python二次开发SDK与参数化组件功能。
# Author: YouQi,YanYinji
# Date: 2021/11

from .pyp3d_convention import *
from .pyp3d_data import *
from .pyp3d_matrix import *
from .pyp3d_calculation import *
from .pyp3d_component import *
from .pyp3d_compat import *
import copy,  math,  sys,  time
from math import *


class TwoPointPlace:
    def linearize(data,  paramStr):
        data['LinearComponentLengthKey'] = paramStr
        # data[PARACMPT_KEYWORD_INTERACT] = interactLiner
        data[PARACMPT_KEYWORD_INTERACT]=Attr(UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT,  PARACMPT_INTERACT_LINER),  member=True)

class RotationPlace:
    def RotationFunction(data):
        data[PARACMPT_KEYWORD_INTERACT] = Attr(UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT,  PARACMPT_INTERACT_ROTATE),  member=True)
        # data[PARACMPT_KEYWORD_INTERACT] = interactRotate

class MultiPointPlace:
    def MultiPointFunction(data,  paramStr):
        data['MultiPointComponentKey'] = paramStr
        # data[PARACMPT_KEYWORD_INTERACT] = interactMultiPoint
        data[PARACMPT_KEYWORD_INTERACT]=Attr(UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT,  PARACMPT_INTERACT_MULTIPOINT),  member=True)
    # @property
    # def replaceMethod(self):
    #     return self._data['replace'].value
    # @replaceMethod.setter
    # def replaceMethod(self,  value):
    #     if isinstance(value,  FunctionType):
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
    # def dynamicMethod(self,  value):
    #     if isinstance(value,  FunctionType):
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
    # def placeMethod(self,  value):
    #     if isinstance(value,  FunctionType):
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
    # def SuspendplaceMethod(self,  value):
    #     if isinstance(value,  FunctionType):
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
    # def LinearComponentLengthKey(self,  value):
    #     self._data['\tLinearComponentLength'] = _Property('')
    #     self._data['\tLinearComponentLength'].value = value
    # @property
    # def MultiPointKey(self):
    #     if '\tMultiPointKey' in self._data:
    #         return self._data['\tMultiPointKey'].value
    # @MultiPointKey.setter
    # def MultiPointKey(self,  value):
    #     self._data['\tMultiPointKey'] = _Property('')
    #     self._data['\tMultiPointKey'].value = value

# ---------------------------------------------------------------------------------
def place(noumenon:Noumenon): #通过布置工具放置组件
    if get_global_variable('is_script_to_josn'):
        set_global_variable('script_to_josn', noumenon)
    else:
        path=sys.argv[0]
        depend = DependentFile()
        depend.readFile(sys.argv[0])
        noumenon[PARACMPT_KEYWORD_DEPENDENT_FILE] = depend
        UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT,  PARACMPT_PLACE_INSTANCE)(noumenon,path)

def place_to(noumenon:Noumenon,  transform:GeTransform):#在特定位置布置几何体
    path=sys.argv[0]
    '''
    appoint position where geometry place to
    '''
    depend = DependentFile()
    depend.readFile(sys.argv[0])
    noumenon[PARACMPT_KEYWORD_DEPENDENT_FILE] = depend
   
    UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT,  PARACMPT_PLACE_INSTANCE_TO)(noumenon,  transform, path)

def replace_noumenon(noumenon:Noumenon,instancekey:P3DInstanceKey):#重生成本体
    '''
    replace noumenon
    '''
    if not isinstance(noumenon,  Noumenon):
        raise TypeError('input parameter error,  please input "Noumenon"!')
    if not isinstance(instancekey,  P3DInstanceKey):
        raise TypeError('input parameter error,  please input "P3DInstanceKey"!')
    
    UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT,  PARACMPT_REPLACE_NOUMENON)(noumenon,instancekey)
    

def delete_entity(**kwargs):#删除当前工程中符合条件的entity 
    '''
    delete all "entity" in present project which meet the conditions
    '''
    if len(kwargs)==0:
        raise ValueError('please input the range of "entityid"!\n')
    UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_DELETE_ENTITY)(kwargs)

def delete_one_entity(entityid:P3DEntityId):#删除当前工程中的某一个entity 
    '''
    delete someone "entity" in present project which meet the conditions
    '''
    if not (isinstance(entityid,  P3DEntityId)):
        raise TypeError('input parameter error,  please input type of "_P3DEntityId"!')
    UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_DELETE_ONE_ENTITY)(entityid)

def get_entity_property(**kwargs)->list: #返回包含当前工程符合条件的entityid的列表
    '''
    return list of "entityid" in current project which meet the condition
    '''
    res = UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_GET_ENTITY_PROPERTY)(kwargs)
    if len(res)==0:
        raise ValueError('there is no proper "entity",  please revise the condition\n')
        # return res
    else:
        return res
        
def get_entityid_from_boxselection()->list: #返回当前工程中框选的entityid的列表
    '''
    return the boxselected "entityid" list in current project 
    '''
    res = UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_GET_ENTITYID_FROM_BOXSELECTION)()
    if len(res)==0:
        raise ValueError('No entity is selected,please choice again\n')
       
    else:
        return res

def set_entity_property(**kwargs)->list: #把当前工程符合条件的所有entity的属性修改为传入的条件
    '''
    change the attributes of all entities that meet the conditions of the current project to the passed in conditions
    '''
    for k, v in kwargs.items():
        if k == 'schemaname' or k =='classname':
            raise TypeError('you can not change "schemaname" and "classname"!\n')
    UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_SET_ENTITY_PROPERTY)(kwargs)

def create_instance_instancekey(schemaName:str, className:str)->P3DInstanceKey:#根据schemaname 和 classname创建instance并返回instancekey
    '''
    using schemaname and classname genetate 'instance',  return instancekey
    '''
    if not(isinstance(schemaName,  str) or isinstance(className, str)):
        raise TypeError('input parameter error,  please input string!')
    return UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_CREATE_INSTANCE_INSTANCEKEY)(schemaName, className)

def delete_instance_byinstancekey(instancekey:P3DInstanceKey):#根据instancekey删除instance
    '''
    delete 'Instance',  using instancekey
    '''
    if not isinstance(instancekey,  P3DInstanceKey):
        raise TypeError('input parameter error,  please input "P3DInstanceKey"!')
    UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_DELETE_INSTANCE_BYINSTANCEKEY)(instancekey)

def bind_entity_instance(entityid:P3DEntityId, instancekey:P3DInstanceKey):#将entity和instance进行绑定
    '''
    binding Entity and Instance
    '''
    if not (isinstance(entityid,  P3DEntityId) or isinstance(instancekey, P3DInstanceKey)):
        raise TypeError('input parameter error,  please input "_P3DInstanceKey"!')
    UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_BIND_ENTITY_INSTANCE)(entityid, instancekey)

def removebind_entity_instance(entityid:P3DEntityId, instancekey:P3DInstanceKey):#将entity和instance的绑定关系解绑
    '''
    remove binding Entity and Instance
    '''
    if not (isinstance(entityid,  P3DEntityId) or isinstance(instancekey, P3DInstanceKey)):
        raise TypeError('input parameter error,  please input "_P3DEntityId" "_P3DInstanceKey"!')
    UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_REMOVEBIND_ENTITY_INSTANCE)(entityid, instancekey)

def get_allbinding_entity_from_instance(instancekey:P3DInstanceKey):#查询与instance绑定的所有entity
    '''
    query all entity that binding instance
    '''
    if not isinstance(instancekey, P3DInstanceKey):
        raise TypeError('input parameter error,  please input "P3DInstanceKey"!')
    return UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_GET_ALLBINDING_ENTITY_FROM_INSTANCE)(instancekey)  

def get_all_instancekey()->list:#获取当前工程中所有的instance，返回包含P3DInstanceKey的列表
    '''
    lookup all instance in current project,  return P3DInstanceKey list
    '''
    return UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_GET_ALL_INSTANCEKEY)()  

def get_modelid_from_instance(instancekey:P3DInstanceKey)->P3DModelId:#获取与P3DInstance绑定的Entity所在的Model，返回modelid
    '''
    get the model of the entity which is bound to instance, return modelid
    '''
    if not isinstance(instancekey, P3DInstanceKey):
        raise TypeError('input parameter error,  please input "P3DInstanceKey"!')
    return UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_GET_MODELID_FROM_INSTANCE)(instancekey) 

def get_instancekey_from_entity(entityid:P3DEntityId)->P3DInstanceKey:#查询与entity绑定的instance,  并返回instancekey
    '''
    get the instance bound to entity and return instancekey
    '''
    if not isinstance(entityid, P3DEntityId):
        raise TypeError('input parameter error,  please input "P3DEntityId"!')
    return UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_GET_INSTANCEKEY_FROM_ENTITY)(entityid) 
 
def get_noumenon_from_instancekey(instancekey:P3DInstanceKey)->Noumenon:#根据instancekey返回noumenon
    '''
    get noumenon from instancekey
    '''
    if not isinstance(instancekey, P3DInstanceKey):
        raise TypeError('input parameter error,  please input "P3DInstanceKey"!')
    return UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_GET_NOUMENON_FROM_INSTANCEKEY)(instancekey)    

def get_modelid_entityid_relation()->dict:#返回当前的工程中AssociateModel_modelid中对应的entityid, ModelInfo_modelid中对应的entityid
                                          #以及ModelInfo_modelid 与AssociateModel_modelid的对应关系
    '''
    return the dict of  relationship of ModelInfo_modelid and entityid, 
    relationship of AssociateModel_modelid and entityid, 
    relationship of ModelInfo_modelid and AssociateModel_modelid,  in present project
    '''
    res = UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_GET_MODELID_ENTITYID_RELATION)()
    return {'ModelInfo_modelid_AssociateModel_modelid': res[0], 
            'ModelInfo_modelid_entityid': res[1], 
            'AssociateModel_modelid_entityid': res[2]}  
    
def create_geometry(noumenon:Noumenon):#在全局坐标系的原点创建一个几何体
    '''
    create a geometry at the origin of the global coordinate system
    '''
    return UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT,  PARACMPT_CREATE_GEOMETRY)(noumenon)

def create_material(name:str,  **kw)->P3DMaterial:#创建材质库, 返回P3DMateria对象
    '''
    create a material library and return the P3DMaterial object
    '''
    kw['Name'] = name
    mat = P3DMaterial(kw)
    UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT,  PARACMPT_CREATE_MATERIAL)(mat)
    return mat

def exit_tool():#退出布置工具
    '''
    exit layout tools
    '''
    UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT,  PARACMTP_PLACE_TOOL_EXIT)()

def get_view_scale(point:GeVec3d):#获取视口旋转矩阵，世界坐标转视口坐标，视口比例
    '''
   
    '''
  
    res = UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_GET_VIEW_SCALE)(point)
    return res
 
def dynamic_preview(noumenon:Noumenon): #动态预览显示
    '''
    dynamic preview display
    '''
    UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT,  PARACMTP_PLACE_TOOL_DYNAMIC)(noumenon)

def pack_to_bfa(path:str,  noumenon:Noumenon,  files:list=[]): #打包bfa文件
    '''
    package BFA files
    '''
    UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT,  PARACMPT_PACK_BFA)(path,  noumenon,  files)

def interact_liner(data:P3DData,  context:dict): # 两点布置工具（也称线性布置工具）
    '''
    two point layout tool (also known as linear layout tool)
    '''
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
            #v12_norm=rotation_to(v12) #带入函数
            v12_norm = norm(v12)
            if v12_norm != 0.0:
                angle_z = acos(v12.z/v12_norm)
                # if angle_z == 0.0:
                if abs(angle_z) < 1e-10:
                    data.transformation *= rotate(GeVec3d(0, 1, 0),  -pi/2)
                # elif angle_z == pi:
                elif abs(abs(angle_z)-pi) < 1e-10:
                    data.transformation *= rotate(GeVec3d(0, 1, 0),  pi/2)
                else:
                    r_xy = sqrt(v12.x**2 + v12.y**2)
                    angle_xy = acos(v12.x/r_xy)
                    if v12.y < 0.0:
                        angle_xy = -angle_xy
                    data.transformation *= rotate(GeVec3d(0, 0, 1),  angle_xy) * rotate(GeVec3d(0, 1, 0),  angle_z-pi/2)
            data[data['LinearComponentLengthKey']] = v12_norm
            data.replace()
            place_to(data,  translate(context['\tplace_1']))
            context['interact_status'] = 'firstButton'
        else:
            pass
    elif context['action'] == 'right down':
        exit_tool()
    elif context['action'] == 'mouse movement':
        if context['interact_status'] == 'firstButton':
            dynamic_preview(translate(context['point']) * data)
        elif context['interact_status'] == 'secondButton':
            dynamic_preview(Line(context['\tplace_1'], context['point']))
        else:
            pass
    else:
        print(context)
    return context

def interact_multi_point(data:P3DData,  context:dict):#多点布置工具
    '''
    multipoint layout tool
    '''
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
        place_to(data,  GeTransform())
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

def interact_rotate(data:P3DData,  context:dict):#旋转布置工具
    '''
    rotate layout tool
    '''
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
                    data.transformation *= rotate(GeVec3d(0, 1, 0),  -pi/2)
                # elif angle_z == pi:
                elif abs(abs(angle_z)-pi) < 1e-10:
                    data.transformation *= rotate(GeVec3d(0, 1, 0),  pi/2)
                else:
                    r_xy = sqrt(v12.x**2 + v12.y**2)
                    angle_xy = acos(v12.x/r_xy)
                    if v12.y < 0.0:
                        angle_xy = -angle_xy
                    data.transformation *= rotate(GeVec3d(0, 0, 1),  angle_xy) * rotate(GeVec3d(0, 1, 0),  angle_z-pi/2)
            data.replace()
            place_to(data,  translate(context['\tplace_1']))
            context['interact_status'] = 'firstButton'
        else:
            pass
    elif context['action'] == 'right down':
        exit_tool()
    elif context['action'] == 'mouse movement':
        if context['interact_status'] == 'firstButton':
            dynamic_preview(translate(context['point']) * data)
        elif context['interact_status'] == 'secondButton':
            dynamic_preview(Line(context['\tplace_1'], context['point']))
        else:
            pass
    else:
        print(context)
    return context

# pyp3d_api
launchData = place
createGeometry = create_geometry

def get_line_from_curvearray(entityid:P3DEntityId):# 通过entityid返回curvearray转换的line
    '''
    get line from entityid, only apply to curvearray
    '''
    if not isinstance(entityid, P3DEntityId):
    # if not isinstance(entityid, int):
        raise TypeError('input parameter error,  please input "entityid"!')
    para = UnifiedFunction(PARACMPT_PARAMETRIC_COMPONENT, PARACMPT_GET_LINE_FROM_CURVEARRAY)(entityid)
    return Line(para)

# 内置基本曲线
def oval(t): #椭圆
    a=300
    b=200
    return Vec3(a*cos(t),b*sin(t),0)

def hyperbola(t): #双曲线
    a=1
    b=1
    return Vec3(a*1/cos(t),b*tan(t),0)

def parabola(t): #抛物线
    c=1
    a=0.3
    return Vec3(2*c*t, a*t*t,0)

def spiral_line_out(t)->Vec3: #螺旋线
    k=0.1
    return Vec3(t*cos(k*t),t*sin(k*t),0)

def spiral_line_up(t)->Vec3:
    c=100
    return Vec3(c*cos(t/10),c*sin(t/10),t)

def cycloid(t): #摆线
    r=100
    x=r*(t-sin(t))
    y=r*(1-cos(t))
    return Vec3(x,y,0)


