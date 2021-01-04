from vortex.Tuple import addTupleType, Tuple, TupleField


@addTupleType
class PeekAdmNavbarUserTuple(Tuple):
    __tupleType__ = "peek_logic_service.PeekAdmNavbarUserTuple"

    username = TupleField("nouser")
