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
    def __init__(
        self,
        name,
        systemSignalRefs=None,
        transformingSystemSignalRef=None,
        parent=None
    ):
        super().__init__(name,parent)
        if isinstance(systemSignalRefs,list):
            self.systemSignalRefs=systemSignalRefs
        else:
            self.systemSignalRefs=[]
        self.transformingSystemSignalRef=transformingSystemSignalRef

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
        initValueRef=None,
        length=None,
        networkRepresentationProps=None,
        systemSignalRef=None,
        timeoutSubstitutionValue=None,
        timeoutSubstitutionValueRef=None,
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
        self.initValueRef = initValueRef
        self.length = length
        self.networkRepresentationProps = networkRepresentationProps
        self.systemSignalRef = systemSignalRef
        self.timeoutSubstitutionValue = timeoutSubstitutionValue
        self.timeoutSubstitutionValueRef = timeoutSubstitutionValueRef
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

class DataTransformationRefConditional():
    def __init__(self, dataTransformationRef=None, variationPoint=None):
        self.dataTransformationRef = dataTransformationRef
        self.variationPoint = variationPoint

class ISignalProps():
    def __init__(self, handleOutOfRange=None):
        self.handleOutOfRange = handleOutOfRange

class TransformationISignalProps():
    def __init__(
        self,
        csErrorReaction=None,
        dataPrototypeTransformationPropss=None,
        transformerRef=None
    ):
        self.csErrorReaction = csErrorReaction
        self.dataPrototypeTransformationPropss = dataPrototypeTransformationPropss
        self.transformerRef = transformerRef

class EndToEndTransformationISignalPropsConditional(TransformationISignalProps):
    def __init__(
        self,
        csErrorReaction=None,
        dataPrototypeTransformationPropss=None,
        transformerRef=None,
        dataIds=None,
        dataLength=None,
        maxDataLength=None,
        minDataLength=None,
        sourceId=None,
        variationPoint=None
    ):
        super().__init__(
            csErrorReaction=csErrorReaction,
            dataPrototypeTransformationPropss=dataPrototypeTransformationPropss,
            transformerRef=transformerRef
        )
        self.dataIds = dataIds
        self.dataLength = dataLength
        self.maxDataLength = maxDataLength
        self.minDataLength = minDataLength
        self.sourceId = sourceId
        self.variationPoint = variationPoint

class SomeipTransformationISignalPropsConditional(TransformationISignalProps):
    def __init__(
        self,
        csErrorReaction=None,
        dataPrototypeTransformationPropss=None,
        transformerRef=None,
        implementsLegacyStringSerialization=None,
        implementsSomeipStringHandling=None,
        interfaceVersion=None,
        isDynamicLengthFieldSize=None,
        messageType=None,
        sessionHandlingSr=None,
        sizeOfArrayLengthFields=None,
        sizeOfStringLengthFields=None,
        sizeOfStructLengthFields=None,
        sizeOfUnionLengthFields=None,
        tlvDataIds=None,
        tlvDataId0Refs=None,
        tlvDataIdDefinitionRefs=None,
        variationPoint=None
    ):
        super().__init__(
            csErrorReaction=csErrorReaction,
            dataPrototypeTransformationPropss=dataPrototypeTransformationPropss,
            transformerRef=transformerRef
        )
        self.implementsLegacyStringSerialization = implementsLegacyStringSerialization
        self.implementsSomeipStringHandling = implementsSomeipStringHandling
        self.interfaceVersion = interfaceVersion
        self.isDynamicLengthFieldSize = isDynamicLengthFieldSize
        self.messageType = messageType
        self.sessionHandlingSr = sessionHandlingSr
        self.sizeOfArrayLengthFields = sizeOfArrayLengthFields
        self.sizeOfStringLengthFields = sizeOfStringLengthFields
        self.sizeOfStructLengthFields = sizeOfStructLengthFields
        self.sizeOfUnionLengthFields = sizeOfUnionLengthFields
        self.tlvDataIds = tlvDataIds
        self.tlvDataId0Refs = tlvDataId0Refs
        self.tlvDataIdDefinitionRefs = tlvDataIdDefinitionRefs
        self.variationPoint = variationPoint

class UserDefinedTransformationISignalPropsConditional(TransformationISignalProps):
    def __init__(
        self,
        csErrorReaction=None,
        dataPrototypeTransformationPropss=None,
        transformerRef=None,
        userDefinedTransformationProps=None,
        variationPoint=None
    ):
        super().__init__(
            csErrorReaction=csErrorReaction,
            dataPrototypeTransformationPropss=dataPrototypeTransformationPropss,
            transformerRef=transformerRef
        )
        self.userDefinedTransformationProps = userDefinedTransformationProps
        self.variationPoint = variationPoint

class TlvDataIdDefinition():
    def __init__(
        self,
        id=None,
        tlvArgumentRef=None,
        tlvImplementationDataTypeElementRef=None,
        tlvRecordElementRef=None,
    ):
        self.id = id
        self.tlvArgumentRef = tlvArgumentRef
        self.tlvImplementationDataTypeElementRef = tlvImplementationDataTypeElementRef
        self.tlvRecordElementRef = tlvRecordElementRef

class DataPrototypeTransformationProps():
    def __init__(
        self,
        dataProtototypeInPortInterfaceRef = None,
        dataPrototypeInPortInterfaceRef = None,
        dataPrototypeRef = None,
        networkRepresentationProps = None,
        transformationPropsRef = None
    ):
        self.dataProtototypeInPortInterfaceRef = dataProtototypeInPortInterfaceRef
        self.dataPrototypeInPortInterfaceRef = dataPrototypeInPortInterfaceRef
        self.dataPrototypeRef = dataPrototypeRef
        self.networkRepresentationProps = networkRepresentationProps
        self.transformationPropsRef = transformationPropsRef
