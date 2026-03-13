/**
 * TerminalResolver - Ceiling-aware terminal resolution
 * 
 * For requests entering the final ~5% boundary:
 * - Resolve immediately into terminal stable state
 * - Deliver informational/planning/preview artifacts only
 * - Never allocate heavy compute
 * - Never promise later fulfillment
 * 
 * Purpose: Convert impossibility into closure, not failure.
 */

export type TerminalArtifact = 
  | 'informational'
  | 'planning'
  | 'preview'
  | 'estimation'
  | 'recommendation';

export interface TerminalResolution {
  isTerminal: true;
  artifactType: TerminalArtifact;
  artifact: {
    title: string;
    content: string;
    actionable: boolean;
  };
  computeAllocated: false;
  promiseMade: false;
  closureMessage: string;
}

export interface BoundaryRequest {
  type: 'certified' | 'deterministic' | 'instant_exact' | 'no_hardware' | 'user_refused';
  originalIntent: string;
  metadata?: Record<string, unknown>;
}

class TerminalResolverEngine {
  /**
   * Resolve a ceiling-boundary request to terminal state
   */
  resolve(request: BoundaryRequest): TerminalResolution {
    const artifact = this.generateArtifact(request);
    
    return {
      isTerminal: true,
      artifactType: artifact.type,
      artifact: {
        title: artifact.title,
        content: artifact.content,
        actionable: artifact.actionable
      },
      computeAllocated: false,
      promiseMade: false,
      closureMessage: this.getClosureMessage(request.type)
    };
  }

  private generateArtifact(request: BoundaryRequest): {
    type: TerminalArtifact;
    title: string;
    content: string;
    actionable: boolean;
  } {
    switch (request.type) {
      case 'certified':
        return {
          type: 'recommendation',
          title: 'Certified Execution Required',
          content: `This workload requires certified execution environment. 
                    Consider: certified cloud providers, on-premise certified hardware, 
                    or compliance-specific deployment options.`,
          actionable: true
        };
      
      case 'deterministic':
        return {
          type: 'planning',
          title: 'Deterministic Audit Path',
          content: `This workload requires deterministic, auditable execution.
                    Planning artifact generated with execution requirements and 
                    recommended audit-compliant infrastructure.`,
          actionable: true
        };
      
      case 'instant_exact':
        return {
          type: 'estimation',
          title: 'Execution Timeline Estimate',
          content: `Fresh + instant + exact computation conflict detected.
                    Estimated completion with exact results: variable based on queue.
                    Alternative: Accept approximation for immediate response.`,
          actionable: true
        };
      
      case 'no_hardware':
        return {
          type: 'informational',
          title: 'Hardware Requirements',
          content: `This workload requires specific hardware capabilities not 
                    currently available. Review hardware requirements and 
                    consider alternative approaches.`,
          actionable: false
        };
      
      case 'user_refused':
        return {
          type: 'informational',
          title: 'Request Closed',
          content: `Request closed per user preference. No compute allocated.
                    Configuration and preferences preserved for future sessions.`,
          actionable: false
        };
      
      default:
        return {
          type: 'informational',
          title: 'Request Resolved',
          content: 'Request has been resolved to informational output.',
          actionable: false
        };
    }
  }

  private getClosureMessage(type: BoundaryRequest['type']): string {
    const messages: Record<string, string> = {
      certified: 'Resolved to recommendation artifact. No compute allocated.',
      deterministic: 'Resolved to planning artifact. Audit requirements documented.',
      instant_exact: 'Resolved to estimation. Approximation available if preferred.',
      no_hardware: 'Resolved to informational artifact. Hardware requirements listed.',
      user_refused: 'Closed per user preference. No action taken.'
    };
    
    return messages[type] || 'Request resolved to terminal state.';
  }

  /**
   * Check if a request should go to terminal resolution
   */
  shouldTerminate(request: {
    requiresCertified?: boolean;
    requiresDeterministic?: boolean;
    requiresInstantExact?: boolean;
    hasHardware?: boolean;
    userRefused?: boolean;
  }): { terminate: boolean; reason?: BoundaryRequest['type'] } {
    if (request.userRefused) {
      return { terminate: true, reason: 'user_refused' };
    }
    if (request.requiresCertified) {
      return { terminate: true, reason: 'certified' };
    }
    if (request.requiresDeterministic) {
      return { terminate: true, reason: 'deterministic' };
    }
    if (request.requiresInstantExact) {
      return { terminate: true, reason: 'instant_exact' };
    }
    if (request.hasHardware === false) {
      return { terminate: true, reason: 'no_hardware' };
    }
    
    return { terminate: false };
  }
}

export const terminalResolver = new TerminalResolverEngine();
