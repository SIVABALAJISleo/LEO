# Project HYPER - Distributed SaaS Architecture Guide

## Overview

Project HYPER has been successfully upgraded from a single-node API monolith into a **horizontally scalable distributed system**. This document outlines the Enterprise capabilities unlocked by this migration.

## Architectural Layers

### 1. The Gateway (`Hyper API`)

The main FastAPI web server handles user connections, JWT verification, and Stripe billing limits.

- Fast response times.
- Contains no blocking AI execution.
- Checks Redis `limit_and_quota_check` middleware for API abuse before dispatching to workers.

### 2. Message Broker (`Redis`)

Redis acts as the central nervous system connecting the Web Gateway to the background inference clusters.

- **Queues**: Celery uses Redis lists under the hood to manage pending inference requests.
- **Rate Limits**: Holds Token Bucket counters dropping aggressive IPs (HTTP 429).
- **Quotas**: Tracks daily limits enforced by Stripe Subscriptions.

### 3. Celery Workers (`Compute Node Clusters`)

The monolithic CPU engines have been extracted into independent, stateless workers.

- **llm_worker** (`backend.tasks.llm_tasks`): Responsible for LLAMA.cpp generation.
- **vision_worker** (`backend.tasks.vision_tasks`): Responsible for YOLO Object Detection.
- Models load lazily _per worker process_, eliminating API memory bloat.

**Kubernetes Auto-Scaling (HPA)**
Workers scale horizontally via `k8s/hpa.yaml`:

- **LLM Nodes:** Scale from 2 to 10 pods when CPU utilization exceeds 75%.
- **Vision Nodes:** Scale from 3 to 15 pods when CPU utilization exceeds 70%.
- This guarantees system stability during volatile request spikes without over-provisioning base hardware.

### 4. S3 Object Storage

- Due to the size of inference payloads (Base64 images, long logs), Redis would OOM under heavy load.
- Output from workers is streamed directly into an S3-compatible bucket (`hyper-saas-bucket`).
- FastAPI returns presigned URLs to the frontend React Dashboard.

## Observability

- `/api/v1/system/health`: Summarizes Redis, Celery Workers, and Host Telemetry for uptime monitoring.
- `/api/v1/system/metrics`: Exposes realtime Prometheus gauges (e.g. `hyper_active_celery_workers`) to link into Grafana.
- **Celery Flower**: A live UI dashboard on `:5555` tracking queue backlogs, worker states, and task throughput.

## Disaster Recovery & Redundancy

- **Data Persistence**: Redis AOF (Append-Only File) is enabled to survive broker crashes and resume queued tasks.
- **Stateless Workers**: If a worker node goes down unexpectedly, its `Deployment` restarts it. Jobs orphaned mid-execution are redelivered (Ack late protocol) by Celery.
- **Storage Replication**: Output artifacts (JSON schemas, Object detections) uploaded to S3 use native cloud bucket replication spanning availability zones.

## Production Deployment Checklist

- Define `.env` fully (STRIPE secrets, S3 buckets, REDIS URL).
- Deploy using the provided `docker-compose.yml` for single-host scaling, or use the manifests inside `/k8s/` for full distributed clustering.
