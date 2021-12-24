# Copyright (C), 2019-2028, Beijing GLory PKPM Tech. Co., Ltd.
# Brief: PKPM-BIMBase Python二次开发SDK与参数化组件功能。
# Author: YouQi
# Date: 2021/05/06
from .serialization import *
from .runtime import *
path = sys.path[-1]
if len(sys.path[-1]) > 1 and sys.path[-1][0]=='?':
    version = Size_t(sys.path[-1][1:])
    sys.path.pop()
    isService = True
else:
    version = UnifiedFunction('BPParametricComponent', 'get_version')()
    isService = False
if version > Size_t(18446497929133883392):
    raise RuntimeError('current pyp3d version is outdated, please get update!')
if version == Size_t(18446497929133883392):
    from .v18446497929133883392 import *
elif version == Size_t(18446497929133817856):
    from .v18446497929133817856 import *
else:
    raise RuntimeError('there is no matched pyp3d version, please install the pyp3d that correspond BIMBase!')
if isService: start_runtime_service()
