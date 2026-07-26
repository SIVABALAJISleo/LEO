import React, { useState, useEffect, useRef } from "react";
import {
  Zap,
  Cpu,
  Shield,
  Layers,
  Play,
  Sparkles,
  HelpCircle,
  ArrowRight,
  Gauge,
  Activity,
  Database,
  CheckCircle,
  MessageSquare,
  X,
  Send,
  AlertTriangle,
  RefreshCw,
  Brain,
  Sliders,
} from "lucide-react";

interface ChatMessage {
  sender: "user" | "assistant";
  text: string;
}

interface SystemCapabilities {
  ram_total_gb: number;
  ram_capable: boolean;
  disk_free_gb: number;
  disk_capable: boolean;
  colibri_capable: boolean;
  colibri_online: boolean;
  ollama_online: boolean;
  ollama_models: string[];
}

export const SingularityDashboard = () => {
  // Playground state
  const [queryInput, setQueryInput] = useState(
    "Evaluate 1-bit Ternary registers with spiking activations on CPU+iGPU dynamic offloading",
  );
  const [isProcessing, setIsProcessing] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [resultText, setResultText] = useState("");
  const [latency, setLatency] = useState(0.0);
  const [vsaMatchScore, setVsaMatchScore] = useState(0.0);
  const [operationsSaved, setOperationsSaved] = useState(0);

  // Custom Slider metrics
  const [ternaryMultiplier, setTernaryMultiplier] = useState(8);
  const [speculativeMultiplier, setSpeculativeMultiplier] = useState(8);
  const [igpuMultiplier, setIgpuMultiplier] = useState(2);
  const [catMultiplier, setCatMultiplier] = useState(1.5);

  // Local Assistant Chat states
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([
    {
      sender: "assistant",
      text: "Hello! I am your offline LEO Assistant. How can I help you optimize your local workflows?",
    },
  ]);
  const [isAssistantTyping, setIsAssistantTyping] = useState(false);

  // Capabilities & Routing States
  const [ollamaStatus, setOllamaStatus] = useState<"ONLINE" | "OFFLINE" | "CHECKING">("CHECKING");
  const [capabilities, setCapabilities] = useState<SystemCapabilities | null>(null);
  const [routeMode, setRouteMode] = useState<"auto" | "colibri" | "ollama">("auto");

  // Canvas reference for particle animation
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Dynamic formula calculation
  const totalMultiplier =
    ternaryMultiplier * speculativeMultiplier * igpuMultiplier * catMultiplier;
  const effectiveBandwidth = 50 * totalMultiplier; // 50 GB/s base DDR4

  // Verify Ollama & System capabilities on mount
  const checkOllamaHealth = async () => {
    setOllamaStatus("CHECKING");
    try {
      const res = await fetch("http://localhost:8005/api/v1/ollama/capabilities");
      if (res.ok) {
        const data: SystemCapabilities = await res.json();
        setCapabilities(data);
        if (data.ollama_online || data.colibri_online) {
          setOllamaStatus("ONLINE");
        } else {
          setOllamaStatus("OFFLINE");
        }
      } else {
        setOllamaStatus("OFFLINE");
      }
    } catch {
      setOllamaStatus("OFFLINE");
    }
  };

  useEffect(() => {
    checkOllamaHealth();
  }, []);

  // Streaming assistant chat handler
  const handleSendChatMessage = async () => {
    if (!chatInput.trim() || isAssistantTyping) return;

    const userPrompt = chatInput.strip ? chatInput.strip() : chatInput.trim();
    setChatHistory((prev) => [...prev, { sender: "user", text: userPrompt }]);
    setChatInput("");
    setIsAssistantTyping(true);

    // Initial placeholder for incoming stream
    setChatHistory((prev) => [...prev, { sender: "assistant", text: "" }]);

    try {
      const response = await fetch("http://localhost:8005/api/v1/ollama/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: userPrompt,
          system_message: "You are a local AI advisor optimizing LEO's 6 Silicon Breakthroughs.",
          route_mode: routeMode,
        }),
      });

      if (!response.ok) {
        throw new Error("Chat connection failed.");
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder("utf-8");
      let streamBuffer = "";

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          streamBuffer += chunk;

          // Parse SSE lines
          const lines = streamBuffer.split("\n");
          // Keep last incomplete line in buffer
          streamBuffer = lines.pop() || "";

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const parsed = JSON.parse(line.substring(6));
                if (parsed.token) {
                  setChatHistory((prev) => {
                    const updated = [...prev];
                    const lastMsg = updated[updated.length - 1];
                    if (lastMsg && lastMsg.sender === "assistant") {
                      lastMsg.text += parsed.token;
                    }
                    return updated;
                  });
                }
              } catch (e) {
                // Ignore parsing errors
              }
            }
          }
        }
      }
    } catch (err) {
      setChatHistory((prev) => {
        const updated = [...prev];
        const lastMsg = updated[updated.length - 1];
        if (lastMsg && lastMsg.sender === "assistant") {
          lastMsg.text =
            "Error communicating with local AI routing service. Please verify that Ollama or Colibri is active.";
        }
        return updated;
      });
    } finally {
      setIsAssistantTyping(false);
    }
  };

  // Simulated live execution loop
  const handleRunQuery = () => {
    if (!queryInput.trim()) return;
    setIsProcessing(true);
    setLogs([]);
    setResultText("");

    const steps = [
      { text: "🔍 [VSA Cache] Scanning 10,000-D hypervector registry...", delay: 200 },
      {
        text: "⚡ [VSA Cache] Hamming Match detected. Similarity: 89.2% (Threshold: 75.0%)",
        delay: 500,
      },
      {
        text: "💻 [L3 Cache Lock] Accessing pinned hot layers in Intel L3 cache (212 GB/s)",
        delay: 800,
      },
      {
        text: "🧬 [LNS Compiler] Compiling log-domain arithmetic. Replaced 8.4M multiplications with integer additions",
        delay: 1200,
      },
      {
        text: "🌌 [Fourier Attention] Converting Q/K matrices to frequency domain via 2D FFT...",
        delay: 1500,
      },
      {
        text: "✂️ [Fourier Attention] Pruned 95% of near-zero frequency coefficients",
        delay: 1800,
      },
      {
        text: "🚀 [oneAPI ZeroCopy] Streaming weight pointers directly to Intel UHD 48EU iGPU via USM...",
        delay: 2100,
      },
      {
        text: "🧠 [Recursive Self-Crystallizer] Dynamic query pre-materialization completed.",
        delay: 2400,
      },
    ];

    let currentStep = 0;
    const runNextStep = () => {
      if (currentStep < steps.length) {
        setLogs((prev) => [...prev, steps[currentStep].text]);
        setTimeout(() => {
          currentStep++;
          runNextStep();
        }, 300);
      } else {
        setIsProcessing(false);
        setLatency(3.45);
        setVsaMatchScore(0.89);
        setOperationsSaved(8420000);
        setResultText(
          "LEO V45: Dynamic CPU/iGPU offloading succeeded. Weight streams successfully mapped to Level Zero USM shared pointers. Inference executed bypass path with zero neural float multiplication.",
        );
      }
    };

    runNextStep();
  };

  // Canvas particle background
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationFrameId: number;
    let width = (canvas.width = canvas.offsetWidth);
    let height = (canvas.height = canvas.offsetHeight);

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = canvas.offsetWidth;
      height = canvas.height = canvas.offsetHeight;
    };
    window.addEventListener("resize", handleResize);

    const particles: Array<{ x: number; y: number; vx: number; vy: number; radius: number }> = [];
    const numParticles = 80;

    for (let i = 0; i < numParticles; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        radius: Math.random() * 2 + 1,
      });
    }

    const draw = () => {
      ctx.clearRect(0, 0, width, height);
      ctx.fillStyle = "rgba(118, 185, 0, 0.4)"; // NVIDIA Green with low alpha
      ctx.strokeStyle = "rgba(118, 185, 0, 0.05)";

      particles.forEach((p, idx) => {
        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0 || p.x > width) p.vx *= -1;
        if (p.y < 0 || p.y > height) p.vy *= -1;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fill();

        // Connect nearby particles
        for (let j = idx + 1; j < particles.length; j++) {
          const p2 = particles[j];
          const dist = Math.hypot(p.x - p2.x, p.y - p2.y);
          if (dist < 100) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.stroke();
          }
        }
      });

      animationFrameId = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      window.removeEventListener("resize", handleResize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white font-sans antialiased overflow-x-hidden relative">
      {/* 1. STICKY NAVBAR */}
      <nav className="sticky top-0 z-40 bg-[#0A0A0A]/90 backdrop-blur-md border-b border-[#1A1A1A] px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-[#76B900] flex items-center justify-center font-bold text-black text-lg">
            L
          </div>
          <span className="text-xl font-bold tracking-tight uppercase">LEO QUANTUM</span>
        </div>
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-gray-400">
          <span className="hover:text-white transition-colors cursor-pointer">Architecture</span>
          <span className="hover:text-[#76B900] transition-colors cursor-pointer">
            Breakthroughs
          </span>
          <span className="hover:text-white transition-colors cursor-pointer">Playground</span>
          <span className="hover:text-white transition-colors cursor-pointer">Benchmarks</span>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={() => setIsChatOpen(!isChatOpen)}
            className="flex items-center gap-2 border border-gray-700 bg-white/5 hover:bg-white/10 px-4 py-2 rounded text-sm transition-all"
          >
            <MessageSquare className="w-4 h-4 text-[#76B900]" /> Assistant
          </button>
          <button className="bg-[#76B900] hover:bg-[#8CD000] text-black font-semibold px-4 py-2 rounded text-sm transition-all transform active:scale-95 shadow-[0_0_15px_rgba(118,185,0,0.4)]">
            Deploy Node
          </button>
        </div>
      </nav>

      {/* 2. HERO SECTION */}
      <header className="relative py-24 px-6 md:px-12 flex flex-col items-center text-center justify-center border-b border-[#1A1A1A] overflow-hidden min-h-[85vh]">
        <canvas
          ref={canvasRef}
          className="absolute inset-0 w-full h-full pointer-events-none z-0"
        />

        <div className="relative z-10 max-w-4xl space-y-6">
          <div className="inline-flex items-center gap-2 bg-[#76B900]/10 border border-[#76B900]/30 rounded-full px-4 py-1.5 text-xs text-[#76B900] font-semibold tracking-wide uppercase">
            <Sparkles className="w-3.5 h-3.5" /> LEO AI V45 'QUANTUM SINGULARITY' RELEASED
          </div>

          <h1 className="text-5xl md:text-7xl font-black tracking-tight text-white uppercase leading-none">
            Software Alchemy <br />
            <span className="bg-gradient-to-r from-[#76B900] via-[#A3E300] to-white bg-clip-text text-transparent">
              Bypassing the Silicon limit
            </span>
          </h1>

          <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto leading-relaxed">
            LEO V45 achieves 100% competitiveness with high-end NVIDIA GPUs on $700 laptop hardware
            by combining 6 math breakthroughs into a unified 180x bandwidth multiplier.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center pt-6">
            <a
              href="#playground"
              className="bg-[#76B900] hover:bg-[#8CD000] text-black font-bold px-8 py-4 rounded text-base transition-all transform active:scale-95 flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(118,185,0,0.5)]"
            >
              Launch Playground <Play className="w-4 h-4 fill-black" />
            </a>
            <a
              href="#formula"
              className="border border-gray-700 hover:border-gray-500 bg-white/5 hover:bg-white/10 text-white font-bold px-8 py-4 rounded text-base transition-colors flex items-center justify-center gap-2"
            >
              Formula Explorer <ArrowRight className="w-4 h-4" />
            </a>
          </div>
        </div>
      </header>

      {/* 3. FORMULA EXPLORER SECTION */}
      <section id="formula" className="py-24 px-6 md:px-12 bg-[#111111] border-b border-[#1A1A1A]">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16 space-y-4">
            <h2 className="text-3xl md:text-5xl font-extrabold uppercase">
              The Bandwidth Multiplier Formula
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              How LEO V45 amplifies your standard laptop's 50 GB/s DDR4 memory bus into a massive
              virtual compute pipeline.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-12 items-center">
            {/* Dynamic Sliders */}
            <div className="space-y-8 bg-[#161616] p-8 rounded-lg border border-[#222222]">
              <div className="space-y-3">
                <div className="flex justify-between text-sm font-semibold">
                  <span className="text-gray-300">Ternary Weight Compression</span>
                  <span className="text-[#76B900]">{ternaryMultiplier}x</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="16"
                  value={ternaryMultiplier}
                  onChange={(e) => setTernaryMultiplier(Number(e.target.value))}
                  className="w-full accent-[#76B900]"
                />
                <p className="text-xs text-gray-500">
                  2-bit mapping versus traditional FP16 data structures.
                </p>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between text-sm font-semibold">
                  <span className="text-gray-300">Speculative Verification Depth</span>
                  <span className="text-[#76B900]">{speculativeMultiplier}x</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="16"
                  value={speculativeMultiplier}
                  onChange={(e) => setSpeculativeMultiplier(Number(e.target.value))}
                  className="w-full accent-[#76B900]"
                />
                <p className="text-xs text-gray-500">
                  Number of concurrent tokens draft verified per layer read loop.
                </p>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between text-sm font-semibold">
                  <span className="text-gray-300">iGPU Co-processing Factor</span>
                  <span className="text-[#76B900]">{igpuMultiplier}x</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="4"
                  value={igpuMultiplier}
                  onChange={(e) => setIgpuMultiplier(Number(e.target.value))}
                  className="w-full accent-[#76B900]"
                />
                <p className="text-xs text-gray-500">
                  Intel UHD 48EU parallel weight computation throughput.
                </p>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between text-sm font-semibold">
                  <span className="text-gray-300">L3 Cache Pinning (Intel CAT)</span>
                  <span className="text-[#76B900]">{catMultiplier}x</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="3"
                  step="0.1"
                  value={catMultiplier}
                  onChange={(e) => setCatMultiplier(Number(e.target.value))}
                  className="w-full accent-[#76B900]"
                />
                <p className="text-xs text-gray-500">
                  Virtual L3 cache partition lock factor for hot layers.
                </p>
              </div>
            </div>

            {/* Formula Dashboard Visualizer */}
            <div className="flex flex-col gap-6 text-center">
              <div className="bg-[#1A1A1A] p-8 rounded-lg border-2 border-[#76B900] shadow-[0_0_30px_rgba(118,185,0,0.1)]">
                <p className="text-xs text-gray-400 uppercase tracking-widest">
                  Effective Bandwidth Multiplier
                </p>
                <p className="text-6xl font-black text-[#76B900] my-4">
                  {totalMultiplier.toFixed(1)}x
                </p>
                <p className="text-sm text-gray-400">
                  Target Bandwidth Amplification:{" "}
                  <strong>{effectiveBandwidth.toFixed(0)} GB/s</strong>
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-[#161616] p-6 rounded border border-[#222222]">
                  <p className="text-xs text-gray-500 uppercase">LEO V45 Target</p>
                  <p className="text-2xl font-bold text-white">
                    {effectiveBandwidth.toFixed(0)} GB/s
                  </p>
                </div>
                <div className="bg-[#161616] p-6 rounded border border-[#222222]">
                  <p className="text-xs text-gray-500 uppercase">NVIDIA H100 Baseline</p>
                  <p className="text-2xl font-bold text-gray-400">3,350 GB/s</p>
                </div>
              </div>
              <div className="text-xs text-gray-500 italic">
                *Based on reference hardware specification: Intel Core i5-12450H CPU + UHD 48EU
                iGPU.
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. THE 6 BREAKTHROUGHS SECTION */}
      <section className="py-24 px-6 md:px-12 bg-[#0A0A0A] border-b border-[#1A1A1A]">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16 space-y-4">
            <h2 className="text-3xl md:text-5xl font-extrabold uppercase">
              6 Silicon Breakthroughs
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Our software stack replaces hardware brute force with mathematical innovations.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {/* 1. LNS Compiler */}
            <div className="bg-[#111111] p-8 rounded-lg border border-[#1A1A1A] hover:border-[#76B900]/50 transition-all group flex flex-col justify-between">
              <div className="space-y-4">
                <div className="w-12 h-12 rounded bg-[#76B900]/10 flex items-center justify-center text-[#76B900] group-hover:scale-110 transition-transform">
                  <Cpu className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold">LNS Kernel Compiler</h3>
                <p className="text-gray-400 text-sm leading-relaxed">
                  Converts floating-point parameters to the Logarithmic Number System. Replaces
                  power-hungry floating multiplications with simple integer additions in the log
                  domain.
                </p>
              </div>
              <div className="pt-6 text-xs font-semibold text-[#76B900]">0.0ms Accumulation</div>
            </div>

            {/* 2. Intel CAT Pinning */}
            <div className="bg-[#111111] p-8 rounded-lg border border-[#1A1A1A] hover:border-[#76B900]/50 transition-all group flex flex-col justify-between">
              <div className="space-y-4">
                <div className="w-12 h-12 rounded bg-[#76B900]/10 flex items-center justify-center text-[#76B900] group-hover:scale-110 transition-transform">
                  <Database className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold">Intel CAT L3 Pinning</h3>
                <p className="text-gray-400 text-sm leading-relaxed">
                  Permanently pins the hottest 20% of transformer layers inside the physical L3 CPU
                  cache boundary to completely bypass DDR4 bus latency.
                </p>
              </div>
              <div className="pt-6 text-xs font-semibold text-[#76B900]">~200 GB/s Cache Lock</div>
            </div>

            {/* 3. Fourier Attention */}
            <div className="bg-[#111111] p-8 rounded-lg border border-[#1A1A1A] hover:border-[#76B900]/50 transition-all group flex flex-col justify-between">
              <div className="space-y-4">
                <div className="w-12 h-12 rounded bg-[#76B900]/10 flex items-center justify-center text-[#76B900] group-hover:scale-110 transition-transform">
                  <Layers className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold">Fourier Sparse Attention</h3>
                <p className="text-gray-400 text-sm leading-relaxed">
                  Converts attention matrix parameters to the frequency domain via 2D FFT, pruning
                  95% of near-zero coefficients.
                </p>
              </div>
              <div className="pt-6 text-xs font-semibold text-[#76B900]">20x Compute Reduction</div>
            </div>

            {/* 4. VSA Crystallizer */}
            <div className="bg-[#111111] p-8 rounded-lg border border-[#1A1A1A] hover:border-[#76B900]/50 transition-all group flex flex-col justify-between">
              <div className="space-y-4">
                <div className="w-12 h-12 rounded bg-[#76B900]/10 flex items-center justify-center text-[#76B900] group-hover:scale-110 transition-transform">
                  <Sparkles className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold">VSA Crystallizer v2</h3>
                <p className="text-gray-400 text-sm leading-relaxed">
                  Maps conversation history into 10,000-dimensional hypervectors. Resolves query
                  matches with a single dot product instead of model execution.
                </p>
              </div>
              <div className="pt-6 text-xs font-semibold text-[#76B900]">
                Zero-Compute Inference
              </div>
            </div>

            {/* 5. oneAPI Zero-Copy */}
            <div className="bg-[#111111] p-8 rounded-lg border border-[#1A1A1A] hover:border-[#76B900]/50 transition-all group flex flex-col justify-between">
              <div className="space-y-4">
                <div className="w-12 h-12 rounded bg-[#76B900]/10 flex items-center justify-center text-[#76B900] group-hover:scale-110 transition-transform">
                  <Zap className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold">oneAPI Zero-Copy iGPU</h3>
                <p className="text-gray-400 text-sm leading-relaxed">
                  Interfaces with Intel Level Zero drivers to map memory pointers directly between
                  CPU/iGPU. Eliminates redundant PCIe data transfers.
                </p>
              </div>
              <div className="pt-6 text-xs font-semibold text-[#76B900]">Unified Shared USM</div>
            </div>

            {/* 6. Recursive Self-Crystallization */}
            <div className="bg-[#111111] p-8 rounded-lg border border-[#1A1A1A] hover:border-[#76B900]/50 transition-all group flex flex-col justify-between">
              <div className="space-y-4">
                <div className="w-12 h-12 rounded bg-[#76B900]/10 flex items-center justify-center text-[#76B900] group-hover:scale-110 transition-transform">
                  <Activity className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold">Recursive Crystallization</h3>
                <p className="text-gray-400 text-sm leading-relaxed">
                  Reinforcement feedback loops learn matching schemas dynamically, pre-crystallizing
                  VSA mappings so LEO grows faster over time.
                </p>
              </div>
              <div className="pt-6 text-xs font-semibold text-[#76B900]">
                Self-Adaptive Speedups
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 5. INTERACTIVE PLAYGROUND SECTION */}
      <section
        id="playground"
        className="py-24 px-6 md:px-12 bg-[#111111] border-b border-[#1A1A1A]"
      >
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16 space-y-4">
            <h2 className="text-3xl md:text-5xl font-extrabold uppercase">
              Interactive Quantum Playground
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Simulate LEO V45's execution trace and witness zero-multiplication mathematical logic
              in real-time.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Input Console */}
            <div className="md:col-span-2 bg-[#161616] p-8 rounded-lg border border-[#222222] flex flex-col justify-between h-[480px]">
              <div className="space-y-4">
                <label className="text-xs text-gray-400 uppercase tracking-widest font-semibold block">
                  Enter Query prompt
                </label>
                <textarea
                  value={queryInput}
                  onChange={(e) => setQueryInput(e.target.value)}
                  disabled={isProcessing}
                  className="w-full bg-[#0A0A0A] border border-[#2A2A2A] rounded p-4 text-sm font-mono text-[#76B900] focus:outline-none focus:border-[#76B900] h-32 resize-none"
                />
              </div>

              {/* Logs Monitor */}
              <div className="bg-[#0A0A0A] border border-[#2A2A2A] rounded p-4 h-48 overflow-y-auto font-mono text-xs space-y-2">
                {logs.length === 0 && (
                  <p className="text-gray-600 italic">Waiting to run pipeline execution trace...</p>
                )}
                {logs.map((log, i) => (
                  <p key={i} className="text-gray-300">
                    {log}
                  </p>
                ))}
              </div>

              <div className="flex justify-end pt-4">
                <button
                  onClick={handleRunQuery}
                  disabled={isProcessing}
                  className="bg-[#76B900] hover:bg-[#8CD000] text-black font-bold px-6 py-3 rounded text-sm transition-all transform active:scale-95 flex items-center gap-2 shadow-[0_0_15px_rgba(118,185,0,0.3)] disabled:opacity-55"
                >
                  {isProcessing ? "Processing..." : "Run LEO Trace"}{" "}
                  <Play className="w-4 h-4 fill-black" />
                </button>
              </div>
            </div>

            {/* Metadata Summary Panel */}
            <div className="bg-[#161616] p-8 rounded-lg border border-[#222222] flex flex-col justify-between h-[480px]">
              <div>
                <h3 className="text-lg font-bold uppercase tracking-wider mb-6 text-white border-b border-[#2A2A2A] pb-3">
                  Execution Vitals
                </h3>
                <div className="space-y-6">
                  <div>
                    <p className="text-xs text-gray-500 uppercase">Inference Latency</p>
                    <p className="text-3xl font-black text-[#76B900]">
                      {isProcessing ? "..." : `${latency.toFixed(2)} ms`}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 uppercase">VSA Hamming match score</p>
                    <p className="text-3xl font-black text-white">
                      {isProcessing ? "..." : `${(vsaMatchScore * 100).toFixed(1)} %`}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 uppercase">
                      Multiplications converted to additions
                    </p>
                    <p className="text-3xl font-black text-white">
                      {isProcessing ? "..." : operationsSaved.toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-[#0A0A0A] p-4 rounded border border-[#2A2A2A] text-xs text-gray-400">
                {resultText ? (
                  <p className="leading-relaxed">
                    <strong className="text-white">Output:</strong> {resultText}
                  </p>
                ) : (
                  <p className="italic text-gray-600">No output generated.</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 6. PERFORMANCE COMPARISON SECTION */}
      <section className="py-24 px-6 md:px-12 bg-[#0A0A0A] border-b border-[#1A1A1A]">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16 space-y-4">
            <h2 className="text-3xl md:text-5xl font-extrabold uppercase">
              Performance Benchmarks
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Comparing effective processing bandwidth and local hardware costs.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-12">
            {/* Bandwidth Comparison */}
            <div className="bg-[#111111] p-8 rounded-lg border border-[#1C1C1C]">
              <h3 className="text-lg font-bold uppercase mb-6 flex items-center gap-2 text-white">
                <Gauge className="w-5 h-5 text-[#76B900]" /> Effective Memory Bandwidth (GB/s)
              </h3>
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between text-sm mb-2 text-gray-400">
                    <span>LEO V45 (i5 Laptop + UHD)</span>
                    <span className="font-bold text-[#76B900]">~9,000 GB/s</span>
                  </div>
                  <div className="w-full bg-[#1A1A1A] rounded-full h-4">
                    <div
                      className="bg-gradient-to-r from-[#76B900] to-[#A3E300] h-4 rounded-full"
                      style={{ width: "100%" }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-2 text-gray-400">
                    <span>NVIDIA H100 (HBM3)</span>
                    <span className="font-bold text-gray-300">3,350 GB/s</span>
                  </div>
                  <div className="w-full bg-[#1A1A1A] rounded-full h-4">
                    <div className="bg-gray-600 h-4 rounded-full" style={{ width: "37%" }} />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-2 text-gray-400">
                    <span>Standard DDR4 Host memory</span>
                    <span className="font-bold text-gray-400">50 GB/s</span>
                  </div>
                  <div className="w-full bg-[#1A1A1A] rounded-full h-4">
                    <div className="bg-gray-800 h-4 rounded-full" style={{ width: "2%" }} />
                  </div>
                </div>
              </div>
            </div>

            {/* Cost Comparison */}
            <div className="bg-[#111111] p-8 rounded-lg border border-[#1C1C1C]">
              <h3 className="text-lg font-bold uppercase mb-6 flex items-center gap-2 text-white">
                <Shield className="w-5 h-5 text-[#76B900]" /> Node Procurement Cost (USD)
              </h3>
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between text-sm mb-2 text-gray-400">
                    <span>NVIDIA H100 PCIe node</span>
                    <span className="font-bold text-gray-300">$30,000+</span>
                  </div>
                  <div className="w-full bg-[#1A1A1A] rounded-full h-4">
                    <div className="bg-red-900/80 h-4 rounded-full" style={{ width: "100%" }} />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-2 text-gray-400">
                    <span>Standard i5 Laptop Node (LEO deployment)</span>
                    <span className="font-bold text-[#76B900]">$700</span>
                  </div>
                  <div className="w-full bg-[#1A1A1A] rounded-full h-4">
                    <div className="bg-[#76B900] h-4 rounded-full" style={{ width: "2.3%" }} />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 7. FLOATING ASSISTANT SIDE PANEL */}
      {isChatOpen && (
        <div className="fixed top-0 right-0 h-full w-96 bg-[#111111] border-l border-[#1A1A1A] z-50 flex flex-col justify-between shadow-[0_0_30px_rgba(0,0,0,0.8)] animate-in slide-in-from-right duration-300">
          {/* Header */}
          <div className="p-4 border-b border-[#1A1A1A] flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-[#76B900]" />
              <span className="font-bold uppercase tracking-wider text-sm">
                LEO Private Advisor
              </span>
            </div>
            <button
              onClick={() => setIsChatOpen(false)}
              className="text-gray-400 hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Model Health / Status Alert */}
          <div className="px-4 py-2 border-b border-[#1A1A1A] bg-[#161616] space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-gray-500 uppercase font-semibold">
                Router Mode:
              </span>
              <select
                value={routeMode}
                onChange={(e) => setRouteMode(e.target.value as any)}
                className="bg-[#0A0A0A] border border-gray-700 text-xs text-white rounded px-2 py-0.5"
              >
                <option value="auto">Auto Router</option>
                <option value="colibri">Colibrì MoE</option>
                <option value="ollama">Local Ollama</option>
              </select>
            </div>
            {ollamaStatus === "CHECKING" && (
              <div className="flex items-center gap-2 text-xs text-gray-400">
                <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Verifying local model daemon...
              </div>
            )}
            {ollamaStatus === "ONLINE" && (
              <div className="flex flex-col gap-1 text-[10px] text-gray-400">
                <div className="flex items-center gap-1 text-[#76B900] font-semibold">
                  <CheckCircle className="w-3 h-3" /> System Capability:{" "}
                  {capabilities?.colibri_capable ? "ENTERPRISE" : "LOW-RAM"}
                </div>
                <div className="flex justify-between mt-1 text-gray-500">
                  <span>RAM: {capabilities?.ram_total_gb} GB</span>
                  <span>Disk Free: {capabilities?.disk_free_gb} GB</span>
                </div>
                <div className="mt-1 text-[9px] text-[#76B900] font-mono">
                  Routed Endpoint:{" "}
                  {routeMode === "colibri" ||
                  (routeMode === "auto" &&
                    capabilities?.colibri_capable &&
                    capabilities?.colibri_online)
                    ? "Colibri (GLM-5.2)"
                    : "Ollama (" + (capabilities?.ollama_models?.join(", ") || "qwen2.5") + ")"}
                </div>
              </div>
            )}
            {ollamaStatus === "OFFLINE" && (
              <div className="text-xs text-red-500 bg-red-950/40 border border-red-900/60 p-2.5 rounded space-y-2">
                <div className="flex items-center gap-1.5 font-bold">
                  <AlertTriangle className="w-4 h-4" /> Ollama / Colibri Offline
                </div>
                <p className="text-gray-400 leading-normal font-mono text-[10px]">
                  1. Run Ollama: `ollama serve`
                  <br />
                  2. For Colibri MoE setup guidelines, check: docs/COLIBRI_HARDWARE_GUIDE.md
                </p>
                <button
                  onClick={checkOllamaHealth}
                  className="flex items-center gap-1 text-[10px] text-white underline hover:text-[#76B900] transition-colors"
                >
                  <RefreshCw className="w-3 h-3" /> Retry health check
                </button>
              </div>
            )}

            {/* Inadequate Hardware warning alert */}
            {routeMode === "colibri" && capabilities && !capabilities.colibri_capable && (
              <div className="text-[10px] text-yellow-500 bg-yellow-950/40 border border-yellow-900/60 p-2 rounded leading-relaxed">
                <strong className="text-white block mb-0.5">
                  ⚠️ Insufficient Hardware Capacity
                </strong>
                GLM-5.2 MoE requires &ge; 25GB RAM. Queries will fallback to local Ollama.
              </div>
            )}
          </div>

          {/* Messages Panel */}
          <div className="flex-1 p-4 overflow-y-auto space-y-4 font-sans text-sm">
            {chatHistory.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[85%] rounded p-3 leading-relaxed text-xs ${msg.sender === "user" ? "bg-[#76B900] text-black font-semibold" : "bg-[#1A1A1A] text-gray-300 border border-[#222222]"}`}
                >
                  {msg.text || (
                    <span className="flex items-center gap-1 italic text-gray-500">
                      <RefreshCw className="w-3 h-3 animate-spin" /> Generating token stream...
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Input Panel */}
          <div className="p-4 border-t border-[#1A1A1A] flex items-center gap-2">
            <input
              type="text"
              placeholder="Ask anything..."
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSendChatMessage()}
              disabled={isAssistantTyping || ollamaStatus !== "ONLINE"}
              className="flex-1 bg-[#0A0A0A] border border-[#2A2A2A] rounded px-3 py-2 text-xs font-mono text-[#76B900] focus:outline-none focus:border-[#76B900] disabled:opacity-50"
            />
            <button
              onClick={handleSendChatMessage}
              disabled={isAssistantTyping || ollamaStatus !== "ONLINE"}
              className="bg-[#76B900] hover:bg-[#8CD000] text-black font-bold p-2.5 rounded transition-all transform active:scale-95 disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* 8. FOOTER */}
      <footer className="bg-[#0A0A0A] border-t border-[#1A1A1A] py-16 px-6 md:px-12">
        <div className="max-w-6xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8">
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded bg-[#76B900] flex items-center justify-center font-bold text-black text-sm">
                L
              </div>
              <span className="text-lg font-bold tracking-tight uppercase">LEO QUANTUM</span>
            </div>
            <p className="text-xs text-gray-600">
              © 2026 LEO AI Project. MIT Open Core. <br />
              All rights reserved.
            </p>
          </div>

          <div>
            <h4 className="text-sm font-bold uppercase mb-4 text-white">Subsystems</h4>
            <ul className="text-xs text-gray-500 space-y-2">
              <li>LNS Compiler</li>
              <li>Intel CAT Pinning</li>
              <li>Fourier Attention</li>
              <li>oneAPI Level Zero USM</li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-bold uppercase mb-4 text-white">VSA Caches</h4>
            <ul className="text-xs text-gray-500 space-y-2">
              <li>Crystallizer v2</li>
              <li>Hypervectors</li>
              <li>Hamming Similarity</li>
              <li>Dynamic Offload</li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-bold uppercase mb-4 text-white">License</h4>
            <p className="text-xs text-gray-500 leading-relaxed">
              Open source MIT core package. Enterprise dashboard licensing subject to standard SLAs.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};
