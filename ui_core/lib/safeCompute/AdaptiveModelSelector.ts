// AdaptiveModelSelector - Auto-selects optimal model
// Auto-picks the right model size based on RAM available
// Prevents GPU memory mismatch errors
// Always picks the fastest safe option

import { ModelVariant, SystemLoad } from './types';

class AdaptiveModelSelector {
  private models: ModelVariant[] = [
    { id: 'tiny', name: 'HYPER Tiny', size: 'tiny', requiredRamMb: 512, accuracy: 0.75, speed: 1.0 },
    { id: 'small', name: 'HYPER Small', size: 'small', requiredRamMb: 1024, accuracy: 0.85, speed: 0.8 },
    { id: 'medium', name: 'HYPER Medium', size: 'medium', requiredRamMb: 2048, accuracy: 0.92, speed: 0.5 },
    { id: 'large', name: 'HYPER Large', size: 'large', requiredRamMb: 4096, accuracy: 0.98, speed: 0.3 },
  ];

  private currentModel: ModelVariant | null = null;
  private listeners: Set<(model: ModelVariant | null) => void> = new Set();

  getAvailableModels(): ModelVariant[] {
    return [...this.models];
  }

  getCurrentModel(): ModelVariant | null {
    return this.currentModel;
  }

  // Select best model based on available resources
  selectOptimalModel(systemLoad: SystemLoad, preferSpeed: boolean = false): ModelVariant {
    const availableRam = systemLoad.availableRam;
    
    // Filter models that fit in available RAM with 20% buffer
    const compatibleModels = this.models.filter(
      model => model.requiredRamMb * 1.2 <= availableRam
    );
    
    if (compatibleModels.length === 0) {
      // Fallback to smallest model
      this.currentModel = this.models[0];
      this.notifyListeners();
      return this.currentModel;
    }
    
    // Sort by preference
    const sorted = [...compatibleModels].sort((a, b) => {
      if (preferSpeed) {
        return b.speed - a.speed; // Higher speed first
      }
      return b.accuracy - a.accuracy; // Higher accuracy first
    });
    
    this.currentModel = sorted[0];
    this.notifyListeners();
    return this.currentModel;
  }

  // Check if current model is still valid for system state
  validateCurrentModel(systemLoad: SystemLoad): boolean {
    if (!this.currentModel) return false;
    return this.currentModel.requiredRamMb * 1.2 <= systemLoad.availableRam;
  }

  // Get model recommendation with explanation
  getRecommendation(systemLoad: SystemLoad): {
    model: ModelVariant;
    reason: string;
    canUpgrade: boolean;
    canDowngrade: boolean;
  } {
    const optimal = this.selectOptimalModel(systemLoad);
    const currentIndex = this.models.findIndex(m => m.id === optimal.id);
    
    let reason = '';
    if (systemLoad.availableRam < 1024) {
      reason = 'Limited RAM available - using compact model for stability';
    } else if (systemLoad.isOverheating) {
      reason = 'Thermal limits detected - using efficient model';
    } else if (systemLoad.availableRam >= 4096) {
      reason = 'Optimal resources available - using high-accuracy model';
    } else {
      reason = 'Balanced selection based on available resources';
    }
    
    return {
      model: optimal,
      reason,
      canUpgrade: currentIndex < this.models.length - 1,
      canDowngrade: currentIndex > 0,
    };
  }

  // Force select a specific model
  forceSelect(modelId: string): ModelVariant | null {
    const model = this.models.find(m => m.id === modelId);
    if (model) {
      this.currentModel = model;
      this.notifyListeners();
    }
    return model || null;
  }

  subscribe(listener: (model: ModelVariant | null) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notifyListeners(): void {
    this.listeners.forEach(listener => listener(this.currentModel));
  }
}

export const adaptiveModelSelector = new AdaptiveModelSelector();
