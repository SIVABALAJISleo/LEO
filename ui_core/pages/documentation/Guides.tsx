import { useState } from "react";
import { Navbar } from "@/components/Navbar";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { useNavigate } from "react-router-dom";
import {
  BookOpen,
  Key,
  Cpu,
  Layers,
  Terminal,
  GraduationCap,
  AlertTriangle,
  HelpCircle,
  ChevronRight,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  ExternalLink,
  Copy,
  Check,
  Zap,
  Settings,
  Play,
} from "lucide-react";

type Section =
  | "getting-started"
  | "authentication"
  | "core-concepts"
  | "gpu-modules"
  | "api-reference"
  | "tutorials"
  | "troubleshooting"
  | "faq"
  | "deployment";

type ModuleId =
  | "neural-compression"
  | "cuda-accelerator"
  | "job-queue"
  | "response-cache"
  | "model-streaming"
  | "neural-approximation"
  | "predictive-rendering"
  | "ray-tracing";

const sidebarItems = [
  { id: "getting-started", label: "Getting Started", icon: BookOpen },
  { id: "authentication", label: "Authentication", icon: Key },
  { id: "core-concepts", label: "Core Concepts", icon: Cpu },
  { id: "gpu-modules", label: "GPU Modules", icon: Layers },
  { id: "api-reference", label: "API Reference", icon: Terminal },
  { id: "tutorials", label: "Tutorials", icon: GraduationCap },
  { id: "troubleshooting", label: "Troubleshooting", icon: AlertTriangle },
  { id: "faq", label: "FAQ", icon: HelpCircle },
  { id: "deployment", label: "Deployment", icon: Settings },
] as const;

const gpuModules: { id: ModuleId; name: string; description: string }[] = [
  {
    id: "neural-compression",
    name: "Neural Compression",
    description: "4/8-bit quantization for models",
  },
  {
    id: "cuda-accelerator",
    name: "CUDA Accelerator",
    description: "640× matrix throughput improvement",
  },
  { id: "job-queue", name: "Job Queue", description: "Handle 1000s of concurrent jobs" },
  { id: "response-cache", name: "Response Cache", description: "85% cache hit rate" },
  { id: "model-streaming", name: "Model Streaming", description: "Train 280GB models on 16GB RAM" },
  {
    id: "neural-approximation",
    name: "Neural Approximation",
    description: "+5-7% performance gain",
  },
  { id: "predictive-rendering", name: "Predictive Rendering", description: "+5-7% speedup" },
  { id: "ray-tracing", name: "Neural Ray Tracing", description: "98-100% visual quality" },
];

