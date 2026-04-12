from comm.mailbox import Mailbox
from comm.message import Message, MsgType

def test_mailbox_push_pop() -> None:
    mb = Mailbox()
    assert len(mb) == 0
    mb.push(Message(MsgType.HELLO, "A0", "A1", 0, None))
    assert len(mb) == 1
    m = mb.pop()
    assert m is not None
    assert m.msg_type == MsgType.HELLO
    assert len(mb) == 0
