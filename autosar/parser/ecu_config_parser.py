import sys
import autosar.ecuc
from autosar.base import splitRef
from autosar.parser.parser_base import ElementParser, parseElementUUID

class EcuConfigurationParser(ElementParser):
    """
    Ecu Configuration parser
    """

    def __init__(self,version=3.0):
        super().__init__(version)
        self.switcher = {
            'ECUC-MODULE-CONFIGURATION-VALUES': self.parseEcuConfiguration
        }
        
        self.handledTags = ['SHORT-NAME', 'DEFINITION-REF']

    def getSupportedTags(self):
        return self.switcher.keys()
    
    def getMetaInformation(self, node):
        name = self.parseTextNode(node.find('SHORT-NAME'))
        definition = self.parseTextNode(node.find('DEFINITION-REF'))
        definition = splitRef(definition)[-1] if definition is not None else None

        return (name, definition)

    @parseElementUUID
    def parseElement(self, xmlElement, parent = None):
        parseFunc = self.switcher.get(xmlElement.tag)
        if parseFunc is not None:
            return parseFunc(xmlElement, parent)
        else:
            return None

    @parseElementUUID
    def parseEcuConfiguration(self, xmlRoot, parent=None):
        ecuConfig = None
        if xmlRoot.tag == 'ECUC-MODULE-CONFIGURATION-VALUES':
            name, definition = self.getMetaInformation(xmlRoot)
            ecuConfig = autosar.ecuc.EcuConfig(name, definition, parent)
        else:
            raise NotImplementedError(xmlRoot.tag)

        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag in self.handledTags:
                continue

            if xmlElem.tag == 'CONTAINERS':
                xmlContainers = xmlElem.findall('./ECUC-CONTAINER-VALUE')
                for xmlContainer in xmlContainers:
                    container = self.parseContainer(xmlContainer, ecuConfig)
                    ecuConfig.appendContainer(container)

        return ecuConfig
 
    @parseElementUUID
    def parseContainer(self, xmlElem, parent = None):
        name, definition = self.getMetaInformation(xmlElem)
        container = autosar.ecuc.Container(name, definition, parent)

        for node in xmlElem.findall('./*'):
            if node.tag in self.handledTags:
                continue

            if node.tag == 'SUB-CONTAINERS':
                xmlSubContainers = node.findall('./ECUC-CONTAINER-VALUE')
                for xmlSubContainer in xmlSubContainers:
                    subContainer = self.parseSubContainer(xmlSubContainer, container)

                    container.appendSubContainer(subContainer)

            elif node.tag == 'REFERENCE-VALUES':
                xmlReferenceValues = node.findall('./ECUC-REFERENCE-VALUE')
                for xmlReferenceValue in xmlReferenceValues:
                    refValue = self.parseReferenceValue(xmlReferenceValue)

                    container.appendRef(refValue)

            elif node.tag == 'PARAMETER-VALUES':
                xmlParameterValues = node.findall('./*')
                for xmlParameterValue in xmlParameterValues:
                    paramValue = self.parseParameterValue(xmlParameterValue)

                    container.appendParam(paramValue)

        return container
 
    @parseElementUUID
    def parseSubContainer(self, xmlElem, parent = None):
        name, definition = self.getMetaInformation(xmlElem)
        subContainer = autosar.ecuc.SubContainer(name, definition, parent)

        for node in xmlElem.findall('./*'):
            if node.tag in self.handledTags:
                continue

            if node.tag == 'REFERENCE-VALUES':
                xmlReferenceValues = node.findall('./ECUC-REFERENCE-VALUE')
                for xmlReferenceValue in xmlReferenceValues:
                    refValue = self.parseReferenceValue(xmlReferenceValue)

                    subContainer.appendRef(refValue)

            elif node.tag == 'PARAMETER-VALUES':
                xmlParameterValues = node.findall('./*')
                for xmlParameterValue in xmlParameterValues:
                    paramValue = self.parseParameterValue(xmlParameterValue)
                    subContainer.appendParam(paramValue)

        return subContainer
    
    def parseReferenceValue(self, xmlElem):
        definition_node = xmlElem.find('DEFINITION-REF')
        definition_content = self.parseTextNode(definition_node)
        definition_destination = definition_node.attrib.get('DEST')

        value_node = xmlElem.find('VALUE-REF')
        value_content = self.parseTextNode(value_node)
        value_destination = value_node.attrib.get('DEST')
        
        return autosar.ecuc.ReferenceValue(definition_content, definition_destination, value_content, value_destination)

    def parseParameterValue(self, xmlElem):
        definition_node = xmlElem.find('DEFINITION-REF')
        definition_content = splitRef(self.parseTextNode(definition_node))[-1]
        definition_destination = definition_node.attrib.get('DEST')

        value_node = xmlElem.find('VALUE')
        value_content = self.parseTextNode(value_node)
        value_destination = value_node.attrib.get('DEST')

        if definition_destination == 'ECUC-BOOLEAN-PARAM-DEF':
            value_content = value_content == "true"
        elif definition_destination == 'ECUC-INTEGER-PARAM-DEF':
            value_content = int(value_content)
        elif definition_destination in ['ECUC-ENUMERATION-PARAM-DEF', 'ECUC-TEXTUAL-PARAM-VALUE']:
            value_content = value_content
        else:
            value_content = None
        
        return autosar.ecuc.ParamValue(definition_content, definition_destination, value_content, value_destination)