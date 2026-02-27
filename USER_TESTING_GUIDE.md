# Project HYPER: User Manual & Testing Guide

Welcome to Project HYPER! This guide will help you run the project and test each core feature one-by-one.

## 🚀 Part 1: Running the Project

To run Project HYPER, you need to start both the **Backend (Python)** and the **Frontend (React)**.

### 1. Start the Backend
1. Open a new terminal in the project root.
2. If you have a virtual environment:
   - Windows: `.\venv\Scripts\activate`
3. Install dependencies:
   - `pip install -r requirements.txt`
4. Run the server:
   - `python -m backend.main`
   - *Note: The server will start on `http://localhost:8005`. (Always use 'localhost' instead of '0.0.0.0' in your browser).*

### 2. Start the Frontend
1. Open **another** terminal window.
2. Install dependencies:
   - `npm install`
3. Run the development server:
   - `npm run dev`
4. Open the link displayed in the terminal (usually `http://localhost:5173`).

---

## 🧪 Part 2: Manual Testing Steps

Follow these steps in order to see all the features in action.

### 1. Core Orchestration (Unified Engine)
- **Where**: Main Dashboard / Orchestration Explorer.
- **Goal**: Test how the "Core Engine" routes complex queries.
- **Steps**:
  1. Click on **"Orchestration Explorer"** in the sidebar.
  2. Select the **"Unified"** tab.
  3. Enter a query like: `"Render a photorealistic car in the rain."`
  4. Observe the **"System Telemetry"** panel on the right. You should see "SDGP BYPASS ACTIVE" and "Ray-Logic" depth updating.
  5. Verify that the result mentions "World Model" and "Symbolic logic".

### 2. GPU Bypass Demo (Pillars of Acceleration)
- **Where**: GPU Bypass Demo page.
- **Goal**: Verify visual evidence of GPU-irrelevant rendering.
- **Steps**:
  1. Navigate to the **"GPU Bypass Demo"** page.
  2. **Pillar 1 (Subtask Router)**: Type `"Optimize my code"` and click **Decompose**. See it break down into atomic tasks.
  3. **Pillar 4 (Ray-Logic Engine)**: Click **"Trigger Engine"**. Observe the "Synthesizing..." progress bar and the Zap icon glowing. This simulates a heavy render bypass.
  4. **Pillar 7 (Optimistic UI)**: Type anything in the "Edit system state" box. Notice how the status bar fills instantly (Pillar 7's latency masking).

### 3. Production Hardening Audit
- **Where**: Production Audit Dashboard.
- **Goal**: Confirm the system is 100% mission-ready.
- **Steps**:
  1. Go to the **"Production Audit"** section.
  2. Observe the **"Readiness Score"**. It should be **100/100**.
  3. Check the **"Backup Health"** and **"Release Safety"** cards. They should say "HEALTHY" and "SECURE" because of the hardening we applied.

### 4. Search & RAG (Retrieval-Augmented Generation)
- **Where**: Orchestration Explorer -> RAG Tab.
- **Goal**: Test document retrieval on CPU.
- **Steps**:
  1. Go to **Orchestration Explorer** and click the **"RAG"** tab.
  2. Search for something related to the system, like `"How does SDGP work?"`.
  3. Observe the retrieved nodes and the confidence score.

### 5. Documentation & Branding Check
- **Where**: Documentation page.
- **Goal**: Ensure no trace of the old "Breakthrough" keyword remains.
- **Steps**:
  1. Click **"Documentation"**.
  2. Browse through the **Architecture** section.
  3. Verify that the layer is named **"Core Acceleration"** and not "Breakthrough".

---

## 🛠️ Troubleshooting
- **Backend Error**: Ensure no other process is using port 8005.
- **Vite Error**: If the frontend won't connect, ensure `VITE_BACKEND_URL` in `.env` is set to `http://localhost:8005`.
- **Missing Icons**: Ensure you have a stable internet connection for Lucide icons to load (or they will use local fallbacks).
