

from vortex.Tuple import addTupleType, Tuple, TupleField


@addTupleType
class PeekAdmNavbarUserTuple(Tuple):
    __tupleType__ = 'peek_server.PeekAdmNavbarUserTuple'

    username = TupleField('nouser')