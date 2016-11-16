'''
Created on 09/07/2014

@author: synerty
'''

from rapui.vortex.Tuple import addTupleType, Tuple, TupleField


@addTupleType
class PeekAdmNavbarTuple(Tuple):
    __tupleType__ = 'admin.navbar'

    supportExceeded = TupleField(False)
    demoExceeded = TupleField(False)
    countsExceeded = TupleField(False)
    username = TupleField('nouser')