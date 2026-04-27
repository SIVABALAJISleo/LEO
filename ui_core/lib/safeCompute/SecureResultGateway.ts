// SecureResultGateway - Controls result access
// Users can only see final results, never system internals
// No GPU sharing, no remote access, no hack entry points
// Sanitizes all inputs and outputs

interface SanitizedResult {
  success: boolean;
  data: unknown;
  metadata: {
    processedAt: string;
    sanitized: boolean;
    version: string;
  };
}

class SecureResultGateway {
  private readonly VERSION = '1.0.0';
  private blockedFields = [
    'systemPath',
    'internalId',
    'gpuAddress',
    'memoryPointer',
    'processId',
    'kernelInfo',
    '__proto__',
    'constructor',
  ];

  // Sanitize input before processing
  sanitizeInput(input: unknown): unknown {
    if (typeof input === 'string') {
      // Remove potential injection patterns
      return input
        .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
        .replace(/javascript:/gi, '')
        .replace(/on\w+\s*=/gi, '')
        .trim();
    }
    
    if (Array.isArray(input)) {
      return input.map(item => this.sanitizeInput(item));
    }
    
    if (input && typeof input === 'object') {
      const sanitized: Record<string, unknown> = {};
      for (const [key, value] of Object.entries(input)) {
        // Skip blocked fields
        if (this.blockedFields.includes(key)) continue;
        // Skip prototype pollution attempts
        if (key.startsWith('__')) continue;
        sanitized[key] = this.sanitizeInput(value);
      }
      return sanitized;
    }
    
    return input;
  }

  // Sanitize output before returning to user
  sanitizeOutput(result: unknown): SanitizedResult {
    const sanitized = this.sanitizeInput(result);
    
    return {
      success: true,
      data: sanitized,
      metadata: {
        processedAt: new Date().toISOString(),
        sanitized: true,
        version: this.VERSION,
      },
    };
  }

  // Validate that no system internals are exposed
  validateResultSafety(result: unknown): boolean {
    const json = JSON.stringify(result);
    
    // Check for any blocked patterns
    const dangerousPatterns = [
      /\/proc\//i,
      /\/sys\//i,
      /0x[0-9a-f]{8,}/i,
      /password/i,
      /secret/i,
      /private_key/i,
    ];
    
    return !dangerousPatterns.some(pattern => pattern.test(json));
  }

  // Create a safe result envelope
  createResultEnvelope(jobId: string, result: unknown): SanitizedResult {
    if (!this.validateResultSafety(result)) {
      return {
        success: false,
        data: { error: 'Result contains restricted information' },
        metadata: {
          processedAt: new Date().toISOString(),
          sanitized: true,
          version: this.VERSION,
        },
      };
    }
    
    return this.sanitizeOutput(result);
  }

  // Get allowed result fields for public API
  getPublicResultFields(): string[] {
    return [
      'id',
      'status',
      'progress',
      'result',
      'completedAt',
      'error',
    ];
  }
}

export const secureResultGateway = new SecureResultGateway();
