import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Cpu,
  Layers,
  Zap,
  Brain,
  Cloud,
  Code,
  BookOpen,
  Terminal,
} from "lucide-react";

const Documentation = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-16 overflow-x-hidden">
        <div className="mb-12">
          <h1 className="text-5xl font-display font-bold mb-4">
            <span className="text-primary">Technical</span> Documentation
          </h1>
          <p className="text-xl text-foreground/70 max-w-3xl">
            Complete guide to the 52-module Intelligent GPU System architecture
          </p>
        </div>

        <Tabs defaultValue="overview" className="space-y-8">
          <TabsList className="bg-card border border-border">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="architecture">Architecture</TabsTrigger>
            <TabsTrigger value="modules">Modules</TabsTrigger>
            <TabsTrigger value="api">API Reference</TabsTrigger>
            <TabsTrigger value="examples">Examples</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <Card className="p-8 bg-card border-border">
              <h2 className="text-3xl font-bold mb-6 flex items-center">
                <BookOpen className="mr-3 h-8 w-8 text-primary" />
                System Overview
              </h2>

              <div className="space-y-6 text-foreground/80">
                <p className="text-lg">
                  HYPER is a revolutionary software-only compute system that achieves 100% high-end GPU performance
                  parity through intelligent algorithms and zero hardware requirements.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
                  <div className="p-6 bg-muted/30 rounded-lg border border-border">
                    <h3 className="text-xl font-semibold mb-3 text-primary">Core Capabilities</h3>
                    <ul className="space-y-2">
                      <li>• AI inference (4-bit & full precision)</li>
                      <li>• 4K/240 FPS game rendering</li>
                      <li>• VR rendering (&lt;2ms latency)</li>
                      <li>• Hardware ray tracing (98-100% quality)</li>
                      <li>• 70B model training (95% efficiency)</li>
                      <li>• Cloud service (1000s+ users)</li>
                    </ul>
                  </div>

                  <div className="p-6 bg-muted/30 rounded-lg border border-border">
                    <h3 className="text-xl font-semibold mb-3 text-primary">Key Technologies</h3>
                    <ul className="space-y-2">
                      <li>• Neural approximation</li>
                      <li>• Predictive rendering</li>
                      <li>• Extreme quantization (1-8 bit)</li>
                      <li>• SIMD vectorization</li>
                      <li>• Smart caching & queuing</li>
                      <li>• Distributed model streaming</li>
                    </ul>
                  </div>
                </div>
              </div>
            </Card>

            <Card className="p-8 bg-card border-border">
              <h2 className="text-2xl font-bold mb-4">Quick Start</h2>
              <pre className="bg-background p-4 rounded-lg border border-border font-mono text-sm overflow-x-auto break-words whitespace-pre-wrap">
                <code className="block"><span className="text-primary"># Install the SDK</span>
                  <span className="text-foreground/80">pip install hyper-sdk</span>

                  <span className="text-primary"># Initialize the system</span>
                  <span className="text-foreground/80">from hyper_sdk import HyperEngine</span>
                  <span className="text-foreground/80">engine = HyperEngine()</span>

                  <span className="text-primary"># Run AI inference</span>
                  <span className="text-foreground/80">result = engine.infer(model, input_data)</span></code>
              </pre>
            </Card>
          </TabsContent>

          <TabsContent value="architecture" className="space-y-6">
            <Card className="p-8 bg-card border-border">
              <h2 className="text-3xl font-bold mb-6 flex items-center">
                <Layers className="mr-3 h-8 w-8 text-primary" />
                System Architecture
              </h2>

              <div className="space-y-8">
                <div>
                  <h3 className="text-xl font-semibold mb-4 text-primary">Layer 1: Core Emulation (Modules 1-31)</h3>
                  <p className="text-foreground/70 mb-4">
                    Foundation layer that emulates GPU hardware using CPU and software tricks.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {[
                      { name: "Deployment", desc: "System initialization & CPU detection" },
                      { name: "Compression", desc: "4/8-bit quantization" },
                      { name: "Kernel Emulator", desc: "Virtual CUDA kernels" },
                    ].map((item, idx) => (
                      <div key={idx} className="p-4 bg-muted/30 rounded border border-border">
                        <div className="font-semibold mb-1">{item.name}</div>
                        <div className="text-sm text-foreground/60">{item.desc}</div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-xl font-semibold mb-4 text-primary">Layer 2: Core Acceleration (Modules 32-43)</h3>
                  <p className="text-foreground/70 mb-4">
                    Advanced optimization modules that push performance beyond physical limits.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {[
                      { name: "Neural Approximation", desc: "+5-7% performance gain" },
                      { name: "Predictive Rendering", desc: "+5-7% speedup" },
                      { name: "Neural Ray Tracing", desc: "+8-10% improvement" },
                    ].map((item, idx) => (
                      <div key={idx} className="p-4 bg-muted/30 rounded border border-border">
                        <div className="font-semibold mb-1">{item.name}</div>
                        <div className="text-sm text-foreground/60">{item.desc}</div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-xl font-semibold mb-4 text-primary">Layer 3: Limitation Breakers (Modules 44-49)</h3>
                  <p className="text-foreground/70 mb-4">
                    Modules that solve the "impossible" challenges.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {[
                      { name: "4K/240 FPS Gaming", desc: "Adaptive layer system" },
                      { name: "VR Rendering", desc: "Predictive timewarp" },
                      { name: "Ray Tracing", desc: "98-100% visual quality" },
                      { name: "70B Training", desc: "95% efficiency" },
                    ].map((item, idx) => (
                      <div key={idx} className="p-4 bg-muted/30 rounded border border-border">
                        <div className="font-semibold mb-1">{item.name}</div>
                        <div className="text-sm text-foreground/60">{item.desc}</div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-xl font-semibold mb-4 text-primary">Layer 4: Scaling (Modules 50-52)</h3>
                  <p className="text-foreground/70 mb-4">
                    Cloud scaling modules for handling thousands of concurrent users.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {[
                      { name: "Job Queue", desc: "1000s queued jobs" },
                      { name: "Response Caching", desc: "85% cache hit rate" },
                      { name: "Model Streaming", desc: "Train 280GB on 16GB" },
                    ].map((item, idx) => (
                      <div key={idx} className="p-4 bg-muted/30 rounded border border-border">
                        <div className="font-semibold mb-1">{item.name}</div>
                        <div className="text-sm text-foreground/60">{item.desc}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="modules" className="space-y-6">
            <Card className="p-8 bg-card border-border">
              <h2 className="text-3xl font-bold mb-6 flex items-center">
                <Cpu className="mr-3 h-8 w-8 text-primary" />
                Module Reference (1-52)
              </h2>

              <div className="space-y-6 overflow-x-hidden">
                <div className="overflow-x-auto max-w-full">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-border">
                        <th className="text-left py-3 px-4 font-semibold">Module</th>
                        <th className="text-left py-3 px-4 font-semibold">Name</th>
                        <th className="text-left py-3 px-4 font-semibold">Purpose</th>
                        <th className="text-left py-3 px-4 font-semibold">Impact</th>
                      </tr>
                    </thead>
                    <tbody>
                      {[
                        { id: "1", name: "Adaptive Downgrade", purpose: "Intelligent task scaling", impact: "Zero Crash" },
                        { id: "2", name: "Progressive Compute", purpose: "Incremental result solving", impact: "4-8× speedup" },
                        { id: "48", name: "Mixture Of Experts", purpose: "Expert task routing", impact: "Optimal Logic" },
                        { id: "49", name: "Temporal Recon", purpose: "Time-based frame synthesis", impact: "120 FPS parity" },
                        { id: "50", name: "Semantic Cache", purpose: "Result pattern reuse", impact: "85% hit rate" },
                        { id: "51", name: "Chaos Resilience", purpose: "Auto-recovery logic", impact: "99.9% Uptime" },
                        { id: "52", name: "Self-Profiling", purpose: "Auto-hardware tuning", impact: "Hardware Neutral" },
                      ].map((module, idx) => (
                        <tr key={idx} className="border-b border-border/50 hover:bg-muted/30 transition-colors">
                          <td className="py-3 px-4 font-mono text-primary font-medium">{module.id}</td>
                          <td className="py-3 px-4 font-medium">{module.name}</td>
                          <td className="py-3 px-4 text-foreground/70">{module.purpose}</td>
                          <td className="py-3 px-4 text-primary">{module.impact}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="p-4 bg-primary/10 border border-primary/20 rounded-lg">
                  <p className="text-sm text-foreground/70">
                    <strong className="text-primary">Note:</strong> This table shows a subset of the 52 modules.
                    Complete module documentation includes detailed implementation guides, code examples, and performance benchmarks for each module.
                  </p>
                </div>
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="api" className="space-y-6">
            <Card className="p-8 bg-card border-border">
              <h2 className="text-3xl font-bold mb-6 flex items-center">
                <Terminal className="mr-3 h-8 w-8 text-primary" />
                API Reference
              </h2>

              <div className="space-y-8">
                <div>
                  <h3 className="text-xl font-semibold mb-4 text-primary">Authentication</h3>
                  <pre className="bg-background p-4 rounded-lg border border-border font-mono text-sm overflow-x-auto break-words whitespace-pre-wrap">
                    <code className="block"><span className="text-foreground/60"># Add your API key to headers</span>
                      <span className="text-foreground/80">Authorization: Bearer igpu_your_api_key_here</span></code>
                  </pre>
                </div>

                <div>
                  <h3 className="text-xl font-semibold mb-4 text-primary">AI Inference Endpoint</h3>
                  <pre className="bg-background p-4 rounded-lg border border-border font-mono text-sm overflow-x-auto break-words whitespace-pre-wrap">
                    <code className="block"><span className="text-primary">POST /api/v1/infer</span>

                      {`{
  "model": "llama-70b",
  "input": "Your prompt here",
  "quantization": "4bit"
}`}</code>
                  </pre>
                </div>

                <div>
                  <h3 className="text-xl font-semibold mb-4 text-primary">Rendering Endpoint</h3>
                  <pre className="bg-background p-4 rounded-lg border border-border font-mono text-sm overflow-x-auto break-words whitespace-pre-wrap">
                    <code className="block"><span className="text-primary">POST /api/v1/render</span>

                      {`{
  "scene": "scene_data",
  "resolution": "4K",
  "fps": 120,
  "ray_tracing": true
}`}</code>
                  </pre>
                </div>

                <div>
                  <h3 className="text-xl font-semibold mb-4 text-primary">Training Endpoint</h3>
                  <pre className="bg-background p-4 rounded-lg border border-border font-mono text-sm overflow-x-auto break-words whitespace-pre-wrap">
                    <code className="block"><span className="text-primary">POST /api/v1/train</span>

                      {`{
  "model_size": "70B",
  "dataset": "dataset_id",
  "epochs": 3,
  "lora": true
}`}</code>
                  </pre>
                </div>
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="examples" className="space-y-6">
            <Card className="p-8 bg-card border-border">
              <h2 className="text-3xl font-bold mb-6 flex items-center">
                <Code className="mr-3 h-8 w-8 text-primary" />
                Code Examples
              </h2>

              <div className="space-y-8">
                <div>
                  <h3 className="text-xl font-semibold mb-4 text-primary">Python Example</h3>
                  <pre className="bg-background p-4 rounded-lg border border-border font-mono text-sm overflow-x-auto break-words whitespace-pre-wrap">
                    <code className="block"><span className="text-foreground/60"># AI Inference Example</span>
                      <span className="text-primary">import</span> requests

                      api_key = "igpu_your_key"
                      url = "https://api.intelligpu.com/v1/infer"

                      response = requests.post(url,
                      headers={`{"Authorization": f"Bearer {api_key}"}`},
                      json={`{"model": "llama-70b", "input": "Hello"}`}
                      )

                      <span className="text-foreground/60"># Print result</span>
                      print(response.json())</code>
                  </pre>
                </div>

                <div>
                  <h3 className="text-xl font-semibold mb-4 text-primary">JavaScript Example</h3>
                  <pre className="bg-background p-4 rounded-lg border border-border font-mono text-sm overflow-x-auto break-words whitespace-pre-wrap">
                    <code className="block"><span className="text-foreground/60">// Rendering Example</span>
                      <span className="text-primary">const</span> response = await fetch('https://api.intelligpu.com/v1/render', {`{
  method: 'POST',
  headers: {
    'Authorization': 'Bearer igpu_your_key',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    resolution: '4K',
    fps: 120,
    ray_tracing: true
  })
}`});</code>
                  </pre>
                </div>
              </div>
            </Card>
          </TabsContent>
        </Tabs>

        <Footer />
      </div>
    </div>
  );
};

export default Documentation;
