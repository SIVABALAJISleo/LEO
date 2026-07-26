// ============================================
// AI GPU Optimization Platform - API Library
// ============================================

// Types
export * from "./types";

// API Service Functions
export {
  // Auth
  login,
  signup,
  logout,
  getCurrentUser,

  // Models
  listModels,
  createModel,
  getModelById,
  updateModel,
  deleteModel,

  // Inference Jobs
  createInferenceJob,
  getActiveJobs,
  getJobs,
  getJobById,
  cancelJob,
  updateJobProgress,

  // Module Configs
  getModuleConfigs,
  updateModuleConfig,
  upsertModuleConfig,

  // Performance Metrics
  getPerformanceMetrics,

  // System Metrics
  getSystemMetricsRecent,
  insertSystemMetrics,

  // Alerts
  getAlerts,
  resolveAlert,
  createAlert,

  // Module Status
  getModuleStatuses,
  updateModuleStatus,
} from "./apiService";

// Realtime Subscriptions
export {
  subscribeToJobs,
  subscribeToJob,
  subscribeToMetrics,
  subscribeToJobMetrics,
  subscribeToAlerts,
  subscribeToNewAlerts,
  subscribeToModuleStatus,
  subscribeToModuleByName,
  subscribeToSystemMetrics,
  subscribeToDashboard,
} from "./realtime";
