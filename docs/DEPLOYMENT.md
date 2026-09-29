# Deployment & Health Checks
`DeploymentEngine` mandates explicit gating. Upon deployment, `verify_health` dictates whether the state proceeds to `DEPLOYED` or reverses to `ROLLBACK`.
