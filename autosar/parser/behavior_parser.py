import autosar.behavior, autosar.element
from autosar.parser.parser_base import EntityParser, parseElementUUID
from autosar.util.errorHandler import handleNotImplementedError, handleValueError

class BehaviorParser(EntityParser):
    def __init__(self,version=3.0):
        super().__init__(version)

    def getSupportedTags(self):
        if (self.version >=3.0) and (self.version < 4.0):
            return ['INTERNAL-BEHAVIOR']
        elif self.version >= 4.0:
            return ['SWC-INTERNAL-BEHAVIOR']
        else:
            return []

    @parseElementUUID
    def parseElement(self, xmlElement, parent = None):
        if (self.version >=3.0) and (self.version < 4.0) and xmlElement.tag == 'INTERNAL-BEHAVIOR':
            return self.parseInternalBehavior(xmlElement, parent)
        elif (self.version >= 4.0) and (xmlElement.tag == 'SWC-INTERNAL-BEHAVIOR'):
            return self.parseSWCInternalBehavior(xmlElement, parent)
        else:
            return None

    @parseElementUUID
    def parseInternalBehavior(self,xmlRoot,parent):
        """AUTOSAR 3 Internal Behavior"""
        assert(xmlRoot.tag == 'INTERNAL-BEHAVIOR')
        name = self.parseTextNode(xmlRoot.find('SHORT-NAME'))
        componentRef = self.parseTextNode(xmlRoot.find('COMPONENT-REF'))
        multipleInstance = False
        xmlSupportMultipleInst = xmlRoot.find('SUPPORTS-MULTIPLE-INSTANTIATION')
        if (xmlSupportMultipleInst is not None) and (xmlSupportMultipleInst.text == 'true'):
            multipleInstance = True
        ws = parent.rootWS()
        assert(ws is not None)
        if (name is not None) and (componentRef is not None):
            internalBehavior = autosar.behavior.InternalBehavior(name, componentRef, multipleInstance, parent)
            swc = ws.find(componentRef)
            if swc is not None:
                swc.behavior=internalBehavior
            for xmlNode in xmlRoot.findall('./*'):
                if (xmlNode.tag == 'SHORT-NAME') or (xmlNode.tag == 'COMPONENT-REF') or (xmlNode.tag == 'SUPPORTS-MULTIPLE-INSTANTIATION'):
                    continue
                if xmlNode.tag == 'EVENTS':
                    for xmlEvent in xmlNode.findall('./*'):
                        event = None
                        if xmlEvent.tag == 'MODE-SWITCH-EVENT':
                            event = self.parseModeSwitchEvent(xmlEvent,internalBehavior)
                        elif xmlEvent.tag == 'TIMING-EVENT':
                            event = self.parseTimingEvent(xmlEvent,internalBehavior)
                        elif xmlEvent.tag == 'DATA-RECEIVED-EVENT':
                            event = self.parseDataReceivedEvent(xmlEvent,internalBehavior)
                        elif xmlEvent.tag == 'OPERATION-INVOKED-EVENT':
                            event = self.parseOperationInvokedEvent(xmlEvent,internalBehavior)
                        else:
                            handleNotImplementedError(xmlEvent.tag)
                        if event is not None:
                            internalBehavior.events.append(event)
                        else:
                            handleValueError('event')
                elif xmlNode.tag == 'PORT-API-OPTIONS':
                    for xmlOption in xmlNode.findall('./PORT-API-OPTION'):
                        portAPIOption = autosar.behavior.PortAPIOption(self.parseTextNode(xmlOption.find('PORT-REF')),self.parseBooleanNode(xmlOption.find('ENABLE-TAKE-ADDRESS')),self.parseBooleanNode(xmlOption.find('INDIRECT-API')))
                        # TODO: Backport PortArgValues support from Autosar 4
                        if portAPIOption is not None: internalBehavior.portAPIOptions.append(portAPIOption)
                elif xmlNode.tag == 'RUNNABLES':
                    for xmRunnable in xmlNode.findall('./RUNNABLE-ENTITY'):
                        runnableEntity = self.parseRunnableEntity(xmRunnable, internalBehavior)
                        if runnableEntity is not None:
                            internalBehavior.runnables.append(runnableEntity)
                elif xmlNode.tag == 'PER-INSTANCE-MEMORYS':
                    for xmlElem in xmlNode.findall('./PER-INSTANCE-MEMORY'):
                        perInstanceMemory = autosar.behavior.PerInstanceMemory(self.parseTextNode(xmlElem.find('SHORT-NAME')),self.parseTextNode(xmlElem.find('TYPE-DEFINITION')), internalBehavior)
                        if perInstanceMemory is not None: internalBehavior.perInstanceMemories.append(perInstanceMemory)
                elif xmlNode.tag == 'SERVICE-NEEDSS':
                    for xmlElem in xmlNode.findall('./*'):
                        if xmlElem.tag=='SWC-NV-BLOCK-NEEDS':
                            swcNvBlockNeeds=self.parseSwcNvBlockNeeds(xmlElem)
                            if swcNvBlockNeeds is not None: internalBehavior.swcNvBlockNeeds.append(swcNvBlockNeeds)
                        else:
                            handleNotImplementedError(xmlElem.tag)
                elif xmlNode.tag == 'SHARED-CALPRMS':
                    for xmlElem in xmlNode.findall('./*'):
                        if xmlElem.tag=='CALPRM-ELEMENT-PROTOTYPE':
                            calPrmElemPrototype=self.parseCalPrmElemPrototype(xmlElem, internalBehavior)
                            assert(calPrmElemPrototype is not None)
                            internalBehavior.sharedCalParams.append(calPrmElemPrototype)
                        else:
                            handleNotImplementedError(xmlElem.tag)
                elif xmlNode.tag == 'EXCLUSIVE-AREAS':
                    for xmlElem in xmlNode.findall('./*'):
                        if xmlElem.tag=='EXCLUSIVE-AREA':
                            exclusiveArea=autosar.behavior.ExclusiveArea(self.parseTextNode(xmlElem.find('SHORT-NAME')), internalBehavior)
                            internalBehavior.exclusiveAreas.append(exclusiveArea)
                        else:
                            handleNotImplementedError(xmlElem.tag)
                else:
                    handleNotImplementedError(xmlNode.tag)
            return internalBehavior

    @parseElementUUID
    def parseSWCInternalBehavior(self, xmlRoot, parent):
        """AUTOSAR 4 internal behavior"""
        assert(xmlRoot.tag == 'SWC-INTERNAL-BEHAVIOR')
        name = self.parseTextNode(xmlRoot.find('SHORT-NAME'))
        multipleInstance = False
        xmlSupportMultipleInst = xmlRoot.find('SUPPORTS-MULTIPLE-INSTANTIATION')
        if xmlSupportMultipleInst is not None:
            multipleInstance = self.parseBooleanNode(xmlSupportMultipleInst)
            assert(multipleInstance is not None)
        ws = parent.rootWS()
        assert(ws is not None)
        if (name is not None):
            handledXML = ['SHORT-NAME', 'SUPPORTS-MULTIPLE-INSTANTIATION']
            internalBehavior = autosar.behavior.SwcInternalBehavior(name, parent.ref, multipleInstance, parent)
            for xmlElem in xmlRoot.findall('./*'):
                if xmlElem.tag in handledXML:
                    pass
                elif xmlElem.tag == 'DATA-TYPE-MAPPING-REFS':
                    for xmlChild in xmlElem.findall('./*'):
                        if xmlChild.tag == 'DATA-TYPE-MAPPING-REF':
                            tmp = self.parseTextNode(xmlChild)
                            if tmp is not None:
                                internalBehavior.appendDataTypeMappingRef(tmp)
                elif xmlElem.tag == 'CONSTANT-VALUE-MAPPING-REFS':
                    for xmlChild in xmlElem.findall('./*'):
                        if xmlChild.tag == 'CONSTANT-VALUE-MAPPING-REF':
                            tmp = self.parseTextNode(xmlChild)
                            if tmp is not None:
                                internalBehavior.appendConstantValueMappingRef(tmp)
                elif xmlElem.tag == 'EVENTS':
                    for xmlEvent in xmlElem.findall('./*'):
                        event = None
                        if xmlEvent.tag == 'INIT-EVENT':
                            event = self.parseInitEvent(xmlEvent, internalBehavior)
                        elif xmlEvent.tag == 'SWC-MODE-SWITCH-EVENT':
                            event = self.parseModeSwitchEvent(xmlEvent, internalBehavior)
                        elif xmlEvent.tag == 'TIMING-EVENT':
                            event = self.parseTimingEvent(xmlEvent, internalBehavior)
                        elif xmlEvent.tag == 'DATA-RECEIVED-EVENT':
                            event = self.parseDataReceivedEvent(xmlEvent, internalBehavior)
                        elif xmlEvent.tag == 'OPERATION-INVOKED-EVENT':
                            event = self.parseOperationInvokedEvent(xmlEvent, internalBehavior)
                        elif xmlEvent.tag == 'MODE-SWITCHED-ACK-EVENT':
                            event = self.parseModeSwitchedAckEvent(xmlEvent, internalBehavior)
                        elif xmlEvent.tag == 'DATA-RECEIVE-ERROR-EVENT':
                            #TODO: Implement later
                            pass
                        else:
                            handleNotImplementedError(xmlEvent.tag)
                        if event is not None:
                            internalBehavior.events.append(event)
                elif xmlElem.tag == 'PORT-API-OPTIONS':
                    for xmlOption in xmlElem.findall('./PORT-API-OPTION'):
                        enableTakeAddress = self.parseBooleanNode(xmlOption.find('ENABLE-TAKE-ADDRESS'))
                        indirectApi = self.parseBooleanNode(xmlOption.find('INDIRECT-API'))
                        portRef = self.parseTextNode(xmlOption.find('PORT-REF'))
                        
                        portArgValues = []
                        for xmlPortDefinedArgumentValue in xmlOption.findall('./PORT-ARG-VALUES/PORT-DEFINED-ARGUMENT-VALUE'):
                            portArgValues.append(self.constantParser.parsePortDefinedArgumentValue(xmlPortDefinedArgumentValue))

                        portAPIOption = autosar.behavior.PortAPIOption(portRef, enableTakeAddress, indirectApi, portArgValues)
                        
                        if portAPIOption is not None: internalBehavior.portAPIOptions.append(portAPIOption)
                elif xmlElem.tag == 'RUNNABLES':
                    for xmRunnable in xmlElem.findall('./RUNNABLE-ENTITY'):
                        runnableEntity = self.parseRunnableEntity(xmRunnable, internalBehavior)
                        if runnableEntity is not None:
                            internalBehavior.runnables.append(runnableEntity)
                elif xmlElem.tag == 'AR-TYPED-PER-INSTANCE-MEMORYS':
                    for xmlChild in xmlElem.findall('./*'):
                        if xmlChild.tag == 'VARIABLE-DATA-PROTOTYPE':
                            dataElement = self.parseAutosarDataPrototype(xmlChild, internalBehavior)
                            internalBehavior.perInstanceMemories.append(dataElement)
                        else:
                            handleNotImplementedError(xmlChild.tag)
                elif xmlElem.tag == 'SERVICE-DEPENDENCYS':
                    for xmlChildElem in xmlElem.findall('./*'):
                        if xmlChildElem.tag == 'SWC-SERVICE-DEPENDENCY':
                            swcServiceDependency = self.parseSwcServiceDependency(xmlChildElem, internalBehavior)
                            internalBehavior.serviceDependencies.append(swcServiceDependency)
                        else:
                            handleNotImplementedError(xmlChildElem.tag)
                elif xmlElem.tag == 'SHARED-PARAMETERS':
                    for xmlChildElem in xmlElem.findall('./*'):
                        if xmlChildElem.tag == 'PARAMETER-DATA-PROTOTYPE':
                            tmp = self.parseParameterDataPrototype(xmlChildElem, internalBehavior)
                            if tmp is not None:
                                internalBehavior.sharedParameterDataPrototype.append(tmp)
                        else:
                            handleNotImplementedError(xmlChildElem.tag)
                elif xmlElem.tag == 'EXCLUSIVE-AREAS':
                    for xmlChild in xmlElem.findall('./*'):
                        if xmlChild.tag=='EXCLUSIVE-AREA':
                            exclusiveArea=autosar.behavior.ExclusiveArea(self.parseTextNode(xmlChild.find('SHORT-NAME')), internalBehavior)
                            internalBehavior.exclusiveAreas.append(exclusiveArea)
                        else:
                            handleNotImplementedError(xmlChild.tag)
                elif xmlElem.tag == 'PER-INSTANCE-PARAMETERS':
                    for xmlChildElem in xmlElem.findall('./*'):
                        if xmlChildElem.tag == 'PARAMETER-DATA-PROTOTYPE':
                            tmp = self.parseParameterDataPrototype(
                                xmlChildElem, internalBehavior)
                            if tmp is not None:
                                internalBehavior.perInstanceParameterDataPrototype.append(
                                    tmp)
                        else:
                            handleNotImplementedError(xmlChildElem.tag)
                elif xmlElem.tag == 'EXPLICIT-INTER-RUNNABLE-VARIABLES':
                    for xmlChild in xmlElem.findall('./*'):
                        if xmlChild.tag == 'VARIABLE-DATA-PROTOTYPE':
                            dataElement = self.parseAutosarDataPrototype(xmlChild, internalBehavior)
                            internalBehavior.explicitVariables.append(dataElement)
                        else:
                            handleNotImplementedError(xmlChild.tag)
                elif xmlElem.tag == 'IMPLICIT-INTER-RUNNABLE-VARIABLES':
                    for xmlChild in xmlElem.findall('./*'):
                        if xmlChild.tag == 'VARIABLE-DATA-PROTOTYPE':
                            dataElement = self.parseAutosarDataPrototype(xmlChild, internalBehavior)
                            internalBehavior.implicitVariables.append(dataElement)
                        else:
                            handleNotImplementedError(xmlChild.tag)
                elif xmlElem.tag == 'HANDLE-TERMINATION-AND-RESTART':
                    pass #implement later
                elif xmlElem.tag == 'STATIC-MEMORYS':
                    pass #implement later
                elif xmlElem.tag == 'INCLUDED-DATA-TYPE-SETS':
                    for xmlChild in xmlElem.findall('./*'):
                        if xmlChild.tag == 'INCLUDED-DATA-TYPE-SET':
                            includedDataTypeSet = self.parseIncludedDataTypeSet(xmlChild)
                            internalBehavior.includedDataTypeSets.append(includedDataTypeSet)
                elif xmlElem.tag == 'CONSTANT-MEMORYS':
                    for xmlChild in xmlElem.findall('./*'):
                        if xmlChild.tag == 'PARAMETER-DATA-PROTOTYPE':
                            tmp = self.parseParameterDataPrototype(xmlChild, internalBehavior)
                            if tmp is not None:
                                internalBehavior.constantMemories.append(tmp)
                        else:
                            handleNotImplementedError(xmlChild.tag)
                elif xmlElem.tag == 'VARIATION-POINT-PROXYS':
                    for xmlChild in xmlElem.findall('./*'):
                        if xmlChild.tag == 'VARIATION-POINT-PROXY':
                            variationPointProxy = self.parseVariationPointProxy(xmlChild, internalBehavior)
                            internalBehavior.variationPointProxies.append(variationPointProxy)
                        else:
                            handleNotImplementedError(xmlChild.tag)
                else:
                    handleNotImplementedError(xmlElem.tag)
            return internalBehavior

    @parseElementUUID
    def parseRunnableEntity(self, xmlRoot, parent):
        name = None
        symbol = None
        xmlDataReceivePoints = None
        xmlDataSendPoints = None
        xmlServerCallPoints = None
        xmlCanEnterExclusiveAreas = None
        adminData = None
        xmlModeAccessPoints = None
        xmlParameterAccessPoints = None
        canBeInvokedConcurrently = False
        xmlModeSwitchPoints = None
        minStartInterval = None

        xmlDataReadAccess = None
        xmlDataWriteAccess = None
        xmlLocalDataReadAccess = None
        xmlLocalDataWriteAccess = None

        self.push()

        if self.version < 4.0:
            for xmlElem in xmlRoot.findall('*'):
                if xmlElem.tag=='SHORT-NAME':
                    name=self.parseTextNode(xmlElem)
                elif xmlElem.tag=='CAN-BE-INVOKED-CONCURRENTLY':
                    canBeInvokedConcurrently=self.parseBooleanNode(xmlElem)
                elif xmlElem.tag=='DATA-RECEIVE-POINTS':
                    xmlDataReceivePoints=xmlElem
                elif xmlElem.tag=='DATA-SEND-POINTS':
                    xmlDataSendPoints=xmlElem
                elif xmlElem.tag=='SERVER-CALL-POINTS':
                    xmlServerCallPoints=xmlElem
                elif xmlElem.tag=='SYMBOL':
                    symbol=self.parseTextNode(xmlElem)
                elif xmlElem.tag=='CAN-ENTER-EXCLUSIVE-AREA-REFS':
                    xmlCanEnterExclusiveAreas=xmlElem
                elif xmlElem.tag=='ADMIN-DATA':
                    adminData=self.parseAdminDataNode(xmlElem)
                else:
                    handleNotImplementedError(xmlElem.tag)
        else:
            for xmlElem in xmlRoot.findall('*'):
                if xmlElem.tag=='SHORT-NAME':
                    name=self.parseTextNode(xmlElem)
                elif xmlElem.tag=='CAN-BE-INVOKED-CONCURRENTLY':
                    canBeInvokedConcurrently=self.parseBooleanNode(xmlElem)
                elif xmlElem.tag == 'MODE-ACCESS-POINTS':
                    xmlModeAccessPoints = xmlElem
                elif xmlElem.tag=='DATA-RECEIVE-POINT-BY-ARGUMENTS':
                    xmlDataReceivePoints=xmlElem
                elif xmlElem.tag=='DATA-SEND-POINTS':
                    xmlDataSendPoints=xmlElem
                elif xmlElem.tag=='SERVER-CALL-POINTS':
                    xmlServerCallPoints=xmlElem
                elif xmlElem.tag=='SYMBOL':
                    symbol=self.parseTextNode(xmlElem)
                elif xmlElem.tag=='CAN-ENTER-EXCLUSIVE-AREA-REFS':
                    xmlCanEnterExclusiveAreas=xmlElem
                elif xmlElem.tag == 'MINIMUM-START-INTERVAL':
                    minStartInterval = self.parseNumberNode(xmlElem)
                elif xmlElem.tag =='ADMIN-DATA':
                    adminData=self.parseAdminDataNode(xmlElem)
                elif xmlElem.tag == 'PARAMETER-ACCESSS':
                    xmlParameterAccessPoints = xmlElem
                elif xmlElem.tag == 'MODE-SWITCH-POINTS':
                    xmlModeSwitchPoints = xmlElem
                elif xmlElem.tag == 'READ-LOCAL-VARIABLES':
                    xmlLocalDataReadAccess = xmlElem
                elif xmlElem.tag == 'WRITTEN-LOCAL-VARIABLES':
                    xmlLocalDataWriteAccess = xmlElem
                elif xmlElem.tag == 'DATA-READ-ACCESSS':
                    xmlDataReadAccess = xmlElem
                elif xmlElem.tag == 'DATA-WRITE-ACCESSS':
                    xmlDataWriteAccess = xmlElem
                elif xmlElem.tag == 'RUNS-INSIDE-EXCLUSIVE-AREA-REFS':
                    pass #implement later
                else:
                    self.defaultHandler(xmlElem)
        if name is None:
            handleValueError('SHORT-NAME is required for RunnableEntity')
            return None
        runnableEntity = autosar.behavior.RunnableEntity(name, canBeInvokedConcurrently, symbol, parent)
        if minStartInterval is not None:
            runnableEntity.minStartInterval = float(1000 * minStartInterval)
        if xmlDataReceivePoints is not None:
            if self.version < 4.0:
                for xmlDataPoint in xmlDataReceivePoints.findall('./DATA-RECEIVE-POINT'):
                    name=self.parseTextNode(xmlDataPoint.find('SHORT-NAME'))
                    dataElementInstanceRef = self.parseDataElementInstanceRef(xmlDataPoint.find('DATA-ELEMENT-IREF'),'R-PORT-PROTOTYPE-REF')
                    if dataElementInstanceRef is not None:
                        dataReceivePoint=autosar.behavior.DataReceivePoint(dataElementInstanceRef.portRef,dataElementInstanceRef.dataElemRef,name)
                        runnableEntity.append(dataReceivePoint)
            else:
                for xmlVariableAcess in xmlDataReceivePoints.findall('VARIABLE-ACCESS'):
                    name=self.parseTextNode(xmlVariableAcess.find('SHORT-NAME'))
                    accessedVariable = self.parseAccessedVariable(xmlVariableAcess.find('./ACCESSED-VARIABLE'))
                    assert(accessedVariable is not None)
                    dataReceivePoint=autosar.behavior.DataReceivePoint(accessedVariable.portPrototypeRef,accessedVariable.targetDataPrototypeRef,name)
                    runnableEntity.append(dataReceivePoint)
        if xmlDataSendPoints is not None:
            if self.version < 4.0:
                for xmlDataPoint in xmlDataSendPoints.findall('./DATA-SEND-POINT'):
                    name=self.parseTextNode(xmlDataPoint.find('SHORT-NAME'))
                    dataElementInstanceRef = self.parseDataElementInstanceRef(xmlDataPoint.find('DATA-ELEMENT-IREF'),'P-PORT-PROTOTYPE-REF')
                    if dataElementInstanceRef is not None:
                        dataSendPoint=autosar.behavior.DataSendPoint(dataElementInstanceRef.portRef,dataElementInstanceRef.dataElemRef,name)
                        runnableEntity.append(dataSendPoint)
            else:
                for xmlVariableAcess in xmlDataSendPoints.findall('VARIABLE-ACCESS'):
                    name=self.parseTextNode(xmlVariableAcess.find('SHORT-NAME'))
                    accessedVariable = self.parseAccessedVariable(xmlVariableAcess.find('./ACCESSED-VARIABLE'))
                    assert(accessedVariable is not None)
                    dataSendPoint=autosar.behavior.DataSendPoint(accessedVariable.portPrototypeRef,accessedVariable.targetDataPrototypeRef,name)
                    runnableEntity.append(dataSendPoint)
        if xmlModeAccessPoints is not None:
            for xmlElem in xmlModeAccessPoints.findall('./*'):
                if xmlElem.tag == 'MODE-ACCESS-POINT':
                    modeAccessPoint = self.parseModeAccessPoint(xmlElem)
                    assert(modeAccessPoint is not None)
                    runnableEntity.modeAccessPoints.append(modeAccessPoint)
                else:
                    handleNotImplementedError(xmlElem.tag)
        if xmlServerCallPoints is not None:
            for xmlServerCallPoint in xmlServerCallPoints.findall('./SYNCHRONOUS-SERVER-CALL-POINT'):
                syncServerCallPoint = self.parseSyncServerCallPoint(xmlServerCallPoint)
                if syncServerCallPoint is not None: runnableEntity.serverCallPoints.append(syncServerCallPoint)
            for xmlServerCallPoint in xmlServerCallPoints.findall('./ASYNCHRONOUS-SERVER-CALL-POINT'):
                asyncServerCallPoint = self.parseAsyncServerCallPoint(xmlServerCallPoint)
                if asyncServerCallPoint is not None: runnableEntity.serverCallPoints.append(asyncServerCallPoint)
        if xmlCanEnterExclusiveAreas is not None:
            for xmlCanEnterExclusiveAreaRef in xmlCanEnterExclusiveAreas.findall('./CAN-ENTER-EXCLUSIVE-AREA-REF'):
                runnableEntity.exclusiveAreaRefs.append(self.parseTextNode(xmlCanEnterExclusiveAreaRef))
        if self.version >= 4.0 and xmlParameterAccessPoints is not None:
            for xmlChild in xmlParameterAccessPoints.findall('./*'):
                if xmlChild.tag == 'PARAMETER-ACCESS':
                    tmp = self.parseParameterAccessPoint(xmlChild, runnableEntity)
                    if tmp is not None:
                        runnableEntity.parameterAccessPoints.append(tmp)
                else:
                    handleNotImplementedError(xmlChild.tag)
        if xmlModeSwitchPoints is not None:
            for xmlElem in xmlModeSwitchPoints.findall('./*'):
                if xmlElem.tag == 'MODE-SWITCH-POINT':
                    modeSwitchPoint = self._parseModeSwitchPoint(xmlElem)
                    assert(modeSwitchPoint is not None)
                    runnableEntity.modeSwitchPoints.append(modeSwitchPoint)
                else:
                    handleNotImplementedError(xmlElem.tag)

        if xmlDataReadAccess is not None:
            for xmlElem in xmlDataReadAccess.findall('./*'):
                if xmlElem.tag == 'VARIABLE-ACCESS':
                    variableAccess = self._parseVariableAccess(xmlElem)
                    assert(variableAccess is not None)
                    runnableEntity.dataReadAccess.append(variableAccess)
                else:
                    handleNotImplementedError(xmlElem.tag)
        
        if xmlDataWriteAccess is not None:
            for xmlElem in xmlDataWriteAccess.findall('./*'):
                if xmlElem.tag == 'VARIABLE-ACCESS':
                    variableAccess = self._parseVariableAccess(xmlElem)
                    assert(variableAccess is not None)
                    runnableEntity.dataWriteAccess.append(variableAccess)
                else:
                    handleNotImplementedError(xmlElem.tag)

        if xmlLocalDataReadAccess is not None:
            for xmlElem in xmlLocalDataReadAccess.findall('./*'):
                if xmlElem.tag == 'VARIABLE-ACCESS':
                    variableAccess = self._parseLocalVariableAccess(xmlElem)
                    assert(variableAccess is not None)
                    runnableEntity.dataLocalReadAccess.append(variableAccess)
                else:
                    handleNotImplementedError(xmlElem.tag)
        
        if xmlLocalDataWriteAccess is not None:
            for xmlElem in xmlLocalDataWriteAccess.findall('./*'):
                if xmlElem.tag == 'VARIABLE-ACCESS':
                    variableAccess = self._parseLocalVariableAccess(xmlElem)
                    assert(variableAccess is not None)
                    runnableEntity.dataLocalWriteAccess.append(variableAccess)
                else:
                    handleNotImplementedError(xmlElem.tag)
        
        if runnableEntity is not None:
            runnableEntity.adminData = adminData
        self.pop()
        return runnableEntity

    def parseModeAccessPoint(self, xmlRoot):
        assert(xmlRoot.tag == 'MODE-ACCESS-POINT')
        (name, modeGroupInstanceRef) = (None, None)
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'SHORT-NAME':
                name = self.parseTextNode(xmlElem)
            if xmlElem.tag == 'MODE-GROUP-IREF':
                for childElem in xmlElem.findall('./*'):
                    if childElem.tag == 'R-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF':
                        if modeGroupInstanceRef is None:
                            modeGroupInstanceRef=self._parseRequireModeGroupInstanceRef(childElem)
                        else:
                            handleNotImplementedError('Multiple instances of R-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF not implemented')
                    elif childElem.tag == 'P-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF':
                        if modeGroupInstanceRef is None:
                            modeGroupInstanceRef=self._parseProvideModeGroupInstanceRef(childElem)
                        else:
                            handleNotImplementedError('Multiple instances of P-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF not implemented')
                    else:
                        handleNotImplementedError(childElem.tag)
            else:
                handleNotImplementedError(xmlElem.tag)
        return autosar.behavior.ModeAccessPoint(name, modeGroupInstanceRef)

    @parseElementUUID
    def _parseModeSwitchPoint(self, xmlRoot):
        assert(xmlRoot.tag == 'MODE-SWITCH-POINT')
        (name, modeGroupInstanceRef) = (None, None)
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'SHORT-NAME':
                name = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'MODE-GROUP-IREF':
                modeGroupInstanceRef=self._parseProvideModeGroupInstanceRef(xmlElem)
            else:
                handleNotImplementedError(xmlElem.tag)
        return autosar.behavior.ModeSwitchPoint(name, modeGroupInstanceRef)

    @parseElementUUID
    def _parseVariableAccess(self, xmlRoot):
        assert(xmlRoot.tag == 'VARIABLE-ACCESS')
        variableAccess = None
        self.push()
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'ACCESSED-VARIABLE':
                variableAccess = self.parseAccessedVariable(xmlElem)
            else:
                self.defaultHandler(xmlElem)
        obj = autosar.behavior.VariableAccess(self.name, variableAccess.portPrototypeRef, variableAccess.targetDataPrototypeRef)
        self.pop()
        return obj

    @parseElementUUID
    def _parseLocalVariableAccess(self, xmlRoot):
        assert(xmlRoot.tag == 'VARIABLE-ACCESS')
        name = None
        self.push()
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'ACCESSED-VARIABLE':
                variableAccess = self.parseLocalAccessedVariable(xmlElem)
            else:
                handleNotImplementedError(xmlElem.tag)
        obj = autosar.behavior.LocalVariableAccess(self.name, variableAccess.localVariableRef)
        self.pop()
        return obj

    @parseElementUUID
    def parseParameterAccessPoint(self, xmlRoot, parent = None):
        assert(xmlRoot.tag == 'PARAMETER-ACCESS')
        (name, accessedParameter, swDataDefProps) = (None, None, None)
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'SHORT-NAME':
                name = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'ACCESSED-PARAMETER':
                for xmlChild in xmlElem.findall('./*'):
                    if xmlChild.tag == 'AUTOSAR-PARAMETER-IREF':
                        accessedParameter = self.parseParameterInstanceRef(xmlChild)
                    elif xmlChild.tag == 'LOCAL-PARAMETER-REF':
                        accessedParameter = autosar.behavior.LocalParameterRef(self.parseTextNode(xmlChild))
                    else:
                        handleNotImplementedError(xmlChild.tag)
            elif xmlElem.tag == 'SW-DATA-DEF-PROPS':
                swDataDefProps = self.parseSwDataDefProps(xmlElem)
            else:
                handleNotImplementedError(xmlElem.tag)
        if (name is not None) and (accessedParameter is not None):
            return autosar.behavior.ParameterAccessPoint(name, accessedParameter, swDataDefProps=swDataDefProps)

    def _parseRequireModeGroupInstanceRef(self, xmlRoot):
        """parses <R-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF>"""
        assert(xmlRoot.tag == 'R-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF')
        (requirePortRef, modeGroupRef ) = (None, None)
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'CONTEXT-R-PORT-REF':
                requirePortRef = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'TARGET-MODE-GROUP-REF':
                modeGroupRef = self.parseTextNode(xmlElem)
            else:
                handleNotImplementedError(xmlElem.tag)
        if requirePortRef is None:
            raise RuntimeError('CONTEXT-R-PORT-REF not set')
        if modeGroupRef is None:
            raise RuntimeError('TARGET-MODE-GROUP-REF not set')
        return autosar.behavior.RequireModeGroupInstanceRef(requirePortRef, modeGroupRef)

    def _parseProvideModeGroupInstanceRef(self, xmlRoot):
        """parses <P-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF>"""
        #This XML item exists multiple times (at least 4 different places) in the AUTOSAR 4 XSD using different XML tag.
        assert(xmlRoot.tag in ['P-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF', 'MODE-GROUP-IREF'])
        (providePortRef, modeGroupRef ) = (None, None)
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'CONTEXT-P-PORT-REF':
                providePortRef = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'TARGET-MODE-GROUP-REF':
                modeGroupRef = self.parseTextNode(xmlElem)
            else:
                handleNotImplementedError(xmlElem.tag)
        if providePortRef is None:
            raise RuntimeError('CONTEXT-P-PORT-REF not set')
        if modeGroupRef is None:
            raise RuntimeError('TARGET-MODE-GROUP-REF not set')
        return autosar.behavior.ProvideModeGroupInstanceRef(providePortRef, modeGroupRef)

    def parseModeInstanceRef(self, xmlRoot):
        """parses <MODE-IREF>"""
        assert(xmlRoot.tag == 'MODE-IREF')
        if self.version < 4.0:
            modeDeclarationRef=self.parseTextNode(xmlRoot.find('MODE-DECLARATION-REF'))
            modeDeclarationGroupPrototypeRef = self.parseTextNode(xmlRoot.find('MODE-DECLARATION-GROUP-PROTOTYPE-REF'))
            requirePortPrototypeRef = self.parseTextNode(xmlRoot.find('R-PORT-PROTOTYPE-REF'))
        elif self.version >= 4.0:
            modeDeclarationRef=self.parseTextNode(xmlRoot.find('TARGET-MODE-DECLARATION-REF'))
            modeDeclarationGroupPrototypeRef = self.parseTextNode(xmlRoot.find('CONTEXT-MODE-DECLARATION-GROUP-PROTOTYPE-REF'))
            requirePortPrototypeRef = self.parseTextNode(xmlRoot.find('CONTEXT-PORT-REF'))
        else:
            raise NotImplemented('version: '+self.version)
        return autosar.behavior.ModeInstanceRef(modeDeclarationRef,modeDeclarationGroupPrototypeRef,requirePortPrototypeRef)

    def parseParameterInstanceRef(self, xmlRoot):
        """parses <AUTOSAR-PARAMETER-IREF>"""
        assert(xmlRoot.tag == 'AUTOSAR-PARAMETER-IREF')
        (portRef, parameterDataRef, rootParameterDataRef, contextDataRef) = (None, None, None, None)

        for itemXML in xmlRoot.findall("./*"):
            tag = itemXML.tag

            if tag == "PORT-PROTOTYPE-REF":
                portRef = self.parseTextNode(itemXML)
            elif tag == "TARGET-DATA-PROTOTYPE-REF":
                parameterDataRef = self.parseTextNode(itemXML)
            elif tag == "ROOT-PARAMETER-DATA-PROTOTYPE-REF":
                rootParameterDataRef = self.parseTextNode(itemXML)
            elif tag == "CONTEXT-DATA-PROTOTYPE-REF":
                contextDataRef = self.parseTextNode(itemXML)
            else:
                raise RuntimeError(f"ERROR: Tag {tag} not recognized")

        return autosar.behavior.ParameterInstanceRef(portRef, parameterDataRef, rootParameterDataRef, contextDataRef)

    def _parseModeDependency(self,xmlRoot,parent=None):
        """parses <MODE-DEPENDENCY>"""
        assert(xmlRoot.tag == 'MODE-DEPENDENCY')
        modeDependency=autosar.behavior.ModeDependency()
        if xmlRoot.find('DEPENDENT-ON-MODE-IREFS') is not None:
            for xmlNode in xmlRoot.findall('./DEPENDENT-ON-MODE-IREFS/DEPENDENT-ON-MODE-IREF'):
                modeInstanceRef = self._parseDependentOnModeInstanceRef(xmlNode)
                if modeInstanceRef is not None:
                    modeDependency.modeInstanceRefs.append(modeInstanceRef)
        return modeDependency

    def _parseDependentOnModeInstanceRef(self,xmlRoot,parent=None):
        """parses <DEPENDENT-ON-MODE-IREF>"""
        assert(xmlRoot.tag == 'DEPENDENT-ON-MODE-IREF')
        modeDeclarationRef=self.parseTextNode(xmlRoot.find('MODE-DECLARATION-REF'))
        modeDeclarationGroupPrototypeRef = self.parseTextNode(xmlRoot.find('MODE-DECLARATION-GROUP-PROTOTYPE-REF'))
        requirePortPrototypeRef = self.parseTextNode(xmlRoot.find('R-PORT-PROTOTYPE-REF'))
        return autosar.behavior.ModeDependencyRef(modeDeclarationRef,modeDeclarationGroupPrototypeRef,requirePortPrototypeRef)

    def _parseDisabledModesInstanceRefs(self,xmlRoot,parent=None):
        """parses <DISABLED-MODE-IREFS>"""
        assert(xmlRoot.tag == 'DISABLED-MODE-IREFS')
        disabledInModes = []
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'DISABLED-MODE-IREF':
                disabledInModes.append(self._parseDisabledModeInstanceRef(xmlElem))
            else:
                handleNotImplementedError(xmlElem.tag)
        return disabledInModes

    def _parseDisabledModeInstanceRef(self, xmlRoot):
        """parses <DISABLED-MODE-IREF>"""
        (requirePortPrototypeRef, modeDeclarationGroupPrototypeRef, modeDeclarationRef) = (None, None, None)
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'CONTEXT-PORT-REF':
                requirePortPrototypeRef = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'CONTEXT-MODE-DECLARATION-GROUP-PROTOTYPE-REF':
                modeDeclarationGroupPrototypeRef = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'TARGET-MODE-DECLARATION-REF':
                modeDeclarationRef = self.parseTextNode(xmlElem)
            else:
                handleNotImplementedError(xmlElem.tag)
        if (modeDeclarationRef is not None) and (modeDeclarationGroupPrototypeRef is not None) and (requirePortPrototypeRef is not None):
            return autosar.behavior.DisabledModeInstanceRef(modeDeclarationRef,modeDeclarationGroupPrototypeRef,requirePortPrototypeRef)
        else:
            raise RuntimeError('Parse Error: <CONTEXT-PORT-REF DEST>, <CONTEXT-MODE-DECLARATION-GROUP-PROTOTYPE-REF> and <TARGET-MODE-DECLARATION-REF> must be defined')

    @parseElementUUID
    def parseInitEvent(self,xmlNode,parent=None):
        name = self.parseTextNode(xmlNode.find('SHORT-NAME'))
        startOnEventRef = self.parseTextNode(xmlNode.find('START-ON-EVENT-REF'))
        initEvent=autosar.behavior.InitEvent(name, startOnEventRef, parent)
        return initEvent

    @parseElementUUID
    def parseModeSwitchEvent(self,xmlNode,parent=None):
        """parses AUTOSAR3 <MODE-SWITCH-EVENT>"""
        if self.version < 4.0:
            assert(xmlNode.tag=='MODE-SWITCH-EVENT')
            name = self.parseTextNode(xmlNode.find('SHORT-NAME'))
            modeInstRef = self.parseModeInstanceRef(xmlNode.find('MODE-IREF'))
            startOnEventRef = self.parseTextNode(xmlNode.find('START-ON-EVENT-REF'))
            activation = self.parseTextNode(xmlNode.find('ACTIVATION'))
            modeSwitchEvent=autosar.behavior.ModeSwitchEvent(name, startOnEventRef, activation, parent, self.version)
            modeSwitchEvent.modeInstRef=modeInstRef
        elif self.version >= 4.0:
            assert(xmlNode.tag=='SWC-MODE-SWITCH-EVENT')
            name = self.parseTextNode(xmlNode.find('SHORT-NAME'))
            modeInstanceRefs = []
            for xmlElem in xmlNode.findall('./MODE-IREFS/*'):
                if xmlElem.tag == 'MODE-IREF':
                    modeInstanceRefs.append(self.parseModeInstanceRef(xmlElem))
                else:
                    handleNotImplementedError(xmlElem.tag)
            startOnEventRef = self.parseTextNode(xmlNode.find('START-ON-EVENT-REF'))
            activation = self.parseTextNode(xmlNode.find('ACTIVATION'))
            modeSwitchEvent=autosar.behavior.ModeSwitchEvent(name, startOnEventRef, activation, parent, self.version)
            modeSwitchEvent.modeInstRef=modeInstanceRefs[0]
        else:
            handleNotImplementedError('version: '+self.version)
        return modeSwitchEvent

    @parseElementUUID
    def parseModeSwitchedAckEvent(self, xmlNode, parent = None):
        if self.version < 4.0:
            handleNotImplementedError(xmlNode.tag)
        else:
            assert(xmlNode.tag=='MODE-SWITCHED-ACK-EVENT')
            (name, startOnEventRef, eventSourceRef, xmlDisabledModeRefs) = (None, None, None, None)
            for xmlElem in xmlNode.findall('./*'):
                if xmlElem.tag == 'SHORT-NAME':
                    name = self.parseTextNode(xmlElem)
                elif xmlElem.tag == 'DISABLED-MODE-IREFS':
                    xmlDisabledModeRefs = xmlElem
                elif xmlElem.tag == 'START-ON-EVENT-REF':
                    startOnEventRef = self.parseTextNode(xmlElem)
                elif xmlElem.tag == 'EVENT-SOURCE-REF':
                    eventSourceRef = self.parseTextNode(xmlElem)
                else:
                    handleNotImplementedError(xmlElem.tag)
            modeSwitchEvent = autosar.behavior.ModeSwitchAckEvent(name, startOnEventRef, eventSourceRef, parent)
            if xmlDisabledModeRefs is not None:
                modeSwitchEvent.disabledInModes = self._parseDisabledModesInstanceRefs(xmlDisabledModeRefs, parent)
            return modeSwitchEvent

    @parseElementUUID
    def parseTimingEvent(self,xmlNode,parent=None):
        (name, startOnEventRef, period, xmlModeDepency, xmlDisabledModeRefs) = (None, None, None, None, None)
        for xmlElem in xmlNode.findall('./*'):
            if xmlElem.tag == 'SHORT-NAME':
                name = self.parseTextNode(xmlElem)
            elif self.version >= 4.0 and xmlElem.tag == 'DISABLED-MODE-IREFS':
                xmlDisabledModeRefs =xmlElem
            elif self.version < 4.0 and xmlElem.tag == 'MODE-DEPENDENCY':
                xmlModeDepency =xmlElem
            elif xmlElem.tag == 'START-ON-EVENT-REF':
                startOnEventRef = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'PERIOD':
                period = self.parseTextNode(xmlElem)
            else:
                handleNotImplementedError(xmlElem.tag)

        if (name is not None) and (startOnEventRef is not None) and (period is not None):
            timingEvent=autosar.behavior.TimingEvent(name, startOnEventRef, float(period)*1000, parent)
            if xmlModeDepency is not None:
                timingEvent.modeDependency = self._parseModeDependency(xmlModeDepency, parent)
            elif xmlDisabledModeRefs is not None:
                timingEvent.disabledInModes = self._parseDisabledModesInstanceRefs(xmlDisabledModeRefs, parent)
            return timingEvent
        else:
            raise RuntimeError('Parse error: <SHORT-NAME> and <START-ON-EVENT-REF> and <PERIOD> must be defined')

    @parseElementUUID
    def parseDataReceivedEvent(self,xmlRoot,parent=None):
        name = self.parseTextNode(xmlRoot.find('SHORT-NAME'))
        startOnEventRef = self.parseTextNode(xmlRoot.find('START-ON-EVENT-REF'))
        portTag = 'CONTEXT-R-PORT-REF' if self.version >= 4.0 else 'R-PORT-PROTOTYPE-REF'
        dataInstanceRef=self.parseDataInstanceRef(xmlRoot.find('DATA-IREF'),portTag)
        dataReceivedEvent=autosar.behavior.DataReceivedEvent(name, startOnEventRef, parent)
        xmlModeDependency = xmlRoot.find('MODE-DEPENDENCY')
        if xmlModeDependency is not None:
            dataReceivedEvent.modeDependency = self._parseModeDependency(xmlModeDependency)
        dataReceivedEvent.dataInstanceRef=dataInstanceRef
        return dataReceivedEvent

    @parseElementUUID
    def parseOperationInvokedEvent(self,xmlRoot,parent=None):
        (name, startOnEventRef, modeDependency, operationInstanceRef) = (None, None, None, None)
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'SHORT-NAME':
                name = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'START-ON-EVENT-REF':
                startOnEventRef = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'OPERATION-IREF':
                portTag = 'CONTEXT-P-PORT-REF' if self.version >= 4.0 else 'P-PORT-PROTOTYPE-REF'
                operationInstanceRef = self.parseOperationInstanceRef(xmlElem, portTag)
            elif xmlElem.tag == 'MODE-DEPENDENCY':
                modeDependency = self._parseModeDependency(xmlElem)
            else:
                handleNotImplementedError(xmlElem.tag)
        operationInvokedEvent=autosar.behavior.OperationInvokedEvent(name, startOnEventRef, parent)
        operationInvokedEvent.modeDependency = modeDependency
        operationInvokedEvent.operationInstanceRef = operationInstanceRef
        return operationInvokedEvent

    def parseDataInstanceRef(self, xmlRoot, portTag):
        """parses <DATA-IREF>"""
        assert(xmlRoot.tag=='DATA-IREF')
        dataElemTag = 'TARGET-DATA-ELEMENT-REF' if self.version >= 4.0 else 'DATA-ELEMENT-PROTOTYPE-REF'
        (portRef, dataElemRef) = (None, None)
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == portTag:
                portRef = self.parseTextNode(xmlElem)
            elif xmlElem.tag == dataElemTag:
                dataElemRef = self.parseTextNode(xmlElem)
            else:
                handleNotImplementedError(xmlElem.tag)
        return autosar.behavior.DataInstanceRef(portRef,dataElemRef)

    def parseOperationInstanceRef(self,xmlRoot,portTag):
        """parses <OPERATION-IREF>"""
        assert(xmlRoot.tag=='OPERATION-IREF')
        assert(xmlRoot.find(portTag) is not None)

        if self.version >= 4.0:
            if portTag == 'CONTEXT-P-PORT-REF':
                operationTag = 'TARGET-PROVIDED-OPERATION-REF'
            else:
                operationTag = 'TARGET-REQUIRED-OPERATION-REF'
        else:
            operationTag = 'OPERATION-PROTOTYPE-REF'
        return autosar.behavior.OperationInstanceRef(self.parseTextNode(xmlRoot.find(portTag)),self.parseTextNode(xmlRoot.find(operationTag)))


    def parseDataElementInstanceRef(self,xmlRoot,portTag):
        """parses <DATA-ELEMENT-IREF>"""
        assert(xmlRoot.tag=='DATA-ELEMENT-IREF')
        assert(xmlRoot.find(portTag) is not None)
        return autosar.behavior.DataElementInstanceRef(self.parseTextNode(xmlRoot.find(portTag)),self.parseTextNode(xmlRoot.find('DATA-ELEMENT-PROTOTYPE-REF')))

    def parseSwcNvBlockNeeds(self,xmlRoot):
        name=self.parseTextNode(xmlRoot.find('SHORT-NAME'))
        numberOfDataSets=self.parseIntNode(xmlRoot.find('N-DATA-SETS'))
        readOnly=self.parseBooleanNode(xmlRoot.find('READONLY'))
        reliability=self.parseTextNode(xmlRoot.find('RELIABILITY'))
        resistantToChangedSW=self.parseBooleanNode(xmlRoot.find('RESISTANT-TO-CHANGED-SW'))
        restoreAtStart=self.parseBooleanNode(xmlRoot.find('RESTORE-AT-START'))
        writeOnlyOnce=self.parseBooleanNode(xmlRoot.find('WRITE-ONLY-ONCE'))
        writingFrequency=self.parseIntNode(xmlRoot.find('WRITING-FREQUENCY'))
        writingPriority=self.parseTextNode(xmlRoot.find('WRITING-PRIORITY'))
        defaultBlockRef=self.parseTextNode(xmlRoot.find('DEFAULT-BLOCK-REF'))
        mirrorBlockRef=self.parseTextNode(xmlRoot.find('MIRROR-BLOCK-REF'))
        serviceCallPorts=self.parseServiceCallPorts(xmlRoot.find('SERVICE-CALL-PORTS'))
        assert(len(serviceCallPorts)>0)
        swcNvBlockNeeds=autosar.behavior.SwcNvBlockNeeds(name,numberOfDataSets,readOnly,reliability,resistantToChangedSW,restoreAtStart,
                                        writeOnlyOnce,writingFrequency,writingPriority,defaultBlockRef,mirrorBlockRef)
        swcNvBlockNeeds.serviceCallPorts=serviceCallPorts
        return swcNvBlockNeeds

    def parseServiceCallPorts(self,xmlRoot):
        """parses <SERVICE-CALL-PORTS>"""
        assert(xmlRoot.tag=='SERVICE-CALL-PORTS')
        serviceCallPorts=[]
        for xmlNode in xmlRoot.findall('ROLE-BASED-R-PORT-ASSIGNMENT'):
            roleBasedRPortAssignment=autosar.behavior.RoleBasedRPortAssignment(self.parseTextNode(xmlNode.find('R-PORT-PROTOTYPE-REF')),self.parseTextNode(xmlNode.find('ROLE')))
            serviceCallPorts.append(roleBasedRPortAssignment)
        return serviceCallPorts

    @parseElementUUID
    def parseCalPrmElemPrototype(self, xmlRoot, parent):
        """
        parses <CALPRM-ELEMENT-PROTOTYPE>
        """
        name = self.parseTextNode(xmlRoot.find('SHORT-NAME'))
        adminData=self.parseAdminDataNode(xmlRoot.find('ADMIN-DATA'))
        typeRef = self.parseTextNode(xmlRoot.find('TYPE-TREF'))
        calPrmElemPrototype = autosar.behavior.CalPrmElemPrototype(name, typeRef, parent, adminData)
        for xmlElem in xmlRoot.findall('./SW-DATA-DEF-PROPS/*'):
            if xmlElem.tag=='SW-ADDR-METHOD-REF':
                calPrmElemPrototype.swDataDefsProps.append(self.parseTextNode(xmlElem))
            else:
                handleNotImplementedError(xmlElem.tag)
        return calPrmElemPrototype

    def _parseServerCallPoint(self, xmlRoot, callType):
        timeout=0.0
        if self.version >= 4.0:
            operationInstanceRefs=[]
            for xmlElem in xmlRoot.findall('*'):
                if xmlElem.tag=='SHORT-NAME':
                    name=self.parseTextNode(xmlElem)
                elif xmlElem.tag=='OPERATION-IREF':
                    operationInstanceRefs.append(self.parseOperationInstanceRef(xmlElem,'CONTEXT-R-PORT-REF'))
                elif xmlElem.tag=='TIMEOUT':
                    timeout=self.parseFloatNode(xmlElem)
                else:
                    handleNotImplementedError(xmlElem.tag)
        else:
            for xmlElem in xmlRoot.findall('*'):
                if xmlElem.tag=='SHORT-NAME':
                    name=self.parseTextNode(xmlElem)
                elif xmlElem.tag=='OPERATION-IREFS':
                    operationInstanceRefs=[]
                    for xmlOperation in xmlElem.findall('*'):
                        if xmlOperation.tag=='OPERATION-IREF':
                            operationInstanceRefs.append(self.parseOperationInstanceRef(xmlOperation,'R-PORT-PROTOTYPE-REF'))
                        else:
                            handleNotImplementedError(xmlElem.tag)
                elif xmlElem.tag=='TIMEOUT':
                    timeout=self.parseFloatNode(xmlElem)
                else:
                    handleNotImplementedError(xmlElem.tag)
        retval=callType(name,timeout)
        retval.operationInstanceRefs=operationInstanceRefs
        return retval
    
    def parseAsyncServerCallPoint(self, xmlRoot):
        """
        parses <ASYNCHRONOUS-SERVER-CALL-POINT>
        """
        assert(xmlRoot.tag=='ASYNCHRONOUS-SERVER-CALL-POINT')
        return self._parseServerCallPoint(xmlRoot, autosar.behavior.AsyncServerCallPoint)

    def parseSyncServerCallPoint(self, xmlRoot):
        """
        parses <SYNCHRONOUS-SERVER-CALL-POINT>
        """
        assert(xmlRoot.tag=='SYNCHRONOUS-SERVER-CALL-POINT')
        return self._parseServerCallPoint(xmlRoot, autosar.behavior.SyncServerCallPoint)

    @parseElementUUID
    def parseAccessedVariable(self, xmlRoot):
        assert(xmlRoot.tag == 'ACCESSED-VARIABLE')

        xmlPortPrototypeRef = xmlRoot.find('./AUTOSAR-VARIABLE-IREF/PORT-PROTOTYPE-REF')
        xmlTargetDataPrototypeRef = xmlRoot.find('./AUTOSAR-VARIABLE-IREF/TARGET-DATA-PROTOTYPE-REF')
        assert (xmlPortPrototypeRef is not None)
        assert (xmlTargetDataPrototypeRef is not None)
        return autosar.behavior.VariableAccess(self.parseTextNode(xmlRoot.find('SHORT-NAME')), self.parseTextNode(xmlPortPrototypeRef), self.parseTextNode(xmlTargetDataPrototypeRef))

    @parseElementUUID
    def parseLocalAccessedVariable(self, xmlRoot, local = False):
        assert(xmlRoot.tag == 'ACCESSED-VARIABLE')

        xmlLocalVariableRef = xmlRoot.find('./LOCAL-VARIABLE-REF')
        assert xmlLocalVariableRef is not None

        return autosar.behavior.LocalVariableAccess(self.parseTextNode(xmlRoot.find('SHORT-NAME')), self.parseTextNode(xmlLocalVariableRef))

    @parseElementUUID
    def parseSwcServiceDependency(self, xmlRoot, parent = None):
        """parses <SWC-SERVICE-DEPENDENCY>"""
        assert(xmlRoot.tag == 'SWC-SERVICE-DEPENDENCY')
        (name, desc, serviceNeeds) = (None, None, None)
        roleBasedDataAssignments = []
        roleBasedPortAssignments = []
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'SHORT-NAME':
                name = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'DESC':
                desc = self.parseDescDirect(xmlElem)
            elif xmlElem.tag == 'ASSIGNED-DATAS':
                for xmlChildElem in xmlElem.findall('./*'):
                    if xmlChildElem.tag == 'ROLE-BASED-DATA-ASSIGNMENT':
                        tmp = self._parseRoleBasedDataAssignment(xmlChildElem)
                        if tmp is not None: roleBasedDataAssignments.append(tmp)
                    else:
                        handleNotImplementedError(xmlChildElem.tag)
            elif xmlElem.tag == 'ASSIGNED-PORTS':
                for xmlChildElem in xmlElem.findall('./*'):
                    if xmlChildElem.tag == 'ROLE-BASED-PORT-ASSIGNMENT':
                        tmp = self._parseRoleBasedPortAssignment(xmlChildElem)
                        if tmp is not None: roleBasedPortAssignments.append(tmp)
                    else:
                        handleNotImplementedError(xmlChildElem.tag)
            elif xmlElem.tag == 'SERVICE-NEEDS':
                serviceNeeds = self.parseServiceNeeds(xmlElem)
            else:
                handleNotImplementedError(xmlElem.tag)
        swcServiceDependency = autosar.behavior.SwcServiceDependency(name, parent = parent)
        if desc is not None:
            swcServiceDependency.desc=desc[0]
            swcServiceDependency.descAttr=desc[1]
        if serviceNeeds is not None:
            swcServiceDependency.serviceNeeds = serviceNeeds
        if len(roleBasedDataAssignments) > 0:
            swcServiceDependency.roleBasedDataAssignments = roleBasedDataAssignments
        if len(roleBasedPortAssignments) > 0:
            swcServiceDependency.roleBasedPortAssignments = roleBasedPortAssignments
        return swcServiceDependency


    @parseElementUUID
    def parseParameterDataPrototype(self, xmlRoot, parent = None):
        """parses <PARAMETER-DATA-PROTOTYPE> (AUTOSAR 4)"""
        return self.parseAutosarDataPrototype(xmlRoot, parent)

    @parseElementUUID
    def parseServiceNeeds(self, xmlRoot, parent = None):
        """parses <SERVICE-NEEDS> (AUTOSAR 4)"""
        assert(xmlRoot.tag == 'SERVICE-NEEDS')
        (xmlNvBlockNeeds, xmlDiagnosticEventNeeds, xmlDiagnosticEventManagerNeeds, xmlDiagnosticCommunicationManagerNeeds) = (None, None, None, None)
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'NV-BLOCK-NEEDS':
                xmlNvBlockNeeds = xmlElem
            elif xmlElem.tag == 'DIAGNOSTIC-EVENT-NEEDS':
                xmlDiagnosticEventNeeds = xmlElem
            elif xmlElem.tag == 'DIAGNOSTIC-EVENT-MANAGER-NEEDS':
                xmlDiagnosticEventManagerNeeds = xmlElem
            elif xmlElem.tag == 'DIAGNOSTIC-COMMUNICATION-MANAGER-NEEDS':
                xmlDiagnosticCommunicationManagerNeeds = xmlElem
            else:
                handleNotImplementedError(xmlElem.tag)
        serviceNeeds = autosar.behavior.ServiceNeeds()
        if xmlNvBlockNeeds is not None:
            serviceNeeds.nvmBlockNeeds = self.parseNvmBlockNeeds(xmlElem, serviceNeeds)
        if xmlDiagnosticEventNeeds is not None:
            serviceNeeds.diagnosticEventNeeds = self.parseDiagnosticEventNeeds(xmlElem, serviceNeeds)
        if xmlDiagnosticEventManagerNeeds is not None:
            serviceNeeds.diagnosticEventManagerNeeds = self.parseDiagnosticEventManagerNeeds(xmlElem, serviceNeeds)
        if xmlDiagnosticCommunicationManagerNeeds is not None:
            serviceNeeds.diagnosticCommunicationManagerNeeds = self.parseDiagnosticCommunicationManagerNeeds(xmlElem, serviceNeeds)
        return serviceNeeds

    def parseNvmBlockNeeds(self, xmlRoot, parent = None):
        """parses <NV-BLOCK-NEEDS> (AUTOSAR 4)"""
        config = autosar.behavior.NvmBlockConfig()

        self.push()
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'N-DATA-SETS':
                config.numberOfDataSets = self.parseIntNode(xmlElem)
            elif xmlElem.tag == 'N-ROM-BLOCKS':
                config.numberOfRomBlocks = self.parseIntNode(xmlElem)
            elif xmlElem.tag == 'RAM-BLOCK-STATUS-CONTROL':
                config.ramBlockStatusControl = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'RELIABILITY':
                config.reliability = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'WRITING-PRIORITY':
                config.writingPriority = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'WRITING-FREQUENCY':
                config.writingFrequency = self.parseIntNode(xmlElem)
            elif xmlElem.tag == 'CALC-RAM-BLOCK-CRC':
                config.calcRamBlockCrc = self.parseBooleanNode(xmlElem)
            elif xmlElem.tag == 'CHECK-STATIC-BLOCK-ID':
                config.checkStaticBlockId = self.parseBooleanNode(xmlElem)
            elif xmlElem.tag == 'READONLY':
                config.readOnly = self.parseBooleanNode(xmlElem)
            elif xmlElem.tag == 'RESISTANT-TO-CHANGED-SW':
                config.resistantToChangedSw = self.parseBooleanNode(xmlElem)
            elif xmlElem.tag == 'RESTORE-AT-START':
                config.restoreAtStartup = self.parseBooleanNode(xmlElem)
            elif xmlElem.tag == 'STORE-AT-SHUTDOWN':
                config.storeAtShutdown = self.parseBooleanNode(xmlElem)
            elif xmlElem.tag == 'WRITE-VERIFICATION':
                config.writeVerification = self.parseBooleanNode(xmlElem)
            elif xmlElem.tag == 'WRITE-ONLY-ONCE':
                config.writeOnlyOnce = self.parseBooleanNode(xmlElem)
            elif xmlElem.tag == 'USE-AUTO-VALIDATION-AT-SHUT-DOWN':
                config.autoValidationAtShutdown = self.parseBooleanNode(xmlElem)
            elif xmlElem.tag == 'USE-CRC-COMP-MECHANISM':
                config.useCrcCompMechanism = self.parseBooleanNode(xmlElem)
            elif xmlElem.tag == 'STORE-EMERGENCY':
                config.storeEmergency = self.parseBooleanNode(xmlElem)
            elif xmlElem.tag == 'STORE-IMMEDIATE':
                config.storeImmediate = self.parseBooleanNode(xmlElem)
            elif xmlElem.tag == 'STORE-CYCLIC':
                config.storeCyclic = self.parseBooleanNode(xmlElem)
            elif xmlElem.tag == 'CYCLIC-WRITING-PERIOD':
                config.cyclicWritePeriod = self.parseFloatNode(xmlElem)
            else:
                self.baseHandler(xmlElem)

        if self.name is None:
            raise RuntimeError('<SHORT-NAME> is missing or incorrectly formatted')
        config.check()
        obj = autosar.behavior.NvmBlockNeeds(self.name, blockConfig = config, parent = parent, adminData = self.adminData)
        self.pop(obj)
        return obj

    def parseDiagnosticEventNeeds(self, xmlRoot, parent = None):
        """parses <DIAGNOSTIC-EVENT-NEEDS> (AUTOSAR 4)"""
        config = autosar.behavior.DiagnosticEventConfig()

        self.push()
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'CONSIDER-PTO-STATUS':
                config.considerPtoStatus = self.parseBooleanNode(xmlElem)
            elif xmlElem.tag == 'DEFERRING-FID-REFS':
                config.deferringFidRefs = []
                for xmlChild in xmlElem.findall('./DEFERRING-FID-REF'):
                    config.deferringFidRefs.append(self.parseTextNode(xmlChild))
            elif xmlElem.tag == 'DIAG-EVENT-DEBOUNCE-ALGORITHM':
                pass # implement later
            elif xmlElem.tag == 'DTC-KIND':
                config.dtcKind = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'DTC-NUMBER':
                config.dtcNumber = self.parseIntNode(xmlElem)
            elif xmlElem.tag == 'INHIBITING-FID-REF':
                config.inhibitingFidRef = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'INHIBITING-SECONDARY-FID-REFS':
                config.inhibitingSecondaryFidRefs = []
                for xmlChild in xmlElem.findall('./INHIBITING-SECONDARY-FID-REF'):
                    config.inhibitingSecondaryFidRefs.append(self.parseTextNode(xmlChild))
            elif xmlElem.tag == 'OBD-DTC-NUMBER':
                config.obdDtcNumber = self.parseIntNode(xmlElem)
            elif xmlElem.tag == 'PRESTORED-FREEZEFRAME-STORED-IN-NVM':
                config.prestoredFreezeframeStoredInNvm = self.parseBooleanNode(xmlElem)
            elif xmlElem.tag == 'REPORT-BEHAVIOR':
                config.reportBehavior = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'UDS-DTC-NUMBER':
                config.udsDtcNumber = self.parseIntNode(xmlElem)
            elif xmlElem.tag == 'USES-MONITOR-DATA':
                config.usesMonitorData = self.parseBooleanNode(xmlElem)
            else:
                self.baseHandler(xmlElem)

        if self.name is None:
            raise RuntimeError('<SHORT-NAME> is missing or incorrectly formatted')
        config.check()
        obj = autosar.behavior.DiagnosticEventNeeds(self.name, eventConfig = config, parent = parent, adminData = self.adminData)
        self.pop(obj)
        return obj

    def parseDiagnosticEventManagerNeeds(self, xmlRoot, parent = None):
        """parses <DIAGNOSTIC-EVENT-MANAGER-NEEDS> (AUTOSAR 4)"""
        self.push()
        for xmlElem in xmlRoot.findall('./*'):
            self.baseHandler(xmlElem)

        if self.name is None:
            raise RuntimeError('<SHORT-NAME> is missing or incorrectly formatted')

        obj = autosar.behavior.DiagnosticEventManagerNeeds(self.name, parent = parent, adminData = self.adminData)
        self.pop(obj)
        return obj
    
    def parseDiagnosticCommunicationManagerNeeds(self, xmlRoot, parent = None):
        """parses <DIAGNOSTIC-EVENT-NEEDS> (AUTOSAR 4)"""
        config = autosar.behavior.DiagnosticCommunicationManagerConfig()

        self.push()
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'SERVICE-REQUEST-CALLBACK-TYPE':
                config.serviceRequestCallbackType = self.parseTextNode(xmlElem)
            else:
                self.baseHandler(xmlElem)

        if self.name is None:
            raise RuntimeError('<SHORT-NAME> is missing or incorrectly formatted')
        config.check()
        obj = autosar.behavior.DiagnosticCommunicationManagerNeeds(self.name, config = config, parent = parent, adminData = self.adminData)
        self.pop(obj)
        return obj

    def _parseRoleBasedDataAssignment(self, xmlRoot):
        assert(xmlRoot.tag == 'ROLE-BASED-DATA-ASSIGNMENT')
        (role, localVariableRef, localParameterRef) = (None, None, None)

        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'ROLE':
                role = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'USED-DATA-ELEMENT':
                for xmlChild in xmlElem.findall('./*'):
                    if xmlChild.tag == 'LOCAL-VARIABLE-REF':
                        localVariableRef = self.parseTextNode(xmlChild)
                    else:
                        handleNotImplementedError(xmlChild.tag)
            elif xmlElem.tag == 'USED-PARAMETER-ELEMENT':
                pass
                for xmlChild in xmlElem.findall('./*'):
                    if xmlChild.tag == 'LOCAL-PARAMETER-REF':
                        localParameterRef = autosar.behavior.LocalParameterRef(self.parseTextNode(xmlChild))
                    else:
                        handleNotImplementedError(xmlChild.tag)
            else:
                handleNotImplementedError(xmlElem.tag)
        if (role is not None) and ( (localVariableRef is not None) or (localParameterRef is not None) ):
            return autosar.behavior.RoleBasedDataAssignment(role, localVariableRef, localParameterRef)
        return None


    def _parseRoleBasedPortAssignment(self, xmlRoot):
        assert(xmlRoot.tag == 'ROLE-BASED-PORT-ASSIGNMENT')
        (portRef, role) = (None, None)
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'PORT-PROTOTYPE-REF':
                portRef = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'ROLE':
                portRef = self.parseTextNode(xmlElem)
            else:
                self.baseHandler(xmlElem)
        if portRef is not None:
            return autosar.behavior.RoleBasedPortAssignment(portRef, role)
        return None

    def parseAutosarVariableRefXML(self, xmlRoot):
        (localVariableRef, portPrototypeRef, targetDataPrototypeRef) = (None, None, None)
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'LOCAL-VARIABLE-REF':
                localVariableRef = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'AUTOSAR-VARIABLE-IREF' or xmlElem.tag == 'AUTOSAR-VARIABLE-IN-IMPL-DATATYPE':
                xmlPortPrototypeRef = xmlElem.find('./PORT-PROTOTYPE-REF')
                xmlTargetDataPrototypeRef = xmlElem.find('./TARGET-DATA-PROTOTYPE-REF')
                assert (xmlPortPrototypeRef is not None)
                assert (xmlTargetDataPrototypeRef is not None)
                portPrototypeRef = self.parseTextNode(xmlPortPrototypeRef)
                targetDataPrototypeRef = self.parseTextNode(xmlTargetDataPrototypeRef)
        return localVariableRef, portPrototypeRef, targetDataPrototypeRef

    @parseElementUUID
    def parseNvBlockSWCnvBlockDescriptor(self, xmlRoot, parent):
        """AUTOSAR 4 NV-BLOCK-DESCRIPTOR"""
        assert(xmlRoot.tag == 'NV-BLOCK-DESCRIPTOR')
        name = self.parseTextNode(xmlRoot.find('SHORT-NAME'))
        ws = parent.rootWS()
        assert(ws is not None)
        if (name is not None):
            handledXML = ['SHORT-NAME']
            descriptor = autosar.behavior.NvBlockDescriptor(name, parent)
            for xmlElem in xmlRoot.findall('./*'):
                if xmlElem.tag in handledXML:
                    pass
                elif xmlElem.tag == 'DATA-TYPE-MAPPING-REFS':
                    for xmlChild in xmlElem.findall('./*'):
                        if xmlChild.tag == 'DATA-TYPE-MAPPING-REF':
                            tmp = self.parseTextNode(xmlChild)
                            if tmp is not None:
                                descriptor.dataTypeMappingRefs.append(tmp)
                elif xmlElem.tag == 'NV-BLOCK-DATA-MAPPINGS':
                    for xmlMapping in xmlElem.findall('./NV-BLOCK-DATA-MAPPING'):
                        dataMapping = autosar.behavior.NvBlockDataMapping(descriptor)
                        descriptor.nvBlockDataMappings.append(dataMapping)
                        for xmlData in xmlMapping.findall('./*'):
                            localVariableRef, portPrototypeRef, targetDataPrototypeRef = self.parseAutosarVariableRefXML(xmlData)
                            if xmlData.tag == 'NV-RAM-BLOCK-ELEMENT':
                                if localVariableRef is None:
                                    handleValueError('Cannot find needed LOCAL-VARIABLE-REF for NV-RAM-BLOCK-ELEMENT in {0}'.format(descriptor.name))
                                dataMapping.nvRamBlockElement = autosar.behavior.NvRamBlockElement(dataMapping, localVariableRef=localVariableRef)
                            elif xmlData.tag == 'READ-NV-DATA':
                                if portPrototypeRef is None and targetDataPrototypeRef is None:
                                    handleValueError('Cannot find needed AUTOSAR-VARIABLE-IREF or AUTOSAR-VARIABLE-IN-IMPL-DATATYPE for READ-NV-DATA in {0}'.format(descriptor.name))
                                dataMapping.readNvData = autosar.behavior.ReadNvData(dataMapping, autosarVariablePortRef=portPrototypeRef, autosarVariableElementRef=targetDataPrototypeRef)
                            elif xmlData.tag == 'WRITTEN-NV-DATA':
                                if portPrototypeRef is None and targetDataPrototypeRef is None:
                                    handleValueError('Cannot find needed AUTOSAR-VARIABLE-IREF or AUTOSAR-VARIABLE-IN-IMPL-DATATYPE for WRITTEN-NV-DATA in {0}'.format(descriptor.name))
                                dataMapping.writtenNvData = autosar.behavior.WrittenNvData(dataMapping, autosarVariablePortRef=portPrototypeRef, autosarVariableElementRef=targetDataPrototypeRef)
                            elif xmlData.tag == 'WRITTEN-READ-NV-DATA':
                                if portPrototypeRef is None and targetDataPrototypeRef is None:
                                    handleValueError('Cannot find needed AUTOSAR-VARIABLE-IREF or AUTOSAR-VARIABLE-IN-IMPL-DATATYPE for WRITTEN-READ-NV-DATA in {0}'.format(descriptor.name))
                                dataMapping.writtenReadNvData = autosar.behavior.WrittenReadNvData(dataMapping, autosarVariablePortRef=portPrototypeRef, autosarVariableElementRef=targetDataPrototypeRef)
                            else:
                                handleNotImplementedError(xmlData.tag)
                elif xmlElem.tag == 'NV-BLOCK-NEEDS':
                    descriptor.nvBlockNeeds = self.parseNvmBlockNeeds(xmlElem, descriptor)
                elif xmlElem.tag == 'RAM-BLOCK':
                    # Change tag so it is correct for the parser.
                    xmlElem.tag = 'VARIABLE-DATA-PROTOTYPE'
                    dataElement = self.parseAutosarDataPrototype(xmlElem, descriptor)
                    # Cast the object to correct class.
                    descriptor.ramBlock = autosar.behavior.NvBlockRamBlock.cast(dataElement)
                elif xmlElem.tag == 'ROM-BLOCK':
                    # Change tag so it is correct for the parser.
                    xmlElem.tag = 'PARAMETER-DATA-PROTOTYPE'
                    dataElement = self.parseParameterDataPrototype(xmlElem, descriptor)
                    # Cast the object to correct class.
                    descriptor.romBlock = autosar.behavior.NvBlockRomBlock.cast(dataElement)
                elif xmlElem.tag == 'SUPPORT-DIRTY-FLAG':
                    dirtyFlag = self.parseBooleanNode(xmlElem)
                    if dirtyFlag is not None:
                        descriptor.supportDirtyFlag = dirtyFlag
                elif xmlElem.tag == 'TIMING-EVENT-REF':
                    timingRef = self.parseTextNode(xmlElem)
                    parts = timingRef.partition('/')
                    while True:
                        if parts[0] == parent.name:
                            timingEvent = parent.find(parts[2])
                            if timingEvent is not None:
                                break
                        elif len(parts[2]) == 0:
                            break
                        parts = parts[2].partition('/')

                    if timingEvent is None:
                        handleValueError('Cannot find timing event {0}'.format(timingRef))
                    descriptor.timingEventRef = timingEvent.name
                else:
                    handleNotImplementedError(xmlElem.tag)
            return descriptor

    @parseElementUUID
    def parseIncludedDataTypeSet(self, xmlRoot):
        """parses <INCLUDED-DATA-TYPE-SET>"""

        assert xmlRoot.tag == 'INCLUDED-DATA-TYPE-SET'
        (dataTypeRefs, literalPrefix) = ([], None)

        for item in xmlRoot.findall("./*"):
            tag = item.tag

            if tag == "DATA-TYPE-REFS":
                for dtrItem in item.findall("./*"):
                    if dtrItem.tag == "DATA-TYPE-REF":
                        dataTypeRefs.append(self.parseTextNode(dtrItem))
                    else: 
                        raise RuntimeError(f"Tag '{tag}' is not present in the AUTOSAR specification for the DATA-TYPE-REFS element")

            elif tag == "LITERAL-PREFIX":
                literalPrefix = self.parseTextNode(item)
            else:
                raise RuntimeError(f"Tag '{tag}' is not present in the AUTOSAR specification for the INCLUDED-DATA-TYPE-SET element")

        return autosar.behavior.IncludedDataTypeSet(dataTypeRefs=dataTypeRefs, literalPrefix=literalPrefix)

    @parseElementUUID
    def parseVariationPointProxy(self, xmlRoot, parent):
        """parses <VARIATION-POINT-PROXY>"""

        assert xmlRoot.tag == 'VARIATION-POINT-PROXY'
        (name, category, binding_time, condition_access) = (None, None, None, None)

        category_items = xmlRoot.findall("./CATEGORY")
        assert len(category_items) == 1, f"Exactly one CATEGORY element is required in the VARIATION-POINT-PROXY element (see '{parent.ref}')"

        category = self.parseTextNode(category_items[0])

        for item in xmlRoot.findall("./*"):
            tag = item.tag
            
            if tag == "SHORT-NAME":
                name = self.parseTextNode(item)
            elif tag == "CATEGORY":
                continue # Already evaluated
            elif tag == "CONDITION-ACCESS":
                if category != "CONDITION":
                    raise RuntimeError("CONDITION-ACCESS is only allowed when the category is 'CONDITION'")
                binding_time = item.get("BINDING-TIME")
                # TODO: Implement condition by formula parsing
                condition_access = ''.join(item.itertext())
            elif tag == "VALUE-ACCESS":
                if category != "VALUE":
                    raise RuntimeError("VALUE-ACCESS is only allowed when the category is 'VALUE'")
                binding_time = item.get("BINDING-TIME")
                # TODO: Implement
                handleNotImplementedError(tag)
            elif tag == "IMPLEMENTATION-DATA-TYPE-REF":
                if category != "VALUE":
                    raise RuntimeError("IMPLEMENTATION-DATA-TYPE-REF is only allowed when the category is 'VALUE'")
                # TODO: Implement
                handleNotImplementedError(tag)
            elif tag == "POST-BUILD-VALUE-ACCESS-REF":
                if category != "VALUE":
                    raise RuntimeError("POST-BUILD-VALUE-ACCESS-REF is only allowed when the category is 'VALUE'")
                # TODO: Implement
                handleNotImplementedError(tag)
            elif tag == "POST-BUILD-VARIANT-CONDITIONS":
                if category != "CONDITION":
                    raise RuntimeError("POST-BUILD-VARIANT-CONDITIONS is only allowed when the category is 'CONDITION'")
                # TODO: Implement
                handleNotImplementedError(tag)
            else:
                raise RuntimeError(f"Tag '{tag}' is not present in the AUTOSAR specification for the VARIATION-POINT-PROXY element")

        return autosar.behavior.VariationPointProxy(name=name, category=category, binding_time=binding_time, condition_access=condition_access, parent=parent)
