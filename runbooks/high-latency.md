# Runbook: High Trace Latency (P99 > 500ms)

## Alert Description

The 99th percentile latency of HTTP requests has exceeded 500ms for more than 2 minutes.

## Impact

Users may experience sluggishness or timeouts in the UI. Service Level Objectives (SLOs) are at risk.

## Investigation Steps

1. **Check Grafana**: Open the [Golden Signals Dashboard](http://grafana/d/sre-golden-signals) and look for latency spikes.
2. **Analyze Traces**: Use Tempo to find traces with high duration. Look for spans with long `fetch_resource` times.
3. **Log Search**: Run the following LogQL in Loki:
   `{app="sre-microservice"} | json | duration > 0.5`
4. **Identify Endpoint**: Check if the spike is localized to `/api/resource`.

## Mitigation

1. **Scale Up**: If saturation is high, increase replicas:
   `kubectl scale deployment sre-microservice --replicas=5`
2. **Disable Failure Injection**: Check if `FAILURE_LATENCY_PROBABILITY` is set in the ConfigMap.

## Verification

- Monitor the P99 latency panel in Grafana to see if it returns below 500ms.

## Escalation Path

- On-call SRE lead or Backend Engineering team.
