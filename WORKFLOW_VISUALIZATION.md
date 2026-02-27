# Project Workflow Visualization

To help you understand exactly how **HYPER** works (both for developers and users), here are the visual workflows.

## 1. Developer Workflow (How to work on the project)
This is the cycle you follow to make changes, test them, and publish.

```mermaid
graph TD
    A[Start: You write code] -->|Save File| B[Dev Server Updates]
    B -->|Hot Reload| C[Browser Refreshes Instantly]
    
    A -->|Run Check| D{Quality Gates}
    D -->|npm test| E[Vitest: Runs Smoke Tests]
    D -->|tsc| F[TypeScript: Checks Strict Types]
    
    E -->|Pass| G[Ready to Build]
    F -->|Pass| G
    
    G -->|npm run build| H[Production Build]
    H -->|Creates| I[./dist folder]
    I -->|Deploy| J[Netlify / Vercel / Docker]
```

## 2. CI/CD Pipeline (GitHub Actions)
This happens automatically whenever you upload code to GitHub.

```mermaid
graph LR
    Push[Code Push to Main] -->|Trigger| CI[GitHub Action]
    
    subgraph "CI Pipeline"
    CI --> Lint[Lint Check]
    CI --> Type[Type Check]
    Lint --> Test[Unit Tests]
    Type --> Test
    Test --> Build[Build App]
    end
    
    Build -->|Success| Artifact[Save Build Artifact]
    Build -->|Fail| Alert[Notify Developer]
```

## 3. Application Logic (The "Honest" Engine)
How the app decides whether to use Real Hardware or the Simulation we built.

```mermaid
graph TD
    User[User Logs In] --> Dashboard[Load Dashboard]
    Dashboard --> Init[Backend Initialization]
    
    Init -->|Check| Agent{Is Local Agent Connected?}
    
    Agent -->|Yes| Real[Mode: REAL HARDWARE]
    Real -->|Stream| GPU[Read NVIDIA GPU Metrics]
    
    Agent -->|No| Sim[Mode: SIMULATION]
    Sim -->|Generate| Mock[Virtual H100 GPU]
    Mock -->|Emulate| Data[Simulated Temp/Load/Power]
    
    GPU --> UI[Update Dashboard UI]
    Data --> UI
    
    style Real fill:#9f9,stroke:#333,stroke-width:2px
    style Sim fill:#f9f,stroke:#333,stroke-width:2px
```

---
*Created for HYPER Documentation*
