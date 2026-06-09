from autosar.base import parseTextNode,parseIntNode
from autosar.signal import *
from autosar.parser.parser_base import EntityParser, parseElementUUID
from autosar.util.errorHandler import handleNotImplementedError

class SignalParser(EntityParser):
    def __init__(self,version=3):
        self.version=version

        if self.version >= 3.0 and self.version < 4.0:
            self.switcher = {'SYSTEM-SIGNAL': self.parseSystemSignalV3,
                             'SYSTEM-SIGNAL-GROUP': self.parseSystemSignalGroup
            }
        elif self.version >= 4.0:
            self.switcher = {'SYSTEM-SIGNAL': self.parseSystemSignalV4,
                             'SYSTEM-SIGNAL-GROUP': self.parseSystemSignalGroup
            }

    def getSupportedTags(self):
        return self.switcher.keys()

    @parseElementUUID
    def parseElement(self, xmlElement, parent = None):
        parseFunc = self.switcher.get(xmlElement.tag)
        if parseFunc is not None:
            return parseFunc(xmlElement,parent)
        else:
            return None

    @parseElementUUID
    def parseSystemSignalV3(self,xmlRoot,parent=None):
        """
        parses <SYSTEM-SIGNAL> (Autosar 3 standard)
        """
        assert(xmlRoot.tag=='SYSTEM-SIGNAL')
        name,dataTypeRef,initValueRef,length,desc=None,None,None,None,None
        for elem in xmlRoot.findall('./*'):
            if elem.tag=='SHORT-NAME':
                name=parseTextNode(elem)
            elif elem.tag=='DATA-TYPE-REF':
                dataTypeRef=parseTextNode(elem)
            elif elem.tag=='INIT-VALUE-REF':
                initValueRef=parseTextNode(elem)
            elif elem.tag=='LENGTH':
                length=parseIntNode(elem)
            elif elem.tag=='DESC':
                descXml = xmlRoot.find('DESC')
                if descXml is not None:
                    L2Xml = descXml.find('L-2')
                    if L2Xml is not None:
                        desc = parseTextNode(L2Xml)
            else:
                handleNotImplementedError(elem.tag)
#      if (name is not None) and (dataTypeRef is not None) and (initValueRef is not None) and length is not None:
        if (name is not None) and length is not None:  #All signals doesn't have IV constant Ref or DatatypeRef
            return SystemSignalV3(name, dataTypeRef, initValueRef, length, desc, parent)
        else:
            raise RuntimeError('failed to parse %s'%xmlRoot.tag)

    @parseElementUUID
    def parseSystemSignalV4(self,xmlRoot,parent=None):
        """
        parses <SYSTEM-SIGNAL> (Autosar 4 standard)
        """
        assert(xmlRoot.tag=='SYSTEM-SIGNAL')
        name, dynamic_length = None, False
        for elem in xmlRoot.findall('./*'):
            if elem.tag=='SHORT-NAME':
                name=parseTextNode(elem)
            elif elem.tag=='DYNAMIC-LENGTH':
                dynamic_length = parseTextNode(elem) == "true"
            elif elem.tag=='PHYSICAL-PROPS':
                # TODO: add implementation to parse this tag
                pass
            else:
                handleNotImplementedError(elem.tag)
            return SystemSignalV4(name, dynamic_length, parent)
        else:
            raise RuntimeError('failed to parse %s'%xmlRoot.tag)

    @parseElementUUID
    def parseSystemSignalGroup(self, xmlRoot, parent=None):
        name,systemSignalRefs=None,None
        for elem in xmlRoot.findall('./*'):
            if elem.tag=='SHORT-NAME':
                name=parseTextNode(elem)
            elif elem.tag=='SYSTEM-SIGNAL-REFS':
                systemSignalRefs=[]
                for childElem in elem.findall('./*'):
                    if childElem.tag=='SYSTEM-SIGNAL-REF':
                        systemSignalRefs.append(parseTextNode(childElem))
                    else:
                        handleNotImplementedError(childElem.tag)
            else:
                handleNotImplementedError(elem.tag)

        if (name is not None) and (isinstance(systemSignalRefs,list)):
            return SystemSignalGroup(name,systemSignalRefs)
        else:
            raise RuntimeError('failed to parse %s'%xmlRoot.tag)

