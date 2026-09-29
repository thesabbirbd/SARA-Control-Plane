class CodeRabbitIntegration:
    """CodeRabbit review ingestion and policy filtering."""
    @staticmethod
    def filter_finding(finding: dict) -> dict:
        # Translate CodeRabbit AI output into standard SARA findings
        severity = finding.get("severity", "MINOR")
        if severity == "CRITICAL":
            return {"action": "BLOCK_MERGE"}
        return {"action": "COMMENT_ONLY"}
