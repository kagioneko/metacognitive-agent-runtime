from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter


DOMAIN_CODES = {
    "security": "s",
    "data": "d",
    "prediction": "p",
    "neurostate": "n",
}

ACTION_CODES = {
    "xss": "x",
    "summarize": "m",
    "branch": "b",
    "validate": "v",
}

DOMAIN_NAMES = {value: key for key, value in DOMAIN_CODES.items()}
ACTION_NAMES = {value: key for key, value in ACTION_CODES.items()}
BASE36 = "0123456789abcdefghijklmnopqrstuvwxyz"


@dataclass(frozen=True)
class TapeReply:
    child: str
    tape: str
    ok: bool
    result: dict[str, object]
    elapsed_ms: float


@dataclass
class TapeChild:
    name: str
    capabilities: set[str]
    memory: dict[int, str] = field(default_factory=dict)

    def handle(self, tape: str) -> TapeReply:
        started = perf_counter()
        domain, target, action, priority = decode_tape(tape)
        action_key = f"{domain}:{action}"
        if action_key not in self.capabilities:
            result: dict[str, object] = {
                "error": "unsupported_instruction",
                "action": action_key,
                "priority": priority,
            }
            ok = False
        else:
            result = self._execute(domain, action, target, priority)
            ok = True
        return TapeReply(
            child=self.name,
            tape=tape,
            ok=ok,
            result=result,
            elapsed_ms=round((perf_counter() - started) * 1000, 4),
        )

    def _execute(self, domain: str, action: str, target: int, priority: int) -> dict[str, object]:
        target_text = self.memory.get(target, "")
        if domain == "security" and action == "xss":
            vulnerable = "<script>" in target_text.lower()
            return {
                "target": f"#ctx{target}",
                "priority": priority,
                "vulnerable": vulnerable,
                "finding": "script_tag_detected" if vulnerable else "none",
            }
        if domain == "data" and action == "summarize":
            return {
                "target": f"#ctx{target}",
                "priority": priority,
                "summary": target_text[:64],
            }
        return {"target": f"#ctx{target}", "priority": priority, "handled": True}


@dataclass
class TapeBus:
    children: dict[str, TapeChild]

    def dispatch(
        self,
        child_name: str,
        *,
        domain: str,
        action: str,
        target: int,
        priority: int = 5,
    ) -> TapeReply:
        if child_name not in self.children:
            raise KeyError(f"unknown child: {child_name}")
        tape = encode_tape(domain=domain, target=target, action=action, priority=priority)
        return self.children[child_name].handle(tape)


def encode_tape(*, domain: str, target: int, action: str, priority: int) -> str:
    if domain not in DOMAIN_CODES:
        raise ValueError(f"unknown domain: {domain}")
    if action not in ACTION_CODES:
        raise ValueError(f"unknown action: {action}")
    if not 0 <= target < 36:
        raise ValueError("target must be between 0 and 35")
    if not 1 <= priority <= 9:
        raise ValueError("priority must be between 1 and 9")
    return f"{DOMAIN_CODES[domain]}{BASE36[target]}{ACTION_CODES[action]}{priority}"


def decode_tape(tape: str) -> tuple[str, int, str, int]:
    if len(tape) != 4:
        raise ValueError("tape must be exactly 4 characters")
    domain_code, target_code, action_code, priority_code = tape
    if domain_code not in DOMAIN_NAMES:
        raise ValueError(f"unknown domain code: {domain_code}")
    if target_code not in BASE36:
        raise ValueError(f"unknown target code: {target_code}")
    if action_code not in ACTION_NAMES:
        raise ValueError(f"unknown action code: {action_code}")
    if priority_code not in "123456789":
        raise ValueError("priority must be 1-9")
    return (
        DOMAIN_NAMES[domain_code],
        BASE36.index(target_code),
        ACTION_NAMES[action_code],
        int(priority_code),
    )


def default_tape_bus() -> TapeBus:
    return TapeBus(
        children={
            "security": TapeChild(
                name="security-child",
                capabilities={"security:xss"},
                memory={
                    4: 'render("<script>alert(1)</script>")',
                    7: "plain text only",
                },
            ),
            "data": TapeChild(
                name="data-child",
                capabilities={"data:summarize"},
                memory={
                    7: "This is a long context document that should be summarized quickly.",
                },
            ),
        }
    )