class ISignalParser(EntityParser):
    def __init__(self,version=3):
        super().__init__(version)
        self.version=version

        if self.version >= 3.0 and self.version < 4.0:
            raise NotImplementedError('ISignal is currently not supported by this library for Autosar 3 standard')
        elif self.version >= 4.0:
            self.switcher = {
                'I-SIGNAL': self.parseISignalV4,
                'I-SIGNAL-GROUP': self.parseISignalGroupV4
            }

    def getSupportedTags(self):
        return self.switcher.keys()

    @parseElementUUID
    def parseElement(self, xmlElement, parent = None):
        parseFunc = self.switcher.get(xmlElement.tag)
        if parseFunc is not None:
            return parseFunc(xmlElement,parent)
        else:
            return None
    
    @parseElementUUID
    def parseISignalV4(self, xmlRoot, parent=None):
        """
        parses <I-SIGNAL> (Autosar 4 standard)
        """
        assert(xmlRoot.tag=='I-SIGNAL')
        dataTransformations = None
        dataTypePolicy = None
        props = None
        iSignalType = None
        initValue = None
        initValueRef = None
        length = None
        networkRepresentationProps = None
        systemSignalRef = None
        timeoutSubstitutionValue = None
        transformationISignalPropss = None

        self.push()

        for elem in xmlRoot.findall('./*'):
            if elem.tag=='DATA-TRANSFORMATIONS':
                dataTransformations = []
                for childElem in elem.findall('./*'):
                    if childElem.tag=='DATA-TRANSFORMATION-REF-CONDITIONAL':
                        dataTransformations.append(self.parseDataTransformationRefConditional(childElem))
                    else:
                        handleNotImplementedError(childElem.tag)
            elif elem.tag=='DATA-TYPE-POLICY':
                dataTypePolicy = self.parseTextNode(elem)
            elif elem.tag=='I-SIGNAL-PROPS':
                props = self.parseISignalProps(elem)
            elif elem.tag=='I-SIGNAL-TYPE':
                iSignalType = self.parseTextNode(elem)
            elif elem.tag=='INIT-VALUE':
                initValue, initValueRef = self._parseAr4InitValue(elem)
            elif elem.tag=='LENGTH':
                length = self.parseIntNode(elem)
            elif elem.tag=='NETWORK-REPRESENTATION-PROPS':
                # TODO: add implementation to parse this tag
                pass
            elif elem.tag=='SYSTEM-SIGNAL-REF':
                # TODO: add implementation to parse this tag
                pass
            elif elem.tag=='TIMEOUT-SUBSTITUTION-VALUE':
                # TODO: add implementation to parse this tag
                pass
            elif elem.tag=='TRANSFORMATION-I-SIGNAL-PROPSS':
                transformationISignalPropss = []
                for childElem in elem.findall('./*'):
                    if childElem.tag=='END-TO-END-TRANSFORMATION-I-SIGNAL-PROPS':
                        # TODO: add implementation to parse this tag
                        pass
                    elif childElem.tag=='SOMEIP-TRANSFORMATION-I-SIGNAL-PROPS':
                        # TODO: add implementation to parse this tag
                        pass
                    elif childElem.tag=='USER-DEFINED-TRANSFORMATION-I-SIGNAL-PROPS':
                        # TODO: add implementation to parse this tag
                        pass
                    else:
                        handleNotImplementedError(childElem.tag)
            else:
                self.defaultHandler(elem)
            
        if self.name is None:
            raise RuntimeError(f'Error in TAG {xmlRoot.tag}: SHORT-NAME must not be None')
        
        adminData = ad if (ad := self.adminData) is not None else None

        iSignal = ISignalV4(
            name=self.name,
            adminData=adminData,
            dataTransformations=dataTransformations,
            dataTypePolicy=dataTypePolicy,
            props=props,
            iSignalType=iSignalType,
            initValue=initValue,
            initValueRef=initValueRef,
            length=length,
            networkRepresentationProps=networkRepresentationProps,
            systemSignalRef=systemSignalRef,
            timeoutSubstitutionValue=timeoutSubstitutionValue,
            transformationISignalPropss=transformationISignalPropss,
            parent=parent
        )

        self.pop(iSignal)

        return iSignal
    
    @parseElementUUID
    def parseISignalGroupV4(self, xmlRoot, parent=None):
        """
        parses <I-SIGNAL-GROUP> (Autosar 4 standard)
        """
        assert(xmlRoot.tag=='I-SIGNAL-GROUP')
        comBasedSignalGroupTransformations = None
        iSignalRefs = None
        systemSignalGroupRef = None
        transformationISignalPropss = None
        
        self.push()
        
        for elem in xmlRoot.findall('./*'):
            if elem.tag=='COM-BASED-SIGNAL-GROUP-TRANSFORMATIONS':
                comBasedSignalGroupTransformations = []
                for childElem in elem.findall('./*'):
                    if childElem.tag=='DATA-TRANSFORMATION-REF-CONDITIONAL':
                        comBasedSignalGroupTransformations.append(self.parseDataTransformationRefConditional(childElem))
                    else:
                        handleNotImplementedError(childElem.tag)
            elif elem.tag=='I-SIGNAL-REFS':
                iSignalRefs = []
                for childElem in elem.findall('./*'):
                    if childElem.tag=='I-SIGNAL-REF':
                        # TODO: add implementation to parse this tag
                        pass
                    else:
                        handleNotImplementedError(childElem.tag)
            elif elem.tag=='SYSTEM-SIGNAL-GROUP-REF':
                # TODO: add implementation to parse this tag
                pass
            elif elem.tag=='TRANSFORMATION-I-SIGNAL-PROPSS':
                transformationISignalPropss = []
                for childElem in elem.findall('./*'):
                    if childElem.tag=='END-TO-END-TRANSFORMATION-I-SIGNAL-PROPS':
                        # TODO: add implementation to parse this tag
                        pass
                    elif childElem.tag=='SOMEIP-TRANSFORMATION-I-SIGNAL-PROPS':
                        # TODO: add implementation to parse this tag
                        pass
                    elif childElem.tag=='USER-DEFINED-TRANSFORMATION-I-SIGNAL-PROPS':
                        # TODO: add implementation to parse this tag
                        pass
                    else:
                        handleNotImplementedError(childElem.tag)
            else:
                self.defaultHandler(elem)
        
        if self.name is None:
            raise RuntimeError(f'Error in TAG {xmlRoot.tag}: SHORT-NAME must not be None')
        
        adminData = ad if (ad := self.adminData) is not None else None

        iSignalGroup = ISignalGroup(
            name=self.name,
            adminData=adminData,
            comBasedSignalGroupTransformations=comBasedSignalGroupTransformations,
            iSignalRefs=iSignalRefs,
            systemSignalGroupRef=systemSignalGroupRef,
            transformationISignalPropss=transformationISignalPropss,
            parent=parent
        )

        self.pop(iSignalGroup)
        return iSignalGroup
    
    def parseDataTransformationRefConditional(self, xmlRoot):
        """
        parses <DATA-TRANSFORMATION-REF-CONDITIONAL> (Autosar 4 standard)
        """
        assert(xmlRoot.tag=='DATA-TRANSFORMATION-REF-CONDITIONAL')
        dataTransformationRef = None
        variationPoint = None

        for elem in xmlRoot.findall('./*'):
            if elem.tag=='DATA-TRANSFORMATION-REF':
                dataTransformationRef = self.parseTextNode(elem)
            elif elem.tag=='VARIATION-POINT':
                variationPoint = self.parseVariationPoint(elem)
            else:
                handleNotImplementedError(elem.tag)
        
        return DataTransformationRefConditional(dataTransformationRef, variationPoint)
    
    def parseISignalProps(self, xmlRoot):
        """
        parses <I-SIGNAL-PROPS> (Autosar 4 standard)
        """
        assert(xmlRoot.tag=='I-SIGNAL-PROPS')
        handleOutOfRange = None

        for elem in xmlRoot.findall('./*'):
            if elem.tag=='HANDLE-OUT-OF-RANGE':
                handleOutOfRange = self.parseTextNode(elem)
            else:
                handleNotImplementedError(elem.tag)
        
        return ISignalProps(handleOutOfRange)
