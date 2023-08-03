import sys

from autosar.element import Element

class EcuConfig(Element):
    def __init__(self, name, definition, parent=None):
        super().__init__(name, parent)

        self.definition = definition

        self.containers = list()

    def appendContainer(self, container):
        self.containers.append(container)

class Container(Element):
    def __init__(self, name, definition, parent=None):
        super().__init__(name, parent)

        self.name = name
        self.definition = definition

        self.subContainers = list()

        # Lists containing ParamValues and ReferenceValues
        self.params = list()
        self.refs = list()

    def appendSubContainer(self, subContainer):
        self.subContainers.append(subContainer)

    def appendParam(self, param):
        self.params.append(param)

    def appendRef(self, ref):
        self.refs.append(ref)

class SubContainer(Element):
    def __init__(self, name, definition, parent=None):
        super().__init__(name, parent)

        self.name = name
        self.definition = definition

        # Lists containing ParamValues and ReferenceValues
        self.params = list()
        self.refs = list()

    def appendParam(self, param):
        self.params.append(param)

    def appendRef(self, ref):
        self.refs.append(ref)

class ParamValue():
    def __init__(self, definition, definition_dest, value, value_dest):
        self.definition = definition
        self.definition_dest = definition_dest
        self.value = value
        self.value_dest = value_dest

class ReferenceValue():
    def __init__(self, definition, definition_dest, value, value_dest):
        self.definition = definition
        self.definition_dest = definition_dest
        self.value = value
        self.value_dest = value_dest