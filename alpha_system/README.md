# Project Alpha: Compute-Avoidance Intelligence System

A production-ready intelligence orchestrator that prioritizes retrieval, prediction, and reasoning over heavy computation.

## 🏗️ Architecture

The system uses a **Capability Router** to detect user intent and route queries to one of four specialized engines:

1.  **Module 1: RAG Intelligence**: Answers questions using vector retrieval (FAISS) instead of parametric generation.
2.  **Module 2: Hypothesis Narrowing**: Reduces experimental search space via Bayesian elimination.
3.  **Module 3: Decision Prep**: Builds reasoning trees and risk assessments for human approval.
4.  **Module 4: Perceptual Optimizer**: Simulates perception via temporal reuse and state prediction.

## 🚀 Setup Instructions

### Backend (FastAPI)
1. `cd alpha_system/backend`
2. `pip install -r requirements.txt`
3. `uvicorn app.main:app --reload`

### Frontend (React)
1. `cd alpha_system/frontend`
2. `npm install`
3. `npm run dev`

## 📊 Core Rules
- **Prefer Reuse over Recompute**
- **Prefer Prediction over Calculation**
- **Prefer Elimination over Search**
- **Prefer Explanation over Authority**
- **Prefer Perception over Simulation**

## 📂 Project Structure
```text
alpha_system/
├── backend/
│   ├── app/
│   │   ├── core/           # Orchestrator & Config
│   │   ├── modules/        # Intelligence Modules (1-4)
│   │   └── services/       # Vector DB & Storage
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.tsx         # Main UI & Dashboard
    │   └── main.tsx
    └── package.json
```