const CodeBlock = ({
  code,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  language = "bash",
  showPlayground = false,
  playgroundEndpoint = "",
}: {
  code: string;
  language?: string;
  showPlayground?: boolean;
  playgroundEndpoint?: string;
}) => {
  const [copied, setCopied] = useState(false);
  const navigate = useNavigate();

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleOpenPlayground = () => {
    navigate(`/documentation/api-playground?endpoint=${encodeURIComponent(playgroundEndpoint)}`);
  };

  return (
    <div className="relative group">
      <pre className="bg-background border border-border rounded-lg p-4 overflow-x-auto">
        <code className="text-sm font-mono text-foreground/80">{code}</code>
      </pre>
      <div className="absolute top-2 right-2 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
        {showPlayground && (
          <Button
            size="sm"
            variant="outline"
            onClick={handleOpenPlayground}
            className="h-7 text-xs"
          >
            <Play className="h-3 w-3 mr-1" />
            Open in Playground
          </Button>
        )}
        <Button size="sm" variant="outline" onClick={handleCopy} className="h-7 w-7 p-0">
          {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
        </Button>
      </div>
    </div>
  );
};

const Guides = () => {
  const [activeSection, setActiveSection] = useState<Section>("getting-started");
  const [activeModule, setActiveModule] = useState<ModuleId | null>(null);

  const renderContent = () => {
    if (activeSection === "gpu-modules" && activeModule) {
      return renderModuleDetail(activeModule);
    }

    switch (activeSection) {
      case "getting-started":
        return <GettingStartedContent />;
      case "authentication":
        return <AuthenticationContent />;
      case "core-concepts":
        return <CoreConceptsContent />;
      case "gpu-modules":
        return <GPUModulesContent onSelectModule={(id) => setActiveModule(id)} />;
      case "api-reference":
        return <APIReferenceContent />;
      case "tutorials":
        return <TutorialsContent />;
      case "troubleshooting":
        return <TroubleshootingContent />;
      case "faq":
        return <FAQContent />;
      case "deployment":
        return <DeploymentContent />;
      default:
        return <GettingStartedContent />;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="flex pt-16">
        {/* Sidebar */}
        <aside className="w-64 border-r border-border h-[calc(100vh-4rem)] sticky top-16">
          <ScrollArea className="h-full py-6 px-4">
            <h2 className="text-lg font-semibold mb-4 px-2">Documentation</h2>
            <nav className="space-y-1">
              {sidebarItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => {
                    setActiveSection(item.id as Section);
                    setActiveModule(null);
                  }}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                    activeSection === item.id
                      ? "bg-primary text-primary-foreground"
                      : "text-foreground/70 hover:bg-muted hover:text-foreground"
                  }`}
                >
                  <item.icon className="h-4 w-4" />
                  {item.label}
                </button>
              ))}
            </nav>

            {activeSection === "gpu-modules" && (
              <>
                <Separator className="my-4" />
                <h3 className="text-sm font-medium mb-2 px-2 text-muted-foreground">Modules</h3>
                <nav className="space-y-1">
                  {gpuModules.map((module) => (
                    <button
                      key={module.id}
                      onClick={() => setActiveModule(module.id)}
                      className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                        activeModule === module.id
                          ? "bg-secondary text-secondary-foreground"
                          : "text-foreground/60 hover:bg-muted hover:text-foreground"
                      }`}
                    >
                      <ChevronRight className="h-3 w-3" />
                      {module.name}
                    </button>
                  ))}
                </nav>
              </>
            )}
          </ScrollArea>
        </aside>

        {/* Main Content */}
        <main className="flex-1 min-h-[calc(100vh-4rem)]">
          <ScrollArea className="h-[calc(100vh-4rem)]">
            <div className="max-w-4xl mx-auto px-8 py-8">
              {activeModule && activeSection === "gpu-modules" && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setActiveModule(null)}
                  className="mb-4"
                >
                  ← Back to Modules
                </Button>
              )}
              {renderContent()}
            </div>
          </ScrollArea>
        </main>
      </div>
    </div>
  );
};

// Content Components
const GettingStartedContent = () => (
  <div className="space-y-8">
    <div>
      <h1 className="text-4xl font-bold mb-4">Getting Started</h1>
      <p className="text-lg text-muted-foreground">
        Welcome to HYPER - the revolutionary software-only compute system that achieves 100%
        high-end GPU performance parity through intelligent algorithms.
      </p>
    </div>

    <Card className="p-6">
      <h2 className="text-2xl font-semibold mb-4">Quick Start</h2>
      <div className="space-y-4">
        <div>
          <h3 className="font-medium mb-2">1. Install the SDK</h3>
          <CodeBlock code="pip install hyper-sdk" language="bash" />
        </div>
        <div>
          <h3 className="font-medium mb-2">2. Initialize the Engine</h3>
          <CodeBlock
            code={`from hyper_sdk import HyperEngine

engine = HyperEngine()
engine.initialize()`}
            language="python"
          />
        </div>
        <div>
          <h3 className="font-medium mb-2">3. Run Your First Inference</h3>
          <CodeBlock
            code={`result = engine.infer(
    model="llama-70b",
    input="Hello, world!",
    quantization="4bit"
)
print(result.output)`}
            language="python"
            showPlayground
            playgroundEndpoint="/inference"
          />
        </div>
      </div>
    </Card>

    <Card className="p-6">
      <h2 className="text-2xl font-semibold mb-4">System Requirements</h2>
      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 bg-muted/30 rounded-lg">
          <h4 className="font-medium mb-2">Minimum</h4>
          <ul className="text-sm text-muted-foreground space-y-1">
            <li>• 8GB RAM</li>
            <li>• 4-core CPU</li>
            <li>• Python 3.8+</li>
            <li>• 10GB disk space</li>
          </ul>
        </div>
        <div className="p-4 bg-muted/30 rounded-lg">
          <h4 className="font-medium mb-2">Recommended</h4>
          <ul className="text-sm text-muted-foreground space-y-1">
            <li>• 32GB RAM</li>
            <li>• 16-core CPU (AVX2+)</li>
            <li>• Python 3.10+</li>
            <li>• 100GB SSD</li>
          </ul>
        </div>
      </div>
    </Card>
  </div>
);

