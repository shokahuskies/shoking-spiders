from comm.message import Message, MsgType

def test_message_fields() -> None:
    m = Message(MsgType.PING, "A0", "A1", 3, {"x": 1})
    assert m.msg_type == MsgType.PING
    assert m.sender == "A0"
    assert m.recipient == "A1"
    assert m.tick == 3
    assert m.payload["x"] == 1
