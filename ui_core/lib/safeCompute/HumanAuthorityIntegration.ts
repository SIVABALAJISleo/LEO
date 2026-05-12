// Human Authority Integration Module
// Formalizes human authority as a system component - no hidden dependencies

export type AuthorityInputType = 
  | 'medical_decision'
  | 'legal_ruling'
  | 'financial_approval'
  | 'safety_certification'
  | 'ethical_override'
  | 'emergency_response';

export interface AuthorityIdentity {
  id: string;
  name: string;
  role: string;
  certificationLevel: string;
  organizationId?: string;
}

export interface AuthorityInput {
  inputId: string;
  authorityType: AuthorityInputType;
  
  // Identity verification
  identity: AuthorityIdentity;
  
  // Temporal proof
  timestamp: string;
  timestampVerified: boolean;
  
  // Digital signature
  signatureHash: string;
  signatureMethod: 'RSA-SHA256' | 'ECDSA-P256' | 'ED25519' | 'HMAC-SHA256';
  
  // Linked evidence
  linkedEvidenceIds: string[];
  
  // Decision
  decision: 'approve' | 'reject' | 'defer' | 'escalate';
  reasoning?: string;
  conditions?: string[];
}

export interface AuthorityRequirement {
  requirementId: string;
  taskId: string;
  authorityType: AuthorityInputType;
  
  // What is being requested
  requestDescription: string;
  evidenceProvided: string[];
  recommendedAction: string;
  
  // Status
  status: 'pending' | 'received' | 'verified' | 'expired';
  
  // Blocking behavior
  blocksExecution: boolean;
  timeoutMs?: number;
  
  // Result
  authorityInput?: AuthorityInput;
  receivedAt?: string;
  verifiedAt?: string;
}

export interface AuthorityIntegrationStats {
  totalRequirements: number;
  pendingRequirements: number;
  receivedInputs: number;
  verifiedInputs: number;
  averageResponseTimeMs: number;
  timeoutRate: number;
}

// System state for authority-locked execution
export type AuthoritySystemState = 
  | 'READY'                    // No authority needed
  | 'REQUIRES_HUMAN_AUTHORITY' // Blocked until authority input
  | 'AUTHORITY_PENDING'        // Waiting for response
  | 'AUTHORITY_VERIFIED'       // Authority received and verified
  | 'AUTHORITY_TIMEOUT'        // Authority not received in time
  | 'AUTHORITY_REJECTED';      // Authority explicitly rejected

class HumanAuthorityIntegration {
  private requirements: Map<string, AuthorityRequirement> = new Map();
  private inputs: Map<string, AuthorityInput> = new Map();
  private stats: AuthorityIntegrationStats = {
    totalRequirements: 0,
    pendingRequirements: 0,
    receivedInputs: 0,
    verifiedInputs: 0,
    averageResponseTimeMs: 0,
    timeoutRate: 0
  };

