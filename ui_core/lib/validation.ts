import { z } from "zod";

// ============================================
// Job Validation Schemas
// ============================================

export const createJobSchema = z.object({
  modelId: z.string().uuid("Invalid model ID"),
  inputData: z.object({
    prompt: z.string().min(1, "Prompt is required").max(32000, "Prompt too long"),
  }),
  enabledModules: z.array(z.string()).optional().default([]),
  options: z
    .object({
      batchSize: z.number().int().min(1).max(128).optional().default(1),
      maxTokens: z.number().int().min(1).max(32000).optional().default(512),
      timeoutMs: z.number().int().min(1000).max(300000).optional().default(60000),
      callbackUrl: z.string().url().optional(),
      temperature: z.number().min(0).max(2).optional().default(0.7),
    })
    .optional()
    .default({}),
  priority: z.number().int().min(1).max(10).optional().default(5),
});

export type CreateJobInput = z.infer<typeof createJobSchema>;

// ============================================
// Module Config Validation Schemas
// ============================================

export const updateModuleConfigSchema = z.object({
  enabled: z.boolean().optional(),
  config: z.record(z.unknown()).optional(),
});

export type UpdateModuleConfigInput = z.infer<typeof updateModuleConfigSchema>;

// ============================================
// Settings Validation Schemas
// ============================================

export const updateProfileSchema = z.object({
  fullName: z.string().min(1).max(100).optional(),
  company: z.string().max(100).optional(),
  avatarUrl: z.string().url().optional().nullable(),
});

export type UpdateProfileInput = z.infer<typeof updateProfileSchema>;

export const createApiKeySchema = z.object({
  keyName: z.string().min(1, "Key name is required").max(50, "Key name too long"),
  expiresAt: z.string().datetime().optional().nullable(),
});

export type CreateApiKeyInput = z.infer<typeof createApiKeySchema>;

export const updateNotificationPrefsSchema = z.object({
  emailNotifications: z.boolean().optional(),
  jobCompletionAlerts: z.boolean().optional(),
  systemAlerts: z.boolean().optional(),
  weeklyDigest: z.boolean().optional(),
});

export type UpdateNotificationPrefsInput = z.infer<typeof updateNotificationPrefsSchema>;

// ============================================
// Webhook Validation Schemas
// ============================================

export const testWebhookSchema = z.object({
  url: z.string().url("Invalid webhook URL"),
  method: z.enum(["GET", "POST", "PUT", "DELETE"]).optional().default("POST"),
  headers: z.record(z.string()).optional().default({}),
  body: z.string().optional().default("{}"),
});

export type TestWebhookInput = z.infer<typeof testWebhookSchema>;

// ============================================
// Alert Validation Schemas
// ============================================

export const createAlertSchema = z.object({
  title: z.string().min(1).max(200),
  message: z.string().min(1).max(1000),
  severity: z.enum(["info", "warning", "error", "critical"]).default("info"),
  alertType: z.string().min(1).max(50),
  moduleName: z.string().max(50).optional().nullable(),
});

export type CreateAlertInput = z.infer<typeof createAlertSchema>;

// ============================================
// Validation Helper
// ============================================

export function validateInput<T>(
  schema: z.ZodSchema<T>,
  data: unknown,
): { success: true; data: T } | { success: false; errors: string[] } {
  const result = schema.safeParse(data);

  if (result.success) {
    return { success: true, data: result.data };
  }

  const errors = result.error.errors.map((err) => `${err.path.join(".")}: ${err.message}`);

  return { success: false, errors };
}
