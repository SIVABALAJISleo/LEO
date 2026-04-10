/**
 * ═══════════════════════════════════════════════════════════════
 *  DOMAIN REGISTRY — Policies #5 (Blast Radius) & #10 (Recovery)
 * ═══════════════════════════════════════════════════════════════
 *  Manages domain definitions, health state, probation, and
 *  blast-radius isolation. Failures in one domain never affect others.
 * ═══════════════════════════════════════════════════════════════
 */

import {
    DomainDefinition,
    DomainState,
    DomainStatus,
    AuthorityLevel,
    ProbationRecord,
    DistributionSnapshot,
} from './types';

export class DomainRegistry {
    private static instance: DomainRegistry;
    private domains = new Map<string, DomainState>();

    // Probation configuration
    private readonly PROBATION_VERIFICATIONS_REQUIRED = 10;
    private readonly PROBATION_SUCCESS_RATE_REQUIRED = 0.9;
    private readonly PROBATION_THRESHOLD_MULTIPLIER = 1.5; // 50% stricter
    private readonly CONSECUTIVE_FAILURES_TO_DISABLE = 5;

    private constructor() {
        this.registerDefaultDomains();
    }

    static getInstance(): DomainRegistry {
        if (!DomainRegistry.instance) {
            DomainRegistry.instance = new DomainRegistry();
        }
        return DomainRegistry.instance;
    }

    /** Register a new domain */
    registerDomain(definition: DomainDefinition): void {
        if (this.domains.has(definition.name)) return;

        this.domains.set(definition.name, {
            definition,
            status: DomainStatus.ACTIVE,
            reliabilityScore: 1.0,
            totalDecisions: 0,
            successfulDecisions: 0,
            failedDecisions: 0,
            consecutiveFailures: 0,
            lastActivityTimestamp: Date.now(),
            probationStartTimestamp: null,
            probationVerifications: 0,
            inputDistribution: this.emptyDistribution(),
        });
    }

    /** Get domain state — null if unknown domain */
    getDomain(name: string): DomainState | null {
        return this.domains.get(name) || null;
    }

    /** Check if domain is operational (ACTIVE or DEGRADED or PROBATION) */
    isOperational(name: string): boolean {
        const d = this.domains.get(name);
        return d !== undefined && d.status !== DomainStatus.DISABLED;
    }

    /** Get effective confidence threshold (higher during probation) */
    getEffectiveConfidenceThreshold(name: string): number {
        const d = this.domains.get(name);
        if (!d) return 1.0; // Unknown domain = max threshold (will refuse)

        const base = d.definition.confidenceThreshold;
        if (d.status === DomainStatus.PROBATION) {
            return Math.min(1.0, base * this.PROBATION_THRESHOLD_MULTIPLIER);
        }
        if (d.status === DomainStatus.DEGRADED) {
            return Math.min(1.0, base * 1.2);
        }
        return base;
    }

    /** Get max authority level allowed for this domain */
    getMaxAuthority(name: string): AuthorityLevel {
        const d = this.domains.get(name);
        if (!d) return AuthorityLevel.ADVISORY;
        if (d.status === DomainStatus.PROBATION) return AuthorityLevel.ADVISORY;
        if (d.status === DomainStatus.DEGRADED) return AuthorityLevel.ASSISTED;
        return d.definition.maxAuthorityLevel;
    }

    /** Is caching allowed for this domain? */
    isCachingAllowed(name: string): boolean {
        const d = this.domains.get(name);
        if (!d) return false;
        // Policy #10: no caching during probation
        if (d.status === DomainStatus.PROBATION) return false;
        return d.definition.allowCaching;
    }

    // ──────────────────── Reliability Updates ────────────────────

    /** Record a successful decision */
    recordSuccess(name: string): void {
        const d = this.domains.get(name);
        if (!d) return;

        d.totalDecisions++;
        d.successfulDecisions++;
        d.consecutiveFailures = 0;
        d.lastActivityTimestamp = Date.now();
        d.reliabilityScore = d.successfulDecisions / d.totalDecisions;

        if (d.status === DomainStatus.PROBATION) {
            d.probationVerifications++;
            this.evaluateProbation(d);
        } else if (d.status === DomainStatus.DEGRADED) {
            this.evaluateRecovery(d);
        }
    }

    /** Record a failed decision */
    recordFailure(name: string): void {
        const d = this.domains.get(name);
        if (!d) return;

        d.totalDecisions++;
        d.failedDecisions++;
        d.consecutiveFailures++;
        d.lastActivityTimestamp = Date.now();
        d.reliabilityScore = d.successfulDecisions / d.totalDecisions;

        // Check if we need to degrade or disable
        if (d.consecutiveFailures >= this.CONSECUTIVE_FAILURES_TO_DISABLE) {
            this.transitionTo(d, DomainStatus.DISABLED);
        } else if (d.reliabilityScore < d.definition.reliabilityFloor) {
            this.transitionTo(d, DomainStatus.DISABLED);
        } else if (d.reliabilityScore < d.definition.reliabilityFloor + 0.1) {
            this.transitionTo(d, DomainStatus.DEGRADED);
        }
    }