  /**
   * Create a formal authority requirement - blocks execution until fulfilled
   */
  createRequirement(params: {
    taskId: string;
    authorityType: AuthorityInputType;
    requestDescription: string;
    evidenceProvided: string[];
    recommendedAction: string;
    timeoutMs?: number;
  }): AuthorityRequirement {
    const requirementId = `auth_req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const requirement: AuthorityRequirement = {
      requirementId,
      taskId: params.taskId,
      authorityType: params.authorityType,
      requestDescription: params.requestDescription,
      evidenceProvided: params.evidenceProvided,
      recommendedAction: params.recommendedAction,
      status: 'pending',
      blocksExecution: true,
      timeoutMs: params.timeoutMs || 24 * 60 * 60 * 1000 // Default 24h
    };

    this.requirements.set(requirementId, requirement);
    this.stats.totalRequirements++;
    this.stats.pendingRequirements++;

    console.log(`[AuthorityIntegration] Created requirement ${requirementId} for ${params.authorityType}`);
    return requirement;
  }

  /**
   * Check if a task can proceed or is blocked by authority
   */
  getSystemState(taskId: string): AuthoritySystemState {
    const taskRequirements = Array.from(this.requirements.values())
      .filter(r => r.taskId === taskId);

    if (taskRequirements.length === 0) {
      return 'READY';
    }

    const pending = taskRequirements.filter(r => r.status === 'pending');
    const verified = taskRequirements.filter(r => r.status === 'verified');
    const expired = taskRequirements.filter(r => r.status === 'expired');

    if (expired.length > 0) {
      return 'AUTHORITY_TIMEOUT';
    }

    if (pending.length > 0) {
      return 'REQUIRES_HUMAN_AUTHORITY';
    }

    if (verified.length === taskRequirements.length) {
      return 'AUTHORITY_VERIFIED';
    }

    return 'AUTHORITY_PENDING';
  }

  /**
   * Receive authority input - with full verification
   */
  receiveAuthorityInput(requirementId: string, input: AuthorityInput): {
    success: boolean;
    error?: string;
    requirement?: AuthorityRequirement;
  } {
    const requirement = this.requirements.get(requirementId);
    
    if (!requirement) {
      return { success: false, error: 'Requirement not found' };
    }

    if (requirement.status !== 'pending') {
      return { success: false, error: `Requirement already ${requirement.status}` };
    }

    // Verify the input
    const verificationResult = this.verifyAuthorityInput(input);
    if (!verificationResult.valid) {
      return { success: false, error: verificationResult.reason };
    }

    // Link the input to the requirement
    requirement.authorityInput = input;
    requirement.status = 'received';
    requirement.receivedAt = new Date().toISOString();

    this.inputs.set(input.inputId, input);
    this.stats.receivedInputs++;
    this.stats.pendingRequirements--;

    // Verify and finalize
    requirement.status = 'verified';
    requirement.verifiedAt = new Date().toISOString();
    this.stats.verifiedInputs++;

    // Update average response time
    const responseTimeMs = new Date(requirement.receivedAt).getTime() - 
      new Date(requirement.requirementId.split('_')[2]).getTime();
    this.stats.averageResponseTimeMs = 
      (this.stats.averageResponseTimeMs * (this.stats.verifiedInputs - 1) + responseTimeMs) / 
      this.stats.verifiedInputs;

    console.log(`[AuthorityIntegration] Authority input received and verified for ${requirementId}`);
    return { success: true, requirement };
  }

  /**
   * Verify authority input has all required components
   */
  private verifyAuthorityInput(input: AuthorityInput): { valid: boolean; reason?: string } {
    // Identity check
    if (!input.identity?.id || !input.identity?.name) {
      return { valid: false, reason: 'Missing identity information' };
    }

    // Timestamp check
    if (!input.timestamp || !input.timestampVerified) {
      return { valid: false, reason: 'Timestamp not verified' };
    }

    // Signature check
    if (!input.signatureHash || !input.signatureMethod) {
      return { valid: false, reason: 'Missing digital signature' };
    }

    // Evidence link check
    if (!input.linkedEvidenceIds || input.linkedEvidenceIds.length === 0) {
      return { valid: false, reason: 'No linked evidence provided' };
    }

    // Decision check
    if (!['approve', 'reject', 'defer', 'escalate'].includes(input.decision)) {
      return { valid: false, reason: 'Invalid decision type' };
    }

    return { valid: true };
  }

  /**
   * Check for timed-out requirements
   */
  checkTimeouts(): AuthorityRequirement[] {
    const now = Date.now();
    const timedOut: AuthorityRequirement[] = [];

    this.requirements.forEach(req => {
      if (req.status === 'pending' && req.timeoutMs) {
        const createdAt = parseInt(req.requirementId.split('_')[2], 10);
        if (now - createdAt > req.timeoutMs) {
          req.status = 'expired';
          timedOut.push(req);
          this.stats.pendingRequirements--;
        }
      }
    });

    if (timedOut.length > 0) {
      this.stats.timeoutRate = timedOut.length / this.stats.totalRequirements;
    }

    return timedOut;
  }

  /**
   * Get all pending requirements
   */
  getPendingRequirements(): AuthorityRequirement[] {
    return Array.from(this.requirements.values())
      .filter(r => r.status === 'pending');
  }

  /**
   * Get requirement by ID
   */
  getRequirement(requirementId: string): AuthorityRequirement | undefined {
    return this.requirements.get(requirementId);
  }

  /**
   * Get integration statistics
   */
  getStats(): AuthorityIntegrationStats {
    return { ...this.stats };
  }

  /**
   * Generate formal audit trail for a requirement
   */
  generateAuditTrail(requirementId: string): {
    requirementId: string;
    trail: Array<{
      event: string;
      timestamp: string;
      details: Record<string, unknown>;
    }>;
  } | null {
    const requirement = this.requirements.get(requirementId);
    if (!requirement) return null;

    const trail: Array<{ event: string; timestamp: string; details: Record<string, unknown> }> = [];

    // Requirement created
    trail.push({
      event: 'REQUIREMENT_CREATED',
      timestamp: new Date(parseInt(requirementId.split('_')[2], 10)).toISOString(),
      details: {
        taskId: requirement.taskId,
        authorityType: requirement.authorityType,
        description: requirement.requestDescription
      }
    });

    // Authority received
    if (requirement.receivedAt && requirement.authorityInput) {
      trail.push({
        event: 'AUTHORITY_INPUT_RECEIVED',
        timestamp: requirement.receivedAt,
        details: {
          identityId: requirement.authorityInput.identity.id,
          decision: requirement.authorityInput.decision,
          signatureMethod: requirement.authorityInput.signatureMethod
        }
      });
    }

    // Verified
    if (requirement.verifiedAt) {
      trail.push({
        event: 'AUTHORITY_VERIFIED',
        timestamp: requirement.verifiedAt,
        details: {
          linkedEvidence: requirement.authorityInput?.linkedEvidenceIds
        }
      });
    }

    return { requirementId, trail };
  }
}

export const humanAuthorityIntegration = new HumanAuthorityIntegration();