const AuthenticationContent = () => (
  <div className="space-y-8">
    <div>
      <h1 className="text-4xl font-bold mb-4">Authentication</h1>
      <p className="text-lg text-muted-foreground">
        Learn how to authenticate with the HYPER API and manage your API keys.
      </p>
    </div>

    <Card className="p-6">
      <h2 className="text-2xl font-semibold mb-4">API Key Authentication</h2>
      <p className="text-muted-foreground mb-4">
        All API requests require authentication using a Bearer token in the Authorization header.
      </p>
      <CodeBlock
        code={`curl -X POST https://api.hyper.dev/v1/infer \\
  -H "Authorization: Bearer hyper_your_api_key_here" \\
  -H "Content-Type: application/json" \\
  -d '{"model": "llama-70b", "input": "Hello"}'`}
        language="bash"
        showPlayground
        playgroundEndpoint="/inference"
      />
    </Card>

    <Card className="p-6">
      <h2 className="text-2xl font-semibold mb-4">JavaScript SDK</h2>
      <CodeBlock
        code={`import { Hyper } from '@hyper-sdk/js';

const client = new Hyper({
  apiKey: process.env.HYPER_API_KEY
});

const result = await client.infer({
  model: 'llama-70b',
  input: 'Hello, world!'
});`}
        language="javascript"
      />
    </Card>

    <Card className="p-6">
      <h2 className="text-2xl font-semibold mb-4">Managing API Keys</h2>
      <p className="text-muted-foreground mb-4">
        Generate and manage your API keys from the Settings page in your dashboard.
      </p>
      <ul className="space-y-2 text-muted-foreground">
        <li className="flex items-center gap-2">
          <Zap className="h-4 w-4 text-primary" />
          Create multiple keys for different environments
        </li>
        <li className="flex items-center gap-2">
          <Zap className="h-4 w-4 text-primary" />
          Set expiration dates for enhanced security
        </li>
        <li className="flex items-center gap-2">
          <Zap className="h-4 w-4 text-primary" />
          Revoke keys instantly when compromised
        </li>
      </ul>
    </Card>
  </div>
);

const CoreConceptsContent = () => (
  <div className="space-y-8">
    <div>
      <h1 className="text-4xl font-bold mb-4">Core Concepts</h1>
      <p className="text-lg text-muted-foreground">
        Understand the fundamental concepts behind HYPER's architecture.
      </p>
    </div>

    <Card className="p-6">
      <h2 className="text-2xl font-semibold mb-4">52-Module Architecture</h2>
      <p className="text-muted-foreground mb-4">
        HYPER uses a layered architecture of 52 specialized modules:
      </p>
      <div className="space-y-4">
        <div className="p-4 bg-muted/30 rounded-lg">
          <Badge className="mb-2">Layer 1</Badge>
          <h4 className="font-medium">Core Emulation (Modules 1-31)</h4>
          <p className="text-sm text-muted-foreground">
            Foundation layer that emulates GPU hardware using CPU and software tricks.
          </p>
        </div>
        <div className="p-4 bg-muted/30 rounded-lg">
          <Badge className="mb-2">Layer 2</Badge>
          <h4 className="font-medium">Core Optimization (Modules 32-43)</h4>
          <p className="text-sm text-muted-foreground">
            Advanced optimization modules that push performance beyond physical limits.
          </p>
        </div>
        <div className="p-4 bg-muted/30 rounded-lg">
          <Badge className="mb-2">Layer 3</Badge>
          <h4 className="font-medium">Limitation Breakers (Modules 44-49)</h4>
          <p className="text-sm text-muted-foreground">
            Modules that solve the "impossible" challenges like 4K/240FPS gaming.
          </p>
        </div>
        <div className="p-4 bg-muted/30 rounded-lg">
          <Badge className="mb-2">Layer 4</Badge>
          <h4 className="font-medium">Scaling (Modules 50-52)</h4>
          <p className="text-sm text-muted-foreground">
            Cloud scaling modules for handling thousands of concurrent users.
          </p>
        </div>
      </div>
    </Card>

    <Card className="p-6">
      <h2 className="text-2xl font-semibold mb-4">Inference Jobs</h2>
      <p className="text-muted-foreground mb-4">
        Every AI workload runs as an inference job with configurable modules and priorities.
      </p>
      <CodeBlock
        code={`{
  "model_id": "llama-70b",
  "input_data": {"prompt": "Your text here"},
  "enabled_modules": ["neural-compression", "cuda-accelerator"],
  "priority": 5,
  "options": {
    "batch_size": 1,
    "max_tokens": 512,
    "timeout_ms": 30000
  }
}`}
        language="json"
        showPlayground
        playgroundEndpoint="/jobs"
      />
    </Card>
  </div>
);

