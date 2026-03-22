# Runbook: High Error Rate (> 5%)

## Alert Description

The ratio of 5xx errors to total requests has exceeded 5% for more than 1 minute.

## Impact

Direct impact on user experience. API requests are failing.

## Investigation Steps

1. **Check Status Codes**: Look at the "Error Rate" panel in Grafana.
2. **Inspect Logs**: Check Loki for error logs:
   `{app="sre-microservice"} | json | level="error"`
3. **Identify Cause**: Look for "Injected failure" logs or upstream timeout errors.

## Mitigation

1. **Rollback**: If a recent deployment occurred, rollback:
   `kubectl rollout undo deployment sre-microservice`
2. **Check Config**: Ensure `FAILURE_ERROR_PROBABILITY` is "0.0".

## Verification

- Verify error rate drops to ~0% in Grafana.

## Escalation Path

- On-call SRE lead.
