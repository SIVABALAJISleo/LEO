# Incident Response Runbook (SoP)

This playbook defines actions to take when Prometheus alerts trigger on the Project HYPER Platform.

## Alert: HighWorkerCrashRate
**Trigger:** Celery task failure rate > 5/sec.
**Assessment:** AI inference limits or OOM (Out Of Memory) are killing Celery containers.
**Response:**
1. Check Sentry logs for `Segmentation Fault` or `MemoryError`.
2. Stop new job ingest at Gateway level.
3. Update `k8s-deployment.yml` resource limit allocations to `8Gi` memory for `hyper_worker_vision`.
4. Scale out cluster horizontally by `+5`.

## Alert: QueueSaturationDetected
**Trigger:** `rabbitmq_queue_messages_ready > 1000`
**Assessment:** Throughput bottleneck. Workers are processing slower than API ingress.
**Response:**
1. Observe Jaeger to identify if a specific AI model (e.g. YOLO vs JEPA) is causing massive latency bubbles.
2. Artificially lower rate limits temporarily in Redis (`HYPER_USER_QUOTA`).
3. If structural, verify Kubernetes HPA is functioning and has not hit its arbitrary `maxReplicas` limit. 

## Alert: HighFastApiLatency
**Trigger:** P95 API Latency > 2.0s
**Assessment:** Usually indicative of Redis lock contention or database saturation, not worker saturation (as API gateway is entirely async).
**Response:**
1. Verify Redis memory limits are not exhausted causing evictions on `setnx` locks.
2. Investigate Supabase/PostgreSQL active connections.

## Dead Letter Recovery
Tasks terminating due to unrecoverable faults (3x backoff failures) are routed to the DLQ (`celery`). 
To debug dead jobs, inspect via Redis CLI or Flower `Tasks` panel. Do NOT replay blindly without fixing the underlying trace failure.
