/**
 * ═══════════════════════════════════════════════════════════════
 *  SCHEMA ENFORCER — Policy #9: Maintainability
 * ═══════════════════════════════════════════════════════════════
 *  All module communication must follow strict schemas.
 *  Invalid output → rejected, not interpreted.
 * ═══════════════════════════════════════════════════════════════
 */

import {
    GovernedInput,
    GovernedOutput,
    OutcomeFeedback,
    SchemaContract,
} from './types';

export class SchemaEnforcer {
    private static instance: SchemaEnforcer;
    private contracts = new Map<string, SchemaContract<unknown>>();

    private constructor() {
        this.registerBuiltInContracts();
    }

    static getInstance(): SchemaEnforcer {
        if (!SchemaEnforcer.instance) {
            SchemaEnforcer.instance = new SchemaEnforcer();
        }
        return SchemaEnforcer.instance;
    }

    register<T>(contract: SchemaContract<T>): void {
        this.contracts.set(contract.name, contract as SchemaContract<unknown>);
    }

    /**
     * Validate data against a named contract.
     * Returns true only if data is structurally valid.
     */
    enforce<T>(contractName: string, data: unknown): data is T {
        const contract = this.contracts.get(contractName);
        if (!contract) {
            console.error(`[SchemaEnforcer] Unknown contract: ${contractName}`);
            return false;
        }
        const valid = contract.validate(data);
        if (!valid) {
            console.warn(`[SchemaEnforcer] Rejected invalid data for contract: ${contractName}`);
        }
        return valid;
    }

    /** Validate a GovernedInput */
    validateInput(data: unknown): data is GovernedInput {
        return this.enforce<GovernedInput>('GovernedInput', data);
    }

    /** Validate a GovernedOutput */
    validateOutput(data: unknown): data is GovernedOutput {
        return this.enforce<GovernedOutput>('GovernedOutput', data);
    }

    /** Validate OutcomeFeedback */
    validateFeedback(data: unknown): data is OutcomeFeedback {
        return this.enforce<OutcomeFeedback>('OutcomeFeedback', data);
    }

    private registerBuiltInContracts(): void {
        // GovernedInput contract
        this.register<GovernedInput>({
            name: 'GovernedInput',
            version: 1,
            validate(data: unknown): data is GovernedInput {
                if (!data || typeof data !== 'object') return false;
                const d = data as Record<string, unknown>;
                return (
                    typeof d.id === 'string' &&
                    typeof d.domain === 'string' &&
                    typeof d.payload === 'string' &&
                    typeof d.timestamp === 'number' &&
                    typeof d.sourceSystem === 'string'
                );
            },
        });

        // GovernedOutput contract
        this.register<GovernedOutput>({
            name: 'GovernedOutput',
            version: 1,
            validate(data: unknown): data is GovernedOutput {
                if (!data || typeof data !== 'object') return false;
                const d = data as Record<string, unknown>;
                return (
                    typeof d.id === 'string' &&
                    typeof d.inputId === 'string' &&
                    typeof d.accepted === 'boolean' &&
                    typeof d.timestamp === 'number' &&
                    d.trace !== undefined
                );
            },
        });

        // OutcomeFeedback contract
        this.register<OutcomeFeedback>({
            name: 'OutcomeFeedback',
            version: 1,
            validate(data: unknown): data is OutcomeFeedback {
                if (!data || typeof data !== 'object') return false;
                const d = data as Record<string, unknown>;
                return (
                    typeof d.outputId === 'string' &&
                    typeof d.domain === 'string' &&
                    typeof d.correct === 'boolean' &&
                    typeof d.reviewerTrust === 'number' &&
                    typeof d.feedbackTimestamp === 'number'
                );
            },
        });
    }
}
