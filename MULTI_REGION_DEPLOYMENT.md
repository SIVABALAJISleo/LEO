# Project HYPER Multi-Region Architecture & Disaster Recovery

This document outlines the Enterprise Grade Multi-Region Active-Passive deployment configuration for Project HYPER.
This ensures the platform maintains 99.99% availability even if an entire AWS/Azure region goes completely offline.

## Core Infrastructure

### Region A: Primary (e.g., US-East-1)

- **Ingress:** AWS Route 53 (Latency-based routing with failover)
- **Compute:** EKS (Kubernetes) Cluster A
  - 3x FastAPI Pods (HPA: 3-100)
  - 10x Celery Worker Pods (HPA: 10-500)
- **Cache & Queue:** Redis Enterprise (Primary)
- **Database:** Supabase PostgreSQL (Master) / Hosted Firestore
- **Storage:** Amazon S3 Multi-Region Access Points

### Region B: Failover (e.g., EU-Central-1)

- **Ingress:** Route 53 (Secondary / Passive)
- **Compute:** EKS (Kubernetes) Cluster B
  - 2x FastAPI Pods (Baseline)
  - 2x Celery Worker Pods (Scales instantly upon failover)
- **Cache & Queue:** Redis Enterprise (Replica)
- **Database:** Supabase PostgreSQL (Read Replica -> Promoted to Master during failure)
- **Storage:** Synced via S3 Cross-Region Replication (CRR)

## Failover Sequence (RTO < 60s)

When Cloudflare Health Checks or Route 53 probes detect `api.hyper.com/health` is returning 5xx (or timing out) consistently for 30 seconds from Cluster A:

1. **Traffic Shift:** Route 53 immediately re-routes 100% of global DNS traffic to Region B's Load Balancer.
2. **Database Promotion:** (Manual or Scripted) The PostgreSQL Read Replica in Region B is promoted to Master.
3. **Queue Re-Binding:** Celery Workers in Region B automatically scale up via Kubernetes HPA in response to incoming task pressure.
4. **Resolution:** Region A is flagged via PagerDuty for immediate SRE investigation.

## Persistent Storage Durability

All ML models (`.gguf`, `.pt`) are identically mirrored between OCI containers and S3 CRR buckets. Loss of a data center results in exactly **zero** permanent data loss.
