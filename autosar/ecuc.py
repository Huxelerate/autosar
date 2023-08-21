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
    def __init__(self, name, definition_reference, definition_dest, parent=None):
        super().__init__(name, parent)

        self.name = name
        self.definition_reference = definition_reference
        self.definition_dest = definition_dest

        # List of children containers
        self.containers = list()

        # Lists containing ParamValues and ReferenceValues
        self.params = list()
        self.refs = list()

    def appendContainer(self, container):
        self.containers.append(container)

    def appendParam(self, param):
        self.params.append(param)

    def appendRef(self, ref):
        self.refs.append(ref)

class Value():
    def __init__(self, definition_reference, definition_dest, value, value_dest):
        self.definition_reference = definition_reference
        self.definition_dest = definition_dest
        self.value = value
        self.value_dest = value_dest

class ParamValue(Value):
    pass

class ReferenceValue(Value):
    pass