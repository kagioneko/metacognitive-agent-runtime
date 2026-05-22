from metacog_runtime import TapeBus, TapeChild, decode_tape, encode_tape


def test_encode_and_decode_tape() -> None:
    tape = encode_tape(domain="security", target=4, action="xss", priority=9)

    assert tape == "s4x9"
    assert decode_tape(tape) == ("security", 4, "xss", 9)


def test_tape_bus_dispatches_to_child() -> None:
    bus = TapeBus(
        children={
            "security": TapeChild(
                name="security-child",
                capabilities={"security:xss"},
                memory={4: "<script>alert(1)</script>"},
            )
        }
    )

    reply = bus.dispatch("security", domain="security", action="xss", target=4, priority=9)

    assert reply.tape == "s4x9"
    assert reply.ok is True
    assert reply.result["vulnerable"] is True