const GPUModulesContent = ({ onSelectModule }: { onSelectModule: (id: ModuleId) => void }) => (
  <div className="space-y-8">
    <div>
      <h1 className="text-4xl font-bold mb-4">GPU Modules</h1>
      <p className="text-lg text-muted-foreground">
        Explore the 52 specialized modules that power HYPER's performance.
      </p>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {gpuModules.map((module) => (
        <Card
          key={module.id}
          className="p-6 cursor-pointer hover:border-primary transition-colors"
          onClick={() => onSelectModule(module.id)}
        >
          <div className="flex items-start justify-between">
            <div>
              <h3 className="font-semibold mb-2">{module.name}</h3>
              <p className="text-sm text-muted-foreground">{module.description}</p>
            </div>
            <ChevronRight className="h-5 w-5 text-muted-foreground" />
          </div>
        </Card>
      ))}
    </div>
  </div>
);

const renderModuleDetail = (moduleId: ModuleId) => {
  const moduleDetails: Record<
    ModuleId,
    {
      name: string;
      description: string;
      purpose: string;
      config: object;
      performance: string;
      usage: string;
    }
  > = {
    "neural-compression": {
      name: "Neural Compression",
      description: "Advanced 4/8-bit quantization for models without significant quality loss.",
      purpose: "Reduce model size and memory footprint while maintaining accuracy.",
      config: {
        enabled: true,
        bit_width: 4,
        calibration_samples: 512,
        preserve_outliers: true,
      },
      performance: "4-8× memory reduction, 2-4× speedup",
      usage: "Enable for large models (>7B parameters) when memory is constrained.",
    },
    "cuda-accelerator": {
      name: "CUDA Accelerator",
      description: "Optimized matrix multiplication using vectorized CPU instructions.",
      purpose: "Maximize throughput for matrix-heavy operations.",
      config: {
        enabled: true,
        use_avx512: true,
        thread_count: "auto",
        batch_optimization: true,
      },
      performance: "640× speedup on matrix operations",
      usage: "Always enable for inference workloads on supported CPUs.",
    },
    "job-queue": {
      name: "Job Queue",
      description: "Intelligent request queuing and prioritization system.",
      purpose: "Handle thousands of concurrent requests with fair scheduling.",
      config: {
        enabled: true,
        max_queue_size: 10000,
        priority_levels: 10,
        timeout_ms: 60000,
      },
      performance: "Handle 1000s of concurrent jobs",
      usage: "Essential for production deployments with multiple users.",
    },
    "response-cache": {
      name: "Response Cache",
      description: "Intelligent caching of inference results for repeated queries.",
      purpose: "Reduce latency and compute costs for common requests.",
      config: {
        enabled: true,
        cache_size_mb: 1024,
        ttl_seconds: 3600,
        similarity_threshold: 0.95,
      },
      performance: "85% cache hit rate on typical workloads",
      usage: "Enable for workloads with repetitive or similar queries.",
    },
    "model-streaming": {
      name: "Model Streaming",
      description: "Layer-by-layer model loading for memory-constrained environments.",
      purpose: "Run models larger than available RAM.",
      config: {
        enabled: true,
        chunk_size_mb: 256,
        prefetch_layers: 2,
        swap_policy: "lru",
      },
      performance: "Train 280GB models on 16GB RAM",
      usage: "Required for very large models or limited memory environments.",
    },
    "neural-approximation": {
      name: "Neural Approximation",
      description: "Replace expensive operations with learned approximations.",
      purpose: "Trade minimal accuracy for significant speedup.",
      config: {
        enabled: true,
        approximation_level: "medium",
        accuracy_threshold: 0.98,
        fallback_on_complex: true,
      },
      performance: "+5-7% overall performance gain",
      usage: "Enable when speed is prioritized over maximum precision.",
    },
    "predictive-rendering": {
      name: "Predictive Rendering",
      description: "Predict and pre-compute likely next outputs.",
      purpose: "Reduce perceived latency through speculation.",
      config: {
        enabled: true,
        prediction_depth: 3,
        speculation_budget_ms: 10,
        discard_on_mismatch: true,
      },
      performance: "+5-7% effective speedup",
      usage: "Best for interactive applications with predictable patterns.",
    },
    "ray-tracing": {
      name: "Neural Ray Tracing",
      description: "Neural network-accelerated ray tracing for rendering.",
      purpose: "Hardware-quality ray tracing without dedicated hardware.",
      config: {
        enabled: true,
        quality_level: "high",
        samples_per_pixel: 4,
        denoiser: "neural",
      },
      performance: "98-100% visual quality vs hardware RT",
      usage: "Enable for graphics workloads requiring realistic lighting.",
    },
  };

  const module = moduleDetails[moduleId];

  return (
    <div className="space-y-8">
      <div>
        <Badge className="mb-2">GPU Module</Badge>
        <h1 className="text-4xl font-bold mb-4">{module.name}</h1>
        <p className="text-lg text-muted-foreground">{module.description}</p>
      </div>

      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-3">Purpose</h2>
        <p className="text-muted-foreground">{module.purpose}</p>
      </Card>

      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-3">Configuration Options</h2>
        <CodeBlock code={JSON.stringify(module.config, null, 2)} language="json" />
      </Card>

      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-3">When to Use</h2>
        <p className="text-muted-foreground">{module.usage}</p>
      </Card>

      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-3">Performance Expectations</h2>
        <div className="flex items-center gap-2">
          <Zap className="h-5 w-5 text-primary" />
          <span className="font-medium">{module.performance}</span>
        </div>
      </Card>

      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-3">Example API Request</h2>
        <CodeBlock
          code={`curl -X POST https://api.intelligpu.com/v1/modules/configure \\
  -H "Authorization: Bearer igpu_your_api_key" \\
  -H "Content-Type: application/json" \\
  -d '${JSON.stringify({ module: moduleId, config: module.config }, null, 2)}'`}
          language="bash"
          showPlayground
          playgroundEndpoint="/modules"
        />
      </Card>
    </div>
  );
};

