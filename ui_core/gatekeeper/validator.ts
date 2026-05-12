/**
 * DETERMINISTIC LOGIC VALIDATOR
 * Fast-Reject Layer for the Gatekeeper Architecture.
 */

export enum ErrorCode {
  MISSING_FIELD = 'MISSING_FIELD',
  AMBIGUOUS_ENTITY = 'AMBIGUOUS_ENTITY',
  INVALID_COMBINATION = 'INVALID_COMBINATION',
  NOT_SUPPORTED = 'NOT_SUPPORTED'
}

export interface ValidationResult {
  isValid: boolean;
  canonicalKey?: string;
  error?: ErrorCode;
  details?: string;
}

export class LogicValidator {
  /**
   * Validates a structured token array and generates a canonical key.
   * Format: domain|entity|metric|time|filters
   */
  public static validate(tokens: any[]): ValidationResult {
    const types = tokens.map(t => t.type);

    // 1. Requirement Check
    if (!types.includes('DOMAIN')) {
      return { isValid: false, error: ErrorCode.MISSING_FIELD, details: 'Domain is required.' };
    }
    if (!types.includes('METRIC')) {
      return { isValid: false, error: ErrorCode.MISSING_FIELD, details: 'Metric is required.' };
    }

    // 2. Conflict Check (Example: Cannot have two domains)
    if (tokens.filter(t => t.type === 'DOMAIN').length > 1) {
      return { isValid: false, error: ErrorCode.INVALID_COMBINATION, details: 'Multiple domains selected.' };
    }

    // 3. Canonicalization
    // Sort by type priority to ensure deterministic key regardless of selection order
    const typeOrder = ['DOMAIN', 'ENTITY', 'METRIC', 'TIME', 'FILTER'];
    const sortedTokens = [...tokens].sort((a, b) => 
      typeOrder.indexOf(a.type) - typeOrder.indexOf(b.type)
    );

    const canonicalKey = sortedTokens.map(t => t.value.toLowerCase()).join('|');

    return {
      isValid: true,
      canonicalKey
    };
  }
}
