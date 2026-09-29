class SonarIntegration:
    """SonarQube Cloud quality gate and findings."""
    @staticmethod
    def evaluate_gate(gate_status: str) -> str:
        if gate_status == "OK":
            return "PASSED"
        if gate_status == "ERROR":
            return "FAILED"
        return "UNKNOWN"