const APIReferenceContent = () => (
  <div className="space-y-8">
    <div>
      <h1 className="text-4xl font-bold mb-4">API Reference</h1>
      <p className="text-lg text-muted-foreground">
        Complete reference for all IntelliGPU API endpoints.
      </p>
    </div>

    <Card className="p-6">
      <h2 className="text-xl font-semibold mb-4">POST /v1/inference</h2>
      <p className="text-muted-foreground mb-4">Create a new inference job.</p>
      <CodeBlock
        code={`curl -X POST https://api.intelligpu.com/v1/inference \\
  -H "Authorization: Bearer igpu_your_api_key" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model_id": "llama-70b",
    "input": "Explain quantum computing",
    "options": {
      "max_tokens": 512,
      "temperature": 0.7
    }
  }'`}
        language="bash"
        showPlayground
        playgroundEndpoint="/inference"
      />
    </Card>

    <Card className="p-6">
      <h2 className="text-xl font-semibold mb-4">GET /v1/jobs</h2>
      <p className="text-muted-foreground mb-4">List all inference jobs.</p>
      <CodeBlock
        code={`curl https://api.intelligpu.com/v1/jobs \\
  -H "Authorization: Bearer igpu_your_api_key"`}
        language="bash"
        showPlayground
        playgroundEndpoint="/jobs"
      />
    </Card>

    <Card className="p-6">
      <h2 className="text-xl font-semibold mb-4">GET /v1/models</h2>
      <p className="text-muted-foreground mb-4">List available models.</p>
      <CodeBlock
        code={`curl https://api.intelligpu.com/v1/models \\
  -H "Authorization: Bearer igpu_your_api_key"`}
        language="bash"
        showPlayground
        playgroundEndpoint="/models"
      />
    </Card>

    <Card className="p-6">
      <h2 className="text-xl font-semibold mb-4">GET /v1/metrics</h2>
      <p className="text-muted-foreground mb-4">Get performance metrics.</p>
      <CodeBlock
        code={`curl https://api.intelligpu.com/v1/metrics?period=24h \\
  -H "Authorization: Bearer igpu_your_api_key"`}
        language="bash"
        showPlayground
        playgroundEndpoint="/metrics"
      />
    </Card>
  </div>
);

