import { describe, it, expect } from "vitest";
import { IntentReconstructionEngine } from "./intentReconstructionEngine";
import { DeepReasoningEngine } from "./deepReasoningEngine";
import { ToolVerificationEngine } from "./toolVerificationEngine";
import { SelfCritiqueEngine } from "./selfCritiqueEngine";
import { EvaluationCenter } from "../evaluation/evaluationCenter";
import { RealityFeedbackEngine } from "./realityFeedbackEngine";
import { KnowledgeGovernor } from "./knowledgeGovernor";
import { MemoryGovernor } from "./memoryGovernor";
import { DebateEngine } from "./debateEngine";

describe("V14 Cognitive Engines", () => {
  it("Intent Reconstruction Engine reconstructions are accurate", () => {
    const recon = new IntentReconstructionEngine();
    
    // Test Tamil-English & slang recovery
    const res = recon.reconstruct("bro startup fail wat do");
    expect(res.isSlang).toBe(true);
    expect(res.reconstructed).toContain("SaaS startup failure");
    expect(res.confidence).toBe(0.95);
    
    const res2 = recon.reconstruct("eppadi train ai");
    expect(res2.isTamilEnglish).toBe(true);
    expect(res2.reconstructed).toContain("train a local artificial intelligence model");
  });

  it("Deep Reasoning Engine execution pathways work correctly", () => {
    const engine = new DeepReasoningEngine();
    const deductive = engine.reason("train ai", "Deductive");
    expect(deductive.reasoningType).toBe("Deductive");
    expect(deductive.steps.length).toBeGreaterThan(0);
    expect(deductive.conclusion).toContain("mathematically validated");

    const counterfactual = engine.reason("verify failure", "Counterfactual");
    expect(counterfactual.reasoningType).toBe("Counterfactual");
    expect(counterfactual.conclusion).toContain("Counterfactual Outlook");
  });

  it("Tool Verification Engine validates math and runs checkpoints", () => {
    const verify = new ToolVerificationEngine();
    
    // Arithmetic match
    const res = verify.verifyOutput("What is 10 + 20?", "The output is 30.");
    expect(res.isVerified).toBe(true);
    expect(res.score).toBe(1.0);
    
    // Arithmetic mismatch repair
    const res2 = verify.verifyOutput("What is 10 + 20?", "The output is 99.");
    expect(res2.isVerified).toBe(false);
    expect(res2.repairedContent).toContain("[Corrected Calculation: 30]");
  });

  it("Self Critique Engine handles contradictions and alerts on risk", () => {
    const critique = new SelfCritiqueEngine();
    
    // Yes and no contradiction
    const res = critique.critique("Check parameters", "Yes, this works, but no, it actually fails.");
    expect(res.hallucinationDetected).toBe(true);
    expect(res.contradictions.length).toBeGreaterThan(0);
    expect(res.refinedAnswer).toContain("Self-Critique Resolution");

    // Dynamic pricing risk
    const res2 = critique.critique("billing model", "Active production setup");
    expect(res2.risks.length).toBeGreaterThan(0);
  });

  it("Evaluation Center runs simulated release benchmarks", () => {
    const center = new EvaluationCenter();
    const report = center.runFullEvaluation();
    expect(report.overallAccuracy).toBeGreaterThanOrEqual(0.95);
    expect(report.passedVerification).toBe(true);
    expect(report.metrics.length).toBe(10);
  });

  it("Reality Feedback Engine tracks metrics and adjusts weights", () => {
    const feedback = new RealityFeedbackEngine();
    
    const entry = feedback.logFeedback("pred-101", "intentAccuracyWeight", 100, 110);
    expect(entry.predictionId).toBe("pred-101");
    expect(entry.errorPct).toBe(10);
    expect(feedback.getHistory().length).toBe(1);
    expect(feedback.getWeights().intentAccuracyWeight).toBeLessThan(0.95); // Adjusts downwards
  });

  it("Knowledge Governor decays/reinforces crystal assets", () => {
    const gov = new KnowledgeGovernor();
    
    const assets = gov.auditAssets();
    expect(assets.find(a => a.id === "V14-K01")?.status).toBe("strengthened");
    expect(assets.find(a => a.id === "V14-K03")?.status).toBe("decayed");
    
    const newAsset = gov.addCrystal("Custom test topic", 0.99, 0.98);
    expect(newAsset.id).toBe("V14-K04");
  });

  it("Memory Governor purges duplicates and resolves contradictions", () => {
    const gov = new MemoryGovernor();
    
    // Initial state contains 3 memories, 1 is a duplicate of M14-001, and M14-002 contradicts M14-001
    const memories = gov.auditMemory();
    
    // M14-003 duplicate of M14-001 is purged, and contradiction keeps the higher decay weight
    expect(memories.length).toBe(1);
    expect(memories[0].id).toBe("M14-003"); // replaced or updated
  });

  it("Debate Engine orchestrates 5-agent debate round-robin cycles", () => {
    const debate = new DebateEngine();
    
    const session = debate.coordinateDebate("startup failure");
    expect(session.rounds.length).toBe(2);
    expect(session.consensus).toContain("Consensus Resolution");
  });
});
