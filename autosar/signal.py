from autosar.base import splitRef
from autosar.element import Element
import sys

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
