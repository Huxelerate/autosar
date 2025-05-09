from autosar.base import hasAdminData,parseAdminDataNode,parseTextNode
import autosar.portinterface
import autosar.base
import autosar.element
import autosar.mode
from autosar.parser.parser_base import EntityParser, parseElementUUID
from autosar.util.errorHandler import handleNotImplementedError

class PortInterfacePackageParser(EntityParser):
    def __init__(self, version=3.0):
        super().__init__(version)

        if self.version >= 3.0 and self.version < 4.0:
            self.switcher = {'SENDER-RECEIVER-INTERFACE': self.parseSenderReceiverInterface,
                             'CALPRM-INTERFACE': self.parseCalPrmInterface,
                             'CLIENT-SERVER-INTERFACE': self.parseClientServerInterface
            }
        elif self.version >= 4.0:
            self.switcher = {
               'SENDER-RECEIVER-INTERFACE': self.parseSenderReceiverInterface,
               'PARAMETER-INTERFACE': self.parseParameterInterface,
               'CLIENT-SERVER-INTERFACE': self.parseClientServerInterface,
               'MODE-SWITCH-INTERFACE': self.parseModeSwitchInterface,
               'NV-DATA-INTERFACE': self.parseNvDataInterface,
               'TRIGGER-INTERFACE': self.parseTriggerInterface
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
    def parseSenderReceiverInterface(self, xmlRoot, parent=None):
        assert (xmlRoot.tag == 'SENDER-RECEIVER-INTERFACE')
        (isService, serviceKind, dataElements, modeGroups, invalidationPolicys) = (False, None, None, None, None)
        self.push()
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'IS-SERVICE':
                isService = self.parseBooleanNode(xmlElem)
            elif xmlElem.tag == 'SERVICE-KIND' and self.version >= 4.0:
                serviceKind = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'DATA-ELEMENTS':
                dataElements = self._parseDataElements(xmlElem)
            elif xmlElem.tag == 'MODE-GROUPS' and self.version < 4.0:
                modeGroups = self._parseModeGroups(xmlElem)
            elif xmlElem.tag == 'INVALIDATION-POLICYS' and self.version >= 4.0:
                invalidationPolicys = self._parseInvalidationPolicys(xmlElem)
            else:
                self.defaultHandler(xmlElem)
        if self.name is not None:
            portinterface = autosar.portinterface.SenderReceiverInterface(self.name, isService, serviceKind, parent = parent, adminData = self.adminData)
            if dataElements is not None:
                for dataElement in dataElements:
                    dataElement.parent = portinterface
                    portinterface.dataElements.append(dataElement)
            if modeGroups is not None:
                for modeGroup in modeGroups:
                    modeGroup.parent = portinterface
                    portinterface.modeGroups.append(modeGroups)
            if invalidationPolicys is not None:
                for policy in invalidationPolicys:
                    policy.parent = portinterface
                    portinterface.invalidationPolicies.append(policy)
            self.pop(portinterface)
            return portinterface
        else:
            self.pop()
            return None

    @parseElementUUID
    def _parseDataElements(self, xmlRoot):
        dataElements = []
        if self.version >= 4.0:
            parseMethod = self.parseAutosarDataPrototype
            dataElemTag = 'VARIABLE-DATA-PROTOTYPE'
        else:
            parseMethod = self._parseDataElementPrototype
            dataElemTag = 'DATA-ELEMENT-PROTOTYPE'
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == dataElemTag:
                dataElem = parseMethod(xmlElem)
                if dataElem is not None:
                    dataElements.append(dataElem)
            else:
                handleNotImplementedError(xmlElem.tag)
        return dataElements
    
    @parseElementUUID
    def _parseTriggers(self, xmlRoot):
        assert(xmlRoot.tag == 'TRIGGERS')
        triggers = []
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'TRIGGER':
                swImplPolicy = None
                self.push()
                for xmlChild in xmlElem.findall('./*'):
                    if xmlChild.tag == "SW-IMPL-POLICY":
                        swImplPolicy = self.parseTextNode(xmlChild)
                    else:
                        # TODO: implement "TRIGGER-PERIOD"
                        self.defaultHandler(xmlChild)
                
                if self.name is not None:
                    triggers.append(autosar.portinterface.Trigger(self.name, swImplPolicy))
                self.pop()
            else:
                handleNotImplementedError(xmlElem.tag)
        return triggers

    @parseElementUUID
    def _parseModeGroups(self, xmlRoot):
        assert(xmlRoot.tag == 'MODE-GROUPS')
        modeGroups = []

        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'MODE-DECLARATION-GROUP-PROTOTYPE':
                self.push()
                for xmlChild in xmlElem.findall('./*'):
                    typeRef = None
                    if xmlChild.tag == 'TYPE-TREF':
                        typeRef = self.parseTextNode(xmlChild)
                    else:
                        self.defaultHandler(xmlChild)
                if self.name is not None and typeRef is not None:
                    modeGroups.append(autosar.portinterface.ModeGroup(self.name, typeRef))
                self.pop()
            else:
                handleNotImplementedError(xmlElem.tag)
        return modeGroups

    def _parseInvalidationPolicys(self, xmlRoot):
        assert(xmlRoot.tag == 'INVALIDATION-POLICYS')
        policyList = []
        for xmlChild in xmlRoot.findall('./*'):
            if xmlChild.tag == 'INVALIDATION-POLICY':
                invalidationPolicy = self._parseInvalidationPolicy(xmlChild)
                if invalidationPolicy is not None:
                    policyList.append(invalidationPolicy)
            else:
                handleNotImplementedError(xmlChild.tag)
        return policyList

    @parseElementUUID
    def _parseDataElementPrototype(self, xmlRoot):
        assert(xmlRoot.tag == 'DATA-ELEMENT-PROTOTYPE')
        (typeRef, isQueued) = (None, False)
        self.push()
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'TYPE-TREF':
                typeRef = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'IS-QUEUED':
                isQueued = True if self.parseTextNode(xmlElem) == 'true' else False
            else:
                self.defaultHandler(xmlElem)
        if (self.name is not None) and (typeRef is not None):
            elem = autosar.element.AutosarDataPrototype(
                autosar.element.AutosarDataPrototype.Role.Variable,
                self.name,
                typeRef,
                isQueued
            )
            self.pop(elem)
            return elem
        else:
            if self.name is None:
                raise RuntimeError(f'Error in TAG {xmlRoot.tag}: SHORT-NAME and TYPE-TREF must not be None')
            else:
                raise RuntimeError(f'Error in TAG {xmlRoot.tag}: TYPE-TREF not defined for element with SHORT-NAME "{self.name}"')
            


    def _parseInvalidationPolicy(self, xmlRoot):
        (dataElementRef, handleInvalid) = (None, None)
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'DATA-ELEMENT-REF':
                dataElementRef = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'HANDLE-INVALID':
                handleInvalid = self.parseTextNode(xmlElem)
            else:
                handleNotImplementedError(xmlElem.tag)
        if (dataElementRef is not None) and (handleInvalid is not None):
            return autosar.portinterface.InvalidationPolicy(dataElementRef, handleInvalid)
        else:
            raise RuntimeError('DATA-ELEMENT-REF and HANDLE-INVALID must not be None')

    @parseElementUUID
    def parseCalPrmInterface(self,xmlRoot,parent=None):
        assert(xmlRoot.tag=='CALPRM-INTERFACE')
        xmlName = xmlRoot.find("./SHORT-NAME")
        if xmlName is not None:
            portInterface = autosar.portinterface.ParameterInterface(xmlName.text)
            if xmlRoot.find("./IS-SERVICE").text == 'true': portInterface.isService = True
            for xmlElem in xmlRoot.findall('./CALPRM-ELEMENTS/CALPRM-ELEMENT-PROTOTYPE'):
                xmlElemName = xmlElem.find("./SHORT-NAME")
                if xmlElemName is not None:
                    typeRef=xmlElem.find("./TYPE-TREF").text
                    parameter = autosar.element.AutosarDataPrototype(autosar.element.AutosarDataPrototype.Role.Parameter, xmlElemName.text, typeRef, parent=portInterface)
                    if hasAdminData(xmlElem):
                        parameter.adminData=parseAdminDataNode(xmlElem.find('ADMIN-DATA'))
                    if xmlElem.find('SW-DATA-DEF-PROPS'):
                        for xmlItem in xmlElem.findall('SW-DATA-DEF-PROPS/SW-ADDR-METHOD-REF'):
                            parameter.swAddressMethodRef = self.parseTextNode(xmlItem)
                    portInterface.append(parameter)
            return portInterface

    @parseElementUUID
    def parseClientServerInterface(self,xmlRoot,parent=None):
        assert(xmlRoot.tag=='CLIENT-SERVER-INTERFACE')
        name = self.parseTextNode(xmlRoot.find('SHORT-NAME'))
        if name is not None:
            portInterface = autosar.portinterface.ClientServerInterface(name)
            self.push()
            if hasAdminData(xmlRoot):
                portInterface.adminData=parseAdminDataNode(xmlRoot.find('ADMIN-DATA'))
            for xmlElem in xmlRoot.findall('./*'):
                if (xmlElem.tag == 'SHORT-NAME') or (xmlElem.tag == 'ADMIN-DATA'):
                    continue
                elif xmlElem.tag == 'IS-SERVICE':
                    if self.parseTextNode(xmlElem) == 'true':
                        portInterface.isService = True
                elif xmlElem.tag == 'OPERATIONS':
                    for xmlChildItem in xmlElem.findall('./*'):
                        if (self.version < 4.0 and xmlChildItem.tag == 'OPERATION-PROTOTYPE') or (self.version >= 4.0 and xmlChildItem.tag == 'CLIENT-SERVER-OPERATION'):
                            operation = self._parseOperationPrototype(xmlChildItem, portInterface)
                            portInterface.operations.append(operation)
                        else:
                            handleNotImplementedError(xmlChildItem.tag)
                elif xmlElem.tag == 'POSSIBLE-ERRORS':
                    for xmlError in xmlElem.findall('APPLICATION-ERROR'):
                        applicationError = self._parseApplicationError(xmlError, portInterface)
                        portInterface.applicationErrors.append(applicationError)
                elif xmlElem.tag == 'SERVICE-KIND':
                    portInterface.serviceKind = self.parseTextNode(xmlElem)
                else:
                    self.defaultHandler(xmlElem)
            self.pop(portInterface)
            return portInterface

    @parseElementUUID
    def parseParameterInterface(self,xmlRoot,parent=None):
        (isService, xmlParameters, serviceKind) = (False, None, None)

        self.push()
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'IS-SERVICE':
                isService = self.parseBooleanNode(xmlElem)
            elif xmlElem.tag == 'PARAMETERS':
                xmlParameters = xmlElem
            elif xmlElem.tag == 'SERVICE-KIND' and self.version >= 4.0:
                serviceKind = self.parseTextNode(xmlElem)
            else:
                self.defaultHandler(xmlElem)
                        
        portInterface = None
        if (self.name is not None) and (xmlParameters is not None):
            portInterface = autosar.portinterface.ParameterInterface(self.name, isService, serviceKind, parent, self.adminData)
            for xmlChild in xmlParameters.findall('./*'):
                if xmlChild.tag == 'PARAMETER-DATA-PROTOTYPE':
                    parameter = self._parseParameterDataPrototype(xmlChild, portInterface)
                    portInterface.append(parameter)
                else:
                    handleNotImplementedError(xmlChild.tag)
        
        self.pop(portInterface)
        return portInterface


    @parseElementUUID
    def parseModeSwitchInterface(self,xmlRoot,parent=None):
        (isService, xmlModeGroup, serviceKind) = (False, None, None)

        self.push()
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'IS-SERVICE':
                isService = self.parseBooleanNode(xmlElem)
            elif xmlElem.tag == 'MODE-GROUP':
                xmlModeGroup = xmlElem
            elif xmlElem.tag == 'SERVICE-KIND' and self.version >= 4.0:
                serviceKind = self.parseTextNode(xmlElem)
            else:
                self.defaultHandler(xmlElem)

        portInterface = None
        if (self.name is not None) and (xmlModeGroup is not None):
            portInterface = autosar.portinterface.ModeSwitchInterface(self.name, isService, serviceKind, parent, self.adminData)
            portInterface.modeGroup=self._parseModeGroup(xmlModeGroup, portInterface)
        
        self.pop(portInterface)
        return portInterface

    @parseElementUUID
    def _parseModeGroup(self, xmlModeGroup, parent):
        if self.version>=4.0:
            assert(xmlModeGroup.tag == "MODE-GROUP")
        else:
            assert(xmlModeGroup.tag == "MODE-DECLARATION-GROUP-PROTOTYPE")
        name = self.parseTextNode(xmlModeGroup.find('SHORT-NAME'))
        typeRef = self.parseTextNode(xmlModeGroup.find('TYPE-TREF'))
        return autosar.mode.ModeGroup(name, typeRef, parent)

    @parseElementUUID
    def _parseOperationPrototype(self, xmlOperation, parent):
        (xmlArguments, xmlPossibleErrorRefs) = (None, None)
        self.push()
        for xmlElem in xmlOperation.findall('./*'):
            if xmlElem.tag == 'ARGUMENTS':
                xmlArguments = xmlElem
            elif xmlElem.tag == 'POSSIBLE-ERROR-REFS':
                xmlPossibleErrorRefs = xmlElem
            else:
                self.defaultHandler(xmlElem)
        
        operation = None
        if self.name is not None:
            operation = autosar.portinterface.Operation(self.name, parent)
            operation.category = self.category
            argumentTag = 'ARGUMENT-DATA-PROTOTYPE' if self.version >= 4.0 else 'ARGUMENT-PROTOTYPE'
            if xmlArguments is not None:
                for xmlChild in xmlArguments.findall('./*'):
                    if xmlChild.tag == argumentTag:
                        if self.version >= 4.0:
                            argument = self._parseOperationArgumentV4(xmlChild, operation)
                        else:
                            argument = self._parseOperationArgumentV3(xmlChild, operation)
                        operation.arguments.append(argument)
                        argument.parent=operation
                    else:
                        handleNotImplementedError(xmlChild.tag)
            if xmlPossibleErrorRefs is not None:
                for xmlChild in xmlPossibleErrorRefs.findall('./*'):
                    if xmlChild.tag == 'POSSIBLE-ERROR-REF':
                        operation.errorRefs.append(self.parseTextNode(xmlChild))
                    else:
                        handleNotImplementedError(xmlChild.tag)

        self.pop(operation)
        return operation

    @parseElementUUID
    def _parseOperationArgumentV3(self, xmlArgument, parent):
        (name, typeRef, direction) = (None, None, None)
        for xmlElem in xmlArgument.findall('./*'):
            if xmlElem.tag == 'SHORT-NAME':
                name = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'TYPE-TREF':
                typeRef = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'DIRECTION':
                direction = self.parseTextNode(xmlElem)
            else:
                handleNotImplementedError(xmlElem.tag)
        if (name is not None) and (typeRef is not None) and (direction is not None):
            return autosar.portinterface.Argument(name, typeRef, direction)
        else:
            raise RuntimeError('SHORT-NAME, TYPE-TREF and DIRECTION must have valid values')

    @parseElementUUID
    def _parseOperationArgumentV4(self, xmlArgument, parent):
        (argument, typeRef, direction, props_variants, serverArgumentImplPolicy) = (None, None, None, None, None)
        self.push()
        for xmlElem in xmlArgument.findall('./*'):
            if xmlElem.tag == 'TYPE-TREF':
                typeRef = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'DIRECTION':
                direction = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'SW-DATA-DEF-PROPS':
                props_variants = self.parseSwDataDefProps(xmlElem)
            elif xmlElem.tag == 'SERVER-ARGUMENT-IMPL-POLICY':
                serverArgumentImplPolicy=self.parseTextNode(xmlElem)
            else:
                self.baseHandler(xmlElem)
        if (self.name is not None) and (typeRef is not None) and (direction is not None):
            argument = autosar.portinterface.Argument(self.name, typeRef, direction, serverArgumentImplPolicy = serverArgumentImplPolicy)
            if props_variants is not None:
                argument.swCalibrationAccess = props_variants[0].swCalibrationAccess
        else:
            raise RuntimeError('SHORT-NAME, TYPE-TREF and DIRECTION must have valid values')
        self.pop(argument)
        return argument

    @parseElementUUID
    def _parseApplicationError(self, xmlElem, parent):
        name=self.parseTextNode(xmlElem.find("./SHORT-NAME"))
        errorCode=self.parseTextNode(xmlElem.find("./ERROR-CODE"))
        return autosar.portinterface.ApplicationError(name, errorCode, parent)

    @parseElementUUID
    def _parseParameterDataPrototype(self, xmlElem, parent):
        return self.parseAutosarDataPrototype(xmlElem, parent)

    @parseElementUUID
    def parseNvDataInterface(self, xmlRoot, parent=None):
        assert (xmlRoot.tag == 'NV-DATA-INTERFACE')
        (isService, serviceKind, nvDatas) = (False, None, None)
        self.push()
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'IS-SERVICE':
                isService = self.parseBooleanNode(xmlElem)
            elif xmlElem.tag == 'SERVICE-KIND' and self.version >= 4.0:
                serviceKind = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'NV-DATAS':
                nvDatas = self._parseDataElements(xmlElem)
            else:
                self.defaultHandler(xmlElem)
        if self.name is not None:
            nvDataInterface = autosar.portinterface.NvDataInterface(self.name, isService, serviceKind, parent = parent, adminData = self.adminData)
            if nvDatas is not None:
                for nvData in nvDatas:
                    nvData.parent = nvDataInterface
                    nvDataInterface.nvDatas.append(nvData)
            self.pop(nvDataInterface)
            return nvDataInterface
        else:
            self.pop()
            return None
        
    @parseElementUUID
    def parseTriggerInterface(self, xmlRoot, parent=None):
        assert (xmlRoot.tag == 'TRIGGER-INTERFACE')
        (isService, serviceKind, triggers) = (False, None, None)
        self.push()
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'IS-SERVICE':
                isService = self.parseBooleanNode(xmlElem)
            elif xmlElem.tag == 'SERVICE-KIND':
                serviceKind = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'TRIGGERS':
                triggers = self._parseTriggers(xmlElem)
            else:
                self.defaultHandler(xmlElem)
        if self.name is not None:
            triggerInterface = autosar.portinterface.TriggerInterface(self.name, isService, serviceKind, parent = parent, adminData = self.adminData)
            if triggers is not None:
                for trigger in triggers:
                    trigger.parent = triggerInterface
                    triggerInterface.triggers.append(trigger)
            self.pop(triggerInterface)
            return triggerInterface
        else:
            self.pop()
            return None


class SoftwareAddressMethodParser(EntityParser):
    def __init__(self,version=3.0):
        self.version=version

    def getSupportedTags(self):
        return ['SW-ADDR-METHOD']

    @parseElementUUID
    def parseElement(self, xmlElement, parent = None):
        if xmlElement.tag == 'SW-ADDR-METHOD':
            return self.parseSWAddrMethod(xmlElement, parent)
        else:
            return None

    @parseElementUUID
    def parseSWAddrMethod(self,xmlRoot,rootProject=None,parent=None):
        assert(xmlRoot.tag == 'SW-ADDR-METHOD')
        name = xmlRoot.find("./SHORT-NAME").text
        return autosar.element.SoftwareAddressMethod(name)
