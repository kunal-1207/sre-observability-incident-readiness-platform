# Runbook: Memory Leak Detected

## Alert Description

Resident memory (RSS) has exceeded 400MB for more than 5 minutes.

## Impact

Potential Out-Of-Memory (OOM) kills, leading to pod restarts and transient errors.

## Investigation Steps

1. **Monitor Memory**: Check the "Memory Usage" panel in Grafana.
2. **Check App Logs**: Look for "simulating_memory_leak" warnings in Loki.

## Mitigation

1. **Restart Pods**: Recycle pods to clear leaked memory:
   `kubectl rollout restart deployment sre-microservice`
2. **Stop Leak Trigger**: Identify if the `/simulate/memory-leak` endpoint was called maliciously or accidentally.

## Verification

- Memory usage should drop back to baseline (~100-150MB).

## Escalation Path

- Backend Engineering team (Root cause analysis required).
