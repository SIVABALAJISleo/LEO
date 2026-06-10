import { runReasoningHunter } from '../hunters/reasoningHunter';
import { runLanguageHunter } from '../hunters/languageHunter';
import { runHallucinationHunter } from '../hunters/hallucinationHunter';
import { runMemoryHunter } from '../hunters/memoryHunter';
import { runAgentHunter } from '../hunters/agentHunter';
import { runRagHunter } from '../hunters/ragHunter';
import { runSecurityHunter } from '../hunters/securityHunter';
import { runEnterpriseHunter } from '../hunters/enterpriseHunter';
import { runLoadHunter } from '../hunters/loadHunter';
import { runNvidiaRelevanceAudit } from '../hunters/nvidiaRelevanceAudit';
import { runRealityGapAudit } from '../hunters/realityGapAudit';

export interface CalculatedScores {
    architectureScore: number;
    infrastructureScore: number;
    reasoningScore: number;
    languageScore: number;
    memoryScore: number;
    ragScore: number;
    agentScore: number;
    securityScore: number;
    enterpriseScore: number;
    realityScore: number;
    verificationScore: number;
    overallProductScore: number;
}

export const calculateBalanceGap = async (): Promise<CalculatedScores> => {
    // Run all hunters in parallel
    const [
        reasoning,
        language,
        hallucination,
        memory,
        agent,
        rag,
        security,
        enterprise,
        load,
        nvidia,
        reality
    ] = await Promise.all([
        runReasoningHunter(),
        runLanguageHunter(),
        runHallucinationHunter(),
        runMemoryHunter(),
        runAgentHunter(),
        runRagHunter(),
        runSecurityHunter(),
        runEnterpriseHunter(),
        runLoadHunter(),
        runNvidiaRelevanceAudit(),
        runRealityGapAudit()
    ]);

    const reasoningScore = Math.max(0, 100 - (reasoning.failureRate * 100));
    const languageScore = Math.max(0, 100 - ((1 - language.intentAccuracy) * 100));
    const memoryScore = Math.max(0, 100 - (memory.memoryDrift * 100));
    const ragScore = Math.max(0, 100 - (rag.wrongRetrieval * 100 + rag.missedRetrieval * 100));
    const agentScore = Math.max(0, 100 - (agent.routingFailures * 100 + agent.deadlocks * 100));
    const securityScore = Math.max(0, 100 - ((1 - security.detectionRate) * 100));
    const enterpriseScore = Math.max(0, 100 - (enterprise.slaViolations * 100));
    const realityScore = Math.max(0, 100 - (reality.unknownUnknowns * 100 + reality.verificationGaps * 100));
    const verificationScore = Math.max(0, 100 - (hallucination.falseConfidence * 100));

    // Base infrastructure factors in load crashes and SLA violations
    const infrastructureScore = Math.max(0, 100 - (load.crashes * 1000 + enterprise.latencyP99 / 100));
    
    // Architecture factors in Nvidia relevance and agent complexity failures
    const avgNvidiaPerformance = nvidia.comparisons[2].enterpriseAi * 100; // Using NVIDIA N1X baseline
    const architectureScore = (avgNvidiaPerformance + agentScore) / 2;

    const overallProductScore = (
        architectureScore + infrastructureScore + reasoningScore + languageScore + 
        memoryScore + ragScore + agentScore + securityScore + enterpriseScore + 
        realityScore + verificationScore
    ) / 11;

    return {
        architectureScore: parseFloat(architectureScore.toFixed(2)),
        infrastructureScore: parseFloat(infrastructureScore.toFixed(2)),
        reasoningScore: parseFloat(reasoningScore.toFixed(2)),
        languageScore: parseFloat(languageScore.toFixed(2)),
        memoryScore: parseFloat(memoryScore.toFixed(2)),
        ragScore: parseFloat(ragScore.toFixed(2)),
        agentScore: parseFloat(agentScore.toFixed(2)),
        securityScore: parseFloat(securityScore.toFixed(2)),
        enterpriseScore: parseFloat(enterpriseScore.toFixed(2)),
        realityScore: parseFloat(realityScore.toFixed(2)),
        verificationScore: parseFloat(verificationScore.toFixed(2)),
        overallProductScore: parseFloat(overallProductScore.toFixed(2))
    };
};
