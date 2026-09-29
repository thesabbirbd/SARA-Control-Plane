# CI/CD Intelligence
SARA evaluates GitHub Actions workflows using the `CIIntelligence` engine. 
Failures are fingerprint-hashed to deduplicate agent assignments and limit repair loops (max 3 cycles by default).
