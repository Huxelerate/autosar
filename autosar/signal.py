from autosar.element import Element

class SystemSignalV3(Element):
    def __init__(self,name,dataTypeRef,initValueRef,length,desc=None,parent=None):
        super().__init__(name,parent)
        self.dataTypeRef=dataTypeRef
        self.initValueRef=initValueRef
        self.length=length
        self.desc=desc
        self.parent=parent

    def asdict(self):
        data={'type': self.__class__.__name__,'name':self.name,
              'dataTypeRef': self.dataTypeRef,
              'initValueRef': self.initValueRef,
              'length': self.length
              }
        if self.desc is not None: data['desc']=self.desc
        return data

class SystemSignalV4(Element):
    def __init__(self,name,dynamic_length=False,parent=None):
        super().__init__(name,parent)
        self.dynamic_length = dynamic_length

    def asdict(self):
        data={
            'type': self.__class__.__name__,
            'name':self.name,
            'dynamic_length': self.dynamic_length
        }
        return data

class SystemSignalGroup(Element):
    def __init__(self, name, systemSignalRefs=None,parent=None):
        super().__init__(name,parent)
        if isinstance(systemSignalRefs,list):
            self.systemSignalRefs=systemSignalRefs
        else:
            self.systemSignalRefs=[]

class ISignalV4(Element):
    def __init__(
        self,
        name,
        parent,
        adminData=None,
        dataTransformations=None,
        dataTypePolicy=None,
        props=None,
        iSignalType=None,
        initValue=None,
        length=None,
        networkRepresentationProps=None,
        systemSignalRef=None,
        timeoutSubstitutionValue=None,
        transformationISignalPropss=None
    ):
        super().__init__(
            name=name,
            parent=parent,
            adminData=adminData
        )
        self.dataTransformations = dataTransformations
        self.dataTypePolicy = dataTypePolicy
        self.props = props
        self.type = iSignalType
        self.initValue = initValue
        self.length = length
        self.networkRepresentationProps = networkRepresentationProps
        self.systemSignalRef = systemSignalRef
        self.timeoutSubstitutionValue = timeoutSubstitutionValue
        self.transformationISignalPropss = transformationISignalPropss

class ISignalGroup(Element):
    def __init__(
            self,
            name,
            parent,
            adminData=None,
            comBasedSignalGroupTransformations=None,
            iSignalRefs=None,
            systemSignalGroupRef=None,
            transformationISignalPropss=None
    ):
        super().__init__(
            name=name,
            parent=parent,
            adminData=adminData
        )
        self.comBasedSignalGroupTransformations = comBasedSignalGroupTransformations
        self.iSignalRefs = iSignalRefs
        self.systemSignalGroupRef = systemSignalGroupRef
        self.transformationISignalPropss = transformationISignalPropss