const TutorialsContent = () => (
  <div className="space-y-8">
    <div>
      <h1 className="text-4xl font-bold mb-4">Tutorials</h1>
      <p className="text-lg text-muted-foreground">
        Step-by-step guides to help you get the most out of IntelliGPU.
      </p>
    </div>

    <Card className="p-6">
      <Badge className="mb-2">Beginner</Badge>
      <h2 className="text-xl font-semibold mb-3">Your First Inference Job</h2>
      <p className="text-muted-foreground mb-4">
        Learn how to create and monitor your first AI inference job.
      </p>
      <ol className="space-y-4">
        <li>
          <h4 className="font-medium mb-2">1. Get your API key</h4>
          <p className="text-sm text-muted-foreground">
            Navigate to Settings → API Keys and generate a new key.
          </p>
        </li>
        <li>
          <h4 className="font-medium mb-2">2. Create an inference job</h4>
          <CodeBlock
            code={`const response = await fetch('/v1/inference', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + apiKey,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    model_id: 'llama-7b',
    input: 'Hello, world!'
  })
});`}
            language="javascript"
          />
        </li>
        <li>
          <h4 className="font-medium mb-2">3. Monitor job status</h4>
          <p className="text-sm text-muted-foreground">
            Check the Jobs page to see your job progress in real-time.
          </p>
        </li>
      </ol>
    </Card>

    <Card className="p-6">
      <Badge className="mb-2">Intermediate</Badge>
      <h2 className="text-xl font-semibold mb-3">Optimizing with Modules</h2>
      <p className="text-muted-foreground mb-4">
        Learn how to configure modules for maximum performance.
      </p>
      <CodeBlock
        code={`// Enable recommended modules for LLM inference
const config = {
  enabled_modules: [
    'neural-compression',
    'cuda-accelerator',
    'response-cache',
    'job-queue'
  ],
  module_configs: {
    'neural-compression': { bit_width: 4 },
    'response-cache': { ttl_seconds: 3600 }
  }
};`}
        language="javascript"
      />
    </Card>
  </div>
);

const TroubleshootingContent = () => (
  <div className="space-y-8">
    <div>
      <h1 className="text-4xl font-bold mb-4">Troubleshooting</h1>
      <p className="text-lg text-muted-foreground">Common issues and their solutions.</p>
    </div>

    <Card className="p-6">
      <h2 className="text-xl font-semibold mb-3">Job Stuck in Queue</h2>
      <p className="text-muted-foreground mb-4">If your job is stuck in the queue:</p>
      <ul className="space-y-2 text-muted-foreground">
        <li>• Check your API quota in Settings</li>
        <li>• Increase job priority if allowed</li>
        <li>• Check system status on the Monitoring page</li>
      </ul>
    </Card>

    <Card className="p-6">
      <h2 className="text-xl font-semibold mb-3">Out of Memory Errors</h2>
      <p className="text-muted-foreground mb-4">For memory issues:</p>
      <ul className="space-y-2 text-muted-foreground">
        <li>• Enable Neural Compression module</li>
        <li>• Enable Model Streaming for large models</li>
        <li>• Reduce batch size in job options</li>
      </ul>
    </Card>

    <Card className="p-6">
      <h2 className="text-xl font-semibold mb-3">Slow Performance</h2>
      <p className="text-muted-foreground mb-4">To improve performance:</p>
      <ul className="space-y-2 text-muted-foreground">
        <li>• Enable CUDA Accelerator module</li>
        <li>• Enable Response Cache for repeated queries</li>
        <li>• Use a smaller quantized model variant</li>
      </ul>
    </Card>
  </div>
);

