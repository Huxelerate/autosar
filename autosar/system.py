from autosar.element import Element

class System(Element):
    def __init__(self,name,parent=None):
        super().__init__(name,parent)
        self.fibexElementRefs=[]
        self.fibexElementRefConditionals=[]
        self.softwareComposition=None
        self.rootSoftwareCompositions=[]
    
    def find(self, ref):
        if ref is None: return None
        if ref[0]=='/': ref=ref[1:] #removes initial '/' if it exists
        ref=ref.partition('/')
        name=ref[0]
        foundElem = None
        for elem in self.rootSoftwareCompositions:
            if elem.name == name:
                foundElem = elem
                break
        if foundElem is not None:
            if len(ref[2])>0 and hasattr(foundElem, "find"):
                return foundElem.find(ref[2])
            else:
                return foundElem
        return None

    def asdict(self):
        # NOTE: outdated, does not include all elements (e.g.: missing fibexElementRefConditionals)
        data={'type': self.__class__.__name__,'name':self.name,
              }
        if len(self.fibexElementRefs)>0:
            data['fibexElementRefs']=self.fibexElementRefs[:]
        return data
    
class SystemV3(System):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.mapping = None
    
class SystemV4(System):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.mappings = []

    def find(self, ref):
        if ref is None: return None

        result = super().find(ref)
        if result is not None:
            return result
        
        if ref[0]=='/': ref=ref[1:] #removes initial '/' if it exists
        ref=ref.partition('/')
        name=ref[0]
        for elem in self.mappings:
            if elem.name == name:
                return elem

        return None

class DataMapping:
    def __init__(self):
        self.swcToImpl=[]
        self.senderReceiverToSignal=[]
        self.senderReceiverToSignalGroup=[]

class Mapping:
    def __init__(self,name=None,parent=None):
        self.name=None
        self.data=DataMapping()

class SystemMapping:
    def __init__(self,name=None,parent=None):
        self.name=name
        self.parent=parent
        self.data=DataMapping()

class SenderReceiverToSignalMappingV3:
    """
    <SENDER-RECEIVER-TO-SIGNAL-MAPPING>
    """
    def __init__(self,dataElemInstanceRef,signalRef):
        self.dataElemInstanceRef=dataElemInstanceRef
        self.signalRef=signalRef

class SignalDataElementInstanceRefV3:
    """
    <DATA-ELEMENT-IREF>
    Note: Observe that there are multiple <DATA-ELEMENT-IREF> definitions in the AUTOSAR XSD (used for different purposes)
    """
    def __init__(self,dataElemRef):
        self.dataElemRef = dataElemRef      #minOccurs=1, maxOccurs=1
        self.softwareCompositionRef=None    #minOccurs=0, maxOccurs=1
        self.componentPrototypeRef=[]       #minOccurs=0, maxOccurs=unbounded
        self.portPrototypeRef=None          #minOccurs=0, maxOccurs=1
    def asdict(self):
        data={'type': self.__class__.__name__,'dataElemRef':self.dataElemRef}
        return data

class SenderReceiverToSignalMappingV4:
    """
    <SENDER-RECEIVER-TO-SIGNAL-MAPPING>
    """
    def __init__(self,dataElemInstanceRef,systemSignalRef):
        self.dataElemInstanceRef=dataElemInstanceRef
        self.systemSignalRef=systemSignalRef

class SignalDataElementInstanceRefV4:
    """
    <DATA-ELEMENT-IREF>
    Note: Observe that there are multiple <DATA-ELEMENT-IREF> definitions in the AUTOSAR XSD (used for different purposes)
    """
    def __init__(self):
        self.targetDataPrototypeRef=None  #minOccurs=0, maxOccurs=1
        self.contextCompositionRef=None   #minOccurs=0, maxOccurs=1
        self.contextPortRef=None          #minOccurs=0, maxOccurs=1
        self.contextComponentRef=[]       #minOccurs=0, maxOccurs=unbound
    def asdict(self):
        data={'type': self.__class__.__name__}
        return data

class SenderReceiverToSignalGroupMapping:
    """
    <SENDER-RECEIVER-TO-SIGNAL-GROUP-MAPPING>
    """
    def __init__(self,dataElemInstanceRef,signalGroupRef,typeMapping):
        self.dataElemInstanceRef=dataElemInstanceRef
        self.signalGroupRef=signalGroupRef
        self.typeMapping=typeMapping

class TypeMapping:
    def __init__(self):
        self.elements=[]


class ArrayElementMapping(TypeMapping):
    def __init__(self):
        super().__init__()

class RecordElementMapping(TypeMapping):
    def __init__(self):
        super().__init__()

class SenderRecRecordElementMapping:
    def __init__(self,recordElementRef,signalRef):
        self.recordElementRef=recordElementRef
        self.signalRef=signalRef

class RootSwCompositionPrototype(Element):
    """
    Implements <ROOT-SW-COMPOSITION-PROTOTYPE> (AUTOSAR 4)
    """
    def tag(self, version=None): return "ROOT-SW-COMPOSITION-PROTOTYPE"

    def __init__(self, name, softwareCompositionTref, flatMapRef, adminData=None, category=None, parent=None):
        super().__init__(name, parent, adminData, category)
        self.softwareCompositionTref = softwareCompositionTref
        self.flatMapRef = flatMapRef
