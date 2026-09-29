from enum import Enum
import re

class RiskLevel(Enum):
    SAFE = "SAFE"
    MODIFY = "MODIFY"
    DANGEROUS = "DANGEROUS"

DANGEROUS_PATTERNS = [
    r"git\s+push\s+--force",
    r"git\s+reset\s+--hard",
    r"git\s+clean\s+-fd",
    r"rm\s+-rf\s+/",
    r"mkfs",
    r"dd\s+if=",
    r"sudo\s+",
    r"chown\s+-R",
    r"chmod\s+-R\s+777",
    r"drop\s+database",
    r"truncate\s+table"
]

SAFE_PATTERNS = [
    r"^git\s+status",
    r"^git\s+log",
    r"^git\s+show",
    r"^ls\s+",
    r"^cat\s+",
    r"^pytest",
    r"^npm\s+test",
    r"^echo\s+"
]

def classify_command(instruction: str) -> RiskLevel:
    instr_lower = instruction.lower().strip()
    
    # Check dangerous
    for pat in DANGEROUS_PATTERNS:
        if re.search(pat, instr_lower):
            return RiskLevel.DANGEROUS
            
    # Check safe
    for pat in SAFE_PATTERNS:
        if re.match(pat, instr_lower):
            return RiskLevel.SAFE
            
    # Default to MODIFY if not explicitly safe
    return RiskLevel.MODIFY
