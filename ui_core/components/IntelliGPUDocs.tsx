import React from "react";
import { BookOpen, Layers, Cpu, Terminal, Code } from "lucide-react";
import { Card, CardContent } from "./ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";

export const IntelliGPUDocs = () => {
  return (
    <div className="bg-[#020813] text-slate-100 min-h-screen pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-12 text-center md:text-left">
          <h1 className="text-4xl font-extrabold text-white font-display mb-3 tracking-tight">
            Technical <span className="text-[#76B900]">Documentation</span>
          </h1>
          <p className="text-slate-400 text-sm sm:text-base max-w-3xl">
            Complete guide to the 52-module Intelligent GPU System architecture
          </p>
        </div>

        <Tabs defaultValue="overview" className="space-y-8">
          <TabsList className="bg-[#030c1b] border border-slate-800 p-1 rounded-lg">
            <TabsTrigger 
              value="overview" 
              className="data-[state=active]:bg-[#76B900] data-[state=active]:text-black text-slate-400 font-bold text-xs uppercase px-4 py-2"
            >
              Overview
            </TabsTrigger>
            <TabsTrigger 
              value="architecture" 
              className="data-[state=active]:bg-[#76B900] data-[state=active]:text-black text-slate-400 font-bold text-xs uppercase px-4 py-2"
            >
              Architecture
            </TabsTrigger>
            <TabsTrigger 
              value="modules" 
              className="data-[state=active]:bg-[#76B900] data-[state=active]:text-black text-slate-400 font-bold text-xs uppercase px-4 py-2"
            >
              Modules
            </TabsTrigger>
            <TabsTrigger 
              value="api" 
              className="data-[state=active]:bg-[#76B900] data-[state=active]:text-black text-slate-400 font-bold text-xs uppercase px-4 py-2"
            >
              API Reference
            </TabsTrigger>
            <TabsTrigger 
              value="examples" 
              className="data-[state=active]:bg-[#76B900] data-[state=active]:text-black text-slate-400 font-bold text-xs uppercase px-4 py-2"
            >
              Examples
            </TabsTrigger>
          </TabsList>

          {/* Overview Content */}
          <TabsContent value="overview" className="space-y-6 animate-in fade-in duration-300">
            <Card className="bg-[#030c1b] border border-slate-800/80">
              <CardContent className="p-8">
                <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
                  <BookOpen className="mr-3 h-6 w-6 text-[#76B900]" />
                  System Overview
                </h2>

                <div className="space-y-6 text-slate-300 text-sm">
                  <p className="text-base leading-relaxed">
                    IntelliGPU is a revolutionary software-only compute system that achieves 100% high-end GPU performance parity through intelligent algorithms and zero hardware requirements.
                  </p>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
                    <div className="p-6 bg-slate-900/30 rounded-lg border border-slate-800">
                      <h3 className="text-lg font-bold mb-3 text-[#76B900]">Core Capabilities</h3>
                      <ul className="space-y-2 text-xs text-slate-400">
                        <li>• AI inference (4-bit & full precision)</li>
                        <li>• 4K/240 FPS game rendering</li>
                        <li>• VR rendering (&lt;2ms latency)</li>
                        <li>• Hardware ray tracing (98-100% quality)</li>
                        <li>• 70B model training (95% efficiency)</li>
                        <li>• Cloud service (1000s+ users)</li>
                      </ul>
                    </div>

                    <div className="p-6 bg-slate-900/30 rounded-lg border border-slate-800">
                      <h3 className="text-lg font-bold mb-3 text-[#76B900]">Key Technologies</h3>
                      <ul className="space-y-2 text-xs text-slate-400">
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
              </CardContent>
            </Card>

            <Card className="bg-[#030c1b] border border-slate-800/80">
              <CardContent className="p-8">
                <h2 className="text-xl font-bold text-white mb-4">Quick Start</h2>
                <pre className="bg-[#020813] p-5 rounded-lg border border-slate-800 font-mono text-xs text-slate-300 overflow-x-auto whitespace-pre">
                  <code>
                    <span className="text-slate-500"># Install the SDK</span>{"\n"}
                    <span className="text-[#76B900]">pip install intelligpu</span>{"\n\n"}
                    <span className="text-slate-500"># Initialize the system</span>{"\n"}
                    <span className="text-blue-400">from</span> intelligpu <span className="text-blue-400">import</span> GPUEngine{"\n"}
                    <span>engine = GPUEngine()</span>{"\n\n"}
                    <span className="text-slate-500"># Run AI inference</span>{"\n"}
                    <span>result = engine.infer(model, input_data)</span>
                  </code>
                </pre>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Architecture Content */}
          <TabsContent value="architecture" className="space-y-6 animate-in fade-in duration-300">
            <Card className="bg-[#030c1b] border border-slate-800/80">
              <CardContent className="p-8">
                <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
                  <Layers className="mr-3 h-6 w-6 text-[#76B900]" />
                  System Architecture
                </h2>

                <div className="space-y-8 text-sm">
                  {/* Layer 1 */}
                  <div>
                    <h3 className="text-base font-bold mb-1 text-[#76B900]">Layer 1: Core Emulation (Modules 1-31)</h3>
                    <p className="text-slate-400 mb-4 text-xs leading-relaxed">
                      Foundation layer that emulates GPU hardware using CPU and software tricks.
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {[
                        { name: "Deployment", desc: "System initialization & CPU detection" },
                        { name: "Compression", desc: "4/8-bit quantization" },
                        { name: "Kernel Emulator", desc: "Virtual CUDA kernels" },
                      ].map((item, idx) => (
                        <div key={idx} className="p-4 bg-[#0b1329]/50 rounded border border-slate-800/80 text-xs">
                          <div className="font-bold text-slate-100 mb-1">{item.name}</div>
                          <div className="text-slate-400">{item.desc}</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Layer 2 */}
                  <div>
                    <h3 className="text-base font-bold mb-1 text-[#76B900]">Layer 2: Breakthrough (Modules 32-43)</h3>
                    <p className="text-slate-400 mb-4 text-xs leading-relaxed">
                      Advanced optimization modules that push performance beyond physical limits.
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {[
                        { name: "Neural Approximation", desc: "+5-7% performance gain" },
                        { name: "Predictive Rendering", desc: "+5-7% speedup" },
                        { name: "Neural Ray Tracing", desc: "+8-10% improvement" },
                      ].map((item, idx) => (
                        <div key={idx} className="p-4 bg-[#0b1329]/50 rounded border border-slate-800/80 text-xs">
                          <div className="font-bold text-slate-100 mb-1">{item.name}</div>
                          <div className="text-slate-400">{item.desc}</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Layer 3 */}
                  <div>
                    <h3 className="text-base font-bold mb-1 text-[#76B900]">Layer 3: Limitation Breakers (Modules 44-49)</h3>
                    <p className="text-slate-400 mb-4 text-xs leading-relaxed">
                      Modules that solve the "impossible" challenges.
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      {[
                        { name: "4K/240 FPS Gaming", desc: "Adaptive layer system" },
                        { name: "VR Rendering", desc: "Predictive timewarp" },
                        { name: "Ray Tracing", desc: "98-100% visual quality" },
                        { name: "70B Training", desc: "95% efficiency" },
                      ].map((item, idx) => (
                        <div key={idx} className="p-4 bg-[#0b1329]/50 rounded border border-slate-800/80 text-xs">
                          <div className="font-bold text-slate-100 mb-1">{item.name}</div>
                          <div className="text-slate-400">{item.desc}</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Layer 4 */}
                  <div>
                    <h3 className="text-base font-bold mb-1 text-[#76B900]">Layer 4: Scaling (Modules 50-52)</h3>
                    <p className="text-slate-400 mb-4 text-xs leading-relaxed">
                      Cloud scaling modules for handling thousands of concurrent users.
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {[
                        { name: "Job Queue", desc: "1000s queued jobs" },
                        { name: "Response Caching", desc: "85% cache hit rate" },
                        { name: "Model Streaming", desc: "Train 280GB on 16GB" },
                      ].map((item, idx) => (
                        <div key={idx} className="p-4 bg-[#0b1329]/50 rounded border border-slate-800/80 text-xs">
                          <div className="font-bold text-slate-100 mb-1">{item.name}</div>
                          <div className="text-slate-400">{item.desc}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Modules Content */}
          <TabsContent value="modules" className="space-y-6 animate-in fade-in duration-300">
            <Card className="bg-[#030c1b] border border-slate-800/80">
              <CardContent className="p-8">
                <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
                  <Cpu className="mr-3 h-6 w-6 text-[#76B900]" />
                  Module Reference (1-52)
                </h2>

                <div className="overflow-x-auto mb-6">
                  <table className="w-full text-left text-xs sm:text-sm">
                    <thead>
                      <tr className="border-b border-slate-800/80 pb-4 text-slate-400">
                        <th className="py-3 px-4 font-bold uppercase tracking-wider">Module</th>
                        <th className="py-3 px-4 font-bold uppercase tracking-wider">Name</th>
                        <th className="py-3 px-4 font-bold uppercase tracking-wider">Purpose</th>
                        <th className="py-3 px-4 font-bold uppercase tracking-wider text-[#76B900]">Impact</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/40">
                      {[
                        { num: "1", name: "Deployment", purpose: "System Initialization", impact: "Core" },
                        { num: "2", name: "Neural Compression", purpose: "4/8-bit quantization", impact: "4-8x speedup" },
                        { num: "48", name: "CUDA Accelerator", purpose: "Matrix throughput", impact: "640x speedup" },
                        { num: "49", name: "Distributed Trainer", purpose: "Big model training", impact: "95% efficiency" },
                        { num: "50", name: "Job Queue", purpose: "Request queuing", impact: "1000s users" },
                        { num: "51", name: "Response Cache", purpose: "Prediction & caching", impact: "85% hit rate" },
                        { num: "52", name: "Model Streaming", purpose: "Layer-by-layer loading", impact: "280GB on 16GB" },
                      ].map((row, idx) => (
                        <tr key={idx} className="hover:bg-slate-800/10 transition-colors">
                          <td className="py-3.5 px-4 font-bold text-[#76B900]">{row.num}</td>
                          <td className="py-3.5 px-4 font-bold text-slate-200">{row.name}</td>
                          <td className="py-3.5 px-4 text-slate-400">{row.purpose}</td>
                          <td className="py-3.5 px-4 font-bold text-emerald-400">{row.impact}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="p-4 bg-[#112415] border border-[#17431e] rounded-lg text-emerald-400 text-xs leading-relaxed font-medium">
                  <strong>Note:</strong> This table shows a subset of the 52 modules. Complete module documentation includes detailed implementation guides, code examples, and performance benchmarks for each module.
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* API Reference */}
          <TabsContent value="api" className="space-y-6 animate-in fade-in duration-300">
            <Card className="bg-[#030c1b] border border-slate-800/80">
              <CardContent className="p-8">
                <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
                  <Terminal className="mr-3 h-6 w-6 text-[#76B900]" />
                  Technical Documentation
                </h2>

                <div className="space-y-8">
                  {/* Authentication Section */}
                  <div>
                    <h3 className="text-lg font-bold text-[#76B900] mb-2 flex items-center">
                      Authentication
                    </h3>
                    <div className="bg-[#020813] border border-slate-800 p-4 rounded-lg font-mono text-xs text-slate-300">
                      <span className="text-slate-500"># Add your API key to headers</span>{"\n"}
                      <span className="text-slate-200">Authorization: Bearer igpu_your_api_key_here</span>
                    </div>
                  </div>

                  {/* Endpoints Section */}
                  <div className="space-y-6">
                    <div>
                      <h4 className="text-sm font-bold text-[#76B900] mb-2">AI Inference Endpoint</h4>
                      <div className="bg-[#020813] border border-slate-800 p-4 rounded-lg font-mono text-xs text-slate-300 space-y-3">
                        <div>
                          <span className="text-[#76B900] font-bold">POST</span> <span className="text-slate-100">/api/v1/infer</span>
                        </div>
                        <pre className="text-slate-400 overflow-x-auto">
                          {`{
  "model": "llama-70b",
  "input": "Your prompt here",
  "quantization": "4bit"
}`}
                        </pre>
                      </div>
                    </div>

                    <div>
                      <h4 className="text-sm font-bold text-[#76B900] mb-2">Rendering Endpoint</h4>
                      <div className="bg-[#020813] border border-slate-800 p-4 rounded-lg font-mono text-xs text-slate-300 space-y-3">
                        <div>
                          <span className="text-[#76B900] font-bold">POST</span> <span className="text-slate-100">/api/v1/render</span>
                        </div>
                        <pre className="text-slate-400 overflow-x-auto">
                          {`{
  "scene": "scene_data",
  "resolution": "4K",
  "fps": 120,
  "ray_tracing": true
}`}
                        </pre>
                      </div>
                    </div>

                    <div>
                      <h4 className="text-sm font-bold text-[#76B900] mb-2">Training Endpoint</h4>
                      <div className="bg-[#020813] border border-slate-800 p-4 rounded-lg font-mono text-xs text-slate-300 space-y-3">
                        <div>
                          <span className="text-[#76B900] font-bold">POST</span> <span className="text-slate-100">/api/v1/train</span>
                        </div>
                        <pre className="text-slate-400 overflow-x-auto">
                          {`{
  "model_size": "70B",
  "dataset": "dataset_id",
  "epochs": 3,
  "lora": true
}`}
                        </pre>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Examples */}
          <TabsContent value="examples" className="space-y-6 animate-in fade-in duration-300">
            <Card className="bg-[#030c1b] border border-slate-800/80">
              <CardContent className="p-8">
                <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
                  <Code className="mr-3 h-6 w-6 text-[#76B900]" />
                  Code Examples
                </h2>

                <div className="space-y-6">
                  {/* Python Example */}
                  <div>
                    <h3 className="text-base font-bold text-[#76B900] mb-2">Python Example</h3>
                    <div className="bg-[#020813] border border-slate-800 p-4 rounded-lg font-mono text-xs text-slate-300">
                      <pre className="overflow-x-auto text-slate-300">
{`# AI Inference Example
import requests

api_key = "igpu_your_key"
url = "https://api.intelligpu.com/v1/infer"
response = requests.post(url,
  headers={"Authorization": f"Bearer \${api_key}"},
  json={"model": "llama-70b", "input": "Hello"}
)

# Print result
print(response.json())`}
                      </pre>
                    </div>
                  </div>

                  {/* JavaScript Example */}
                  <div>
                    <h3 className="text-base font-bold text-[#76B900] mb-2">JavaScript Example</h3>
                    <div className="bg-[#020813] border border-slate-800 p-4 rounded-lg font-mono text-xs text-slate-300">
                      <pre className="overflow-x-auto text-slate-300">
{`// Rendering Example
const response = await fetch('https://api.intelligpu.com/v1/render', {
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
});`}
                      </pre>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};