    /** Manually enter probation for a disabled domain */
    enterProbation(name: string): boolean {
        const d = this.domains.get(name);
        if (!d || d.status !== DomainStatus.DISABLED) return false;

        d.status = DomainStatus.PROBATION;
        d.probationStartTimestamp = Date.now();
        d.probationVerifications = 0;
        d.consecutiveFailures = 0;
        return true;
    }

    /** Get probation record if domain is in probation */
    getProbationRecord(name: string): ProbationRecord | null {
        const d = this.domains.get(name);
        if (!d || d.status !== DomainStatus.PROBATION) return null;

        const successRate = d.probationVerifications > 0
            ? d.successfulDecisions / Math.max(1, d.probationVerifications)
            : 0;

        return {
            domain: name,
            enteredAt: d.probationStartTimestamp!,
            requiredVerifications: this.PROBATION_VERIFICATIONS_REQUIRED,
            completedVerifications: d.probationVerifications,
            successfulVerifications: Math.round(successRate * d.probationVerifications),
            strictThresholdMultiplier: this.PROBATION_THRESHOLD_MULTIPLIER,
        };
    }

    /** Get all domain states */
    getAllDomains(): DomainState[] {
        return Array.from(this.domains.values());
    }

    /** Get health report across all domains */
    getHealthReport(): Record<string, { status: DomainStatus; reliability: number }> {
        const report: Record<string, { status: DomainStatus; reliability: number }> = {};
        this.domains.forEach((d, name) => {
            report[name] = { status: d.status, reliability: d.reliabilityScore };
        });
        return report;
    }

    // ──────────────────── Private Helpers ────────────────────

    private transitionTo(d: DomainState, newStatus: DomainStatus): void {
        if (d.status === newStatus) return;
        const oldStatus = d.status;
        d.status = newStatus;

        if (newStatus === DomainStatus.PROBATION) {
            d.probationStartTimestamp = Date.now();
            d.probationVerifications = 0;
        }

        console.warn(
            `[DomainRegistry] ${d.definition.name}: ${oldStatus} → ${newStatus} ` +
            `(reliability=${d.reliabilityScore.toFixed(3)}, consecutive_failures=${d.consecutiveFailures})`
        );
    }

    private evaluateProbation(d: DomainState): void {
        if (d.probationVerifications >= this.PROBATION_VERIFICATIONS_REQUIRED) {
            const recentReliability = d.reliabilityScore;
            if (recentReliability >= this.PROBATION_SUCCESS_RATE_REQUIRED) {
                this.transitionTo(d, DomainStatus.ACTIVE);
                d.probationStartTimestamp = null;
            } else {
                // Probation failed — disable again
                this.transitionTo(d, DomainStatus.DISABLED);
            }
        }
    }

    private evaluateRecovery(d: DomainState): void {
        if (d.reliabilityScore >= d.definition.reliabilityFloor + 0.15) {
            this.transitionTo(d, DomainStatus.ACTIVE);
        }
    }

    private emptyDistribution(): DistributionSnapshot {
        return {
            mean: [],
            variance: [],
            sampleCount: 0,
            windowStart: Date.now(),
            windowEnd: Date.now(),
        };
    }

    private registerDefaultDomains(): void {
        const defaults: DomainDefinition[] = [
            {
                name: 'inference',
                confidenceThreshold: 0.7,
                reliabilityFloor: 0.6,
                maxAuthorityLevel: AuthorityLevel.AUTOMATED,
                allowCaching: true,
                driftSensitivity: 0.3,
            },
            {
                name: 'rendering',
                confidenceThreshold: 0.5,
                reliabilityFloor: 0.5,
                maxAuthorityLevel: AuthorityLevel.AUTOMATED,
                allowCaching: true,
                driftSensitivity: 0.2,
            },
            {
                name: 'physics',
                confidenceThreshold: 0.8,
                reliabilityFloor: 0.7,
                maxAuthorityLevel: AuthorityLevel.ASSISTED,
                allowCaching: false,
                driftSensitivity: 0.4,
            },
            {
                name: 'safety',
                confidenceThreshold: 0.95,
                reliabilityFloor: 0.9,
                maxAuthorityLevel: AuthorityLevel.ADVISORY,
                allowCaching: false,
                driftSensitivity: 0.1,
            },
            {
                name: 'general',
                confidenceThreshold: 0.6,
                reliabilityFloor: 0.5,
                maxAuthorityLevel: AuthorityLevel.ASSISTED,
                allowCaching: true,
                driftSensitivity: 0.3,
            },
        ];

        defaults.forEach(d => this.registerDomain(d));
    }
}
