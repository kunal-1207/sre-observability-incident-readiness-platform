# Postmortem: 2026-02-12 - Latency Spike in /api/resource

## Incident Summary

Between 10:00 and 10:15 UTC, the `sre-microservice` experienced a sudden increase in P99 latency on the `/api/resource` endpoint, peaking at 3.2s.

## Timeline (UTC)

- **10:00**: HighLatency alert fired in Prometheus.
- **10:02**: On-call engineer received notification and acknowledged.
- **10:05**: Investigation via Grafana showed latency spike localized to `sre-microservice`.
- **10:07**: Tempo traces revealed `fetch_resource` spans taking 3s+.
- **10:10**: Loki logs showed `injecting_latency` logs, confirming failure injection was active.
- **10:12**: ConfigMap updated to set `FAILURE_LATENCY_PROBABILITY` to "0.0".
- **10:15**: Latency returned to baseline levels (100ms). Alert resolved.

## Root Cause

The `FAILURE_LATENCY_PROBABILITY` environment variable was accidentally set to "0.5" during a manual config update, causing 50% of requests to sleep for 1-3 seconds.

## Contributing Factors

- Manual updates to ConfigMaps are error-prone.
- Lack of validation on failure injection parameters.

## What Went Well

- Monitoring stack detected the latency spike within 30 seconds.
- Runbook provided clear steps to identify and mitigate failure injection issues.
- Tracing allowed for immediate localization of the bottleneck.

## What Went Wrong

- Failure injection was enabled in a production-style environment without a clear expiration or safety check.

## Action Items

- [ ] Implement validation in `app/main.py` for failure probabilities.
- [ ] Move failure injection controls to a secure, audited feature flag system.
- [ ] Add a "Chaos Mode" banner to the API responses when injection is active.
