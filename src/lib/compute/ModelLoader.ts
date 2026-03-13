export interface ModelConfig {
    path: string;
    format: 'gguf' | 'onnx';
    quantization: 'q4_0' | 'q5_1' | 'q8_0' | 'f16';
    memoryRequiredMb: number;
}

export class ModelLoader {
    private static instance: ModelLoader;
    private loadedModels: Map<string, ModelConfig> = new Map();
    private maxMemoryMb = 4096; // Simulated 4GB limit for browser
    private currentMemoryUsage = 0;

    private constructor() { }

    static getInstance(): ModelLoader {
        if (!ModelLoader.instance) {
            ModelLoader.instance = new ModelLoader();
        }
        return ModelLoader.instance;
    }

    async loadModel(config: ModelConfig): Promise<boolean> {
        if (this.loadedModels.has(config.path)) {
            console.log(`[ModelLoader] Model ${config.path} already loaded`);
            return true;
        }

        if (this.currentMemoryUsage + config.memoryRequiredMb > this.maxMemoryMb) {
            console.warn(`[ModelLoader] Not enough memory to load ${config.path}. Evicting...`);
            this.evictLRU();
        }

        console.log(`[ModelLoader] Loading quantized model ${config.path} (${config.quantization})...`);

        // Simulate loading delay
        await new Promise(r => setTimeout(r, 1000 + (config.memoryRequiredMb / 10)));

        this.loadedModels.set(config.path, config);
        this.currentMemoryUsage += config.memoryRequiredMb;

        return true;
    }

    private evictLRU() {
        // Simple eviction: remove first found (not true LRU but sufficient for demo)
        const firstKey = this.loadedModels.keys().next().value;
        if (firstKey) {
            const model = this.loadedModels.get(firstKey);
            if (model) {
                this.currentMemoryUsage -= model.memoryRequiredMb;
                this.loadedModels.delete(firstKey);
                console.log(`[ModelLoader] Evicted ${firstKey}`);
            }
        }
    }

    getStats() {
        return {
            loaded: this.loadedModels.size,
            memoryUsage: this.currentMemoryUsage,
            limit: this.maxMemoryMb
        };
    }
}
