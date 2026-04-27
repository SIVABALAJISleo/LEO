/**
 * DETERMINISTIC FSA ENGINE
 * Principles: 
 * 1. No raw text interpretation.
 * 2. Only valid next-states permitted.
 * 3. Output is a structured UUID array.
 */

export type TokenType = 'DOMAIN' | 'ENTITY' | 'METRIC' | 'TIME' | 'FILTER' | 'OPERATOR';

export interface Token {
  id: string; // UUID
  type: TokenType;
  value: string;
  label: string;
}

export interface StateDefinition {
  allowedTypes: TokenType[];
  isFinal: boolean;
}

export const FSA_STATES: Record<string, StateDefinition> = {
  START: { allowedTypes: ['DOMAIN'], isFinal: false },
  DOMAIN_SELECTED: { allowedTypes: ['ENTITY', 'METRIC'], isFinal: false },
  ENTITY_SELECTED: { allowedTypes: ['METRIC', 'FILTER'], isFinal: false },
  METRIC_SELECTED: { allowedTypes: ['TIME', 'OPERATOR', 'FILTER'], isFinal: true },
  FILTER_SELECTED: { allowedTypes: ['OPERATOR', 'METRIC', 'TIME'], isFinal: true },
  TIME_SELECTED: { allowedTypes: ['FILTER', 'OPERATOR'], isFinal: true },
};

export class GatekeeperFSA {
  private currentTokens: Token[] = [];
  private state: string = 'START';

  constructor(private ontology: any) {}

  public getValidNextTokens(input: string): Token[] {
    const currentState = FSA_STATES[this.state];
    if (!currentState) return [];

    // Filter ontology based on allowed types for current state
    return this.ontology.filter((t: Token) => 
      currentState.allowedTypes.includes(t.type) &&
      t.label.toLowerCase().includes(input.toLowerCase())
    );
  }

  public selectToken(token: Token): void {
    this.currentTokens.push(token);
    this.transition(token.type);
  }

  private transition(type: TokenType): void {
    switch (type) {
      case 'DOMAIN': this.state = 'DOMAIN_SELECTED'; break;
      case 'ENTITY': this.state = 'ENTITY_SELECTED'; break;
      case 'METRIC': this.state = 'METRIC_SELECTED'; break;
      case 'FILTER': this.state = 'FILTER_SELECTED'; break;
      case 'TIME': this.state = 'TIME_SELECTED'; break;
      default: break;
    }
  }

  public getQuery(): string[] {
    return this.currentTokens.map(t => t.id);
  }

  public getCanonicalString(): string {
    return this.currentTokens
      .sort((a, b) => a.type.localeCompare(b.type))
      .map(t => t.value)
      .join('|');
  }

  public reset(): void {
    this.currentTokens = [];
    this.state = 'START';
  }
}