const FAQContent = () => (
  <div className="space-y-8">
    <div>
      <h1 className="text-4xl font-bold mb-4">Frequently Asked Questions</h1>
    </div>

    <Card className="p-6">
      <h3 className="font-semibold mb-2">
        How does IntelliGPU achieve GPU-level performance without a GPU?
      </h3>
      <p className="text-muted-foreground">
        IntelliGPU uses a combination of neural approximation, extreme quantization, intelligent
        caching, and vectorized CPU instructions to achieve comparable performance to dedicated GPU
        hardware.
      </p>
    </Card>

    <Card className="p-6">
      <h3 className="font-semibold mb-2">What models are supported?</h3>
      <p className="text-muted-foreground">
        We support all major open-source LLMs including LLaMA, Mistral, Falcon, and custom
        fine-tuned models. Check the Models page for the full list.
      </p>
    </Card>

    <Card className="p-6">
      <h3 className="font-semibold mb-2">Can I run IntelliGPU on-premises?</h3>
      <p className="text-muted-foreground">
        Yes! Enterprise customers can deploy IntelliGPU on their own infrastructure. See the
        Deployment section for Docker and Kubernetes guides.
      </p>
    </Card>

    <Card className="p-6">
      <h3 className="font-semibold mb-2">What's the accuracy compared to GPU inference?</h3>
      <p className="text-muted-foreground">
        With 8-bit quantization, accuracy is typically within 0.5% of full precision. 4-bit
        quantization maintains 95-98% accuracy for most use cases.
      </p>
    </Card>
  </div>
);

const DeploymentContent = () => (
  <div className="space-y-8">
    <div>
      <h1 className="text-4xl font-bold mb-4">Deployment</h1>
      <p className="text-lg text-muted-foreground">
        Deploy IntelliGPU to production using various methods.
      </p>
    </div>

    <Card className="p-6">
      <h2 className="text-xl font-semibold mb-4">Deploy on Vercel</h2>
      <p className="text-muted-foreground mb-4">
        The simplest way to deploy the IntelliGPU dashboard.
      </p>
      <ol className="space-y-4 text-muted-foreground">
        <li>1. Fork the repository on GitHub</li>
        <li>2. Connect your Vercel account to GitHub</li>
        <li>3. Import the project and configure environment variables</li>
        <li>4. Deploy with one click</li>
      </ol>
      <CodeBlock
        code={`# Required environment variables
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_PUBLISHABLE_KEY=your_anon_key`}
        language="bash"
      />
    </Card>

    <Card className="p-6">
      <h2 className="text-xl font-semibold mb-4">Deploy with Docker</h2>
      <p className="text-muted-foreground mb-4">Run IntelliGPU in a containerized environment.</p>
      <CodeBlock
        code={`# Build the image
docker build -t intelligpu-app .

# Run the container
docker run -p 3000:3000 \\
  -e VITE_SUPABASE_URL=your_url \\
  -e VITE_SUPABASE_PUBLISHABLE_KEY=your_key \\
  intelligpu-app`}
        language="bash"
      />
    </Card>

    <Card className="p-6">
      <h2 className="text-xl font-semibold mb-4">Deploy with Docker Compose</h2>
      <p className="text-muted-foreground mb-4">
        For production deployments with additional services.
      </p>
      <CodeBlock
        code={`# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down`}
        language="bash"
      />
    </Card>
  </div>
);

export default Guides;
