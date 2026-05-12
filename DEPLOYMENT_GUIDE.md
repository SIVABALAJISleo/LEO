# Enterprise Deployment Guide

This manual covers the strict operational deployment of the HYPER SaaS platform into a production Kubernetes cluster (EKS/AKS/GKE).

## 1. Secrets Generation
Never deploy `.env` files to Git. Push your secrets directly to the Kubernetes namespace:
```bash
kubectl create secret generic hyper-secrets \
  --from-literal=STRIPE_SECRET_KEY=sk_live_... \
  --from-literal=STRIPE_WEBHOOK_SECRET=whsec_... \
  --from-literal=PAYPAL_CLIENT_SECRET=... \
  --from-literal=SENTRY_DSN=https://...
```

## 2. Cluster Deployment
Deploy the primary Redis, API Gateway, and Auto-Scaling Workers:
```bash
kubectl apply -f k8s-deployment.yml
```

## 3. Node Affinity & Taints
Project HYPER is heavily CPU-bound. Ensure your EKS/GKE nodes are tagged appropriately. The `Celery` worker pods should be scheduled purely on high-frequency CPU nodes (e.g. AWS `c6i.4xlarge` equivalents). The API Gateway pods can reside on standard general-purpose nodes (`m5.large`).

## 4. Tracing Ingestion
For active Jaeger telemetry, ensure the backend `.env` mappings export the Collector IP:
```env
OTEL_EXPORTER_OTLP_ENDPOINT=http://<jaeger-collector-svc>:4318/v1/traces
```

## 5. Scaling Strategy
The `HorizontalPodAutoscaler` is designed to trigger new pods at **70% CPU Utilization**.

If the `celery_task_failed_total` Prometheus metric spikes alongside pod creation, it indicates you are triggering OOM (Out-of-Memory) kills. In this scenario, increase your pod memory limit via `k8s-deployment.yml` `resources.limits.memory`.
