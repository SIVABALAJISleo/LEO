import React from "react";
import {
  Zap,
  Code,
  Shield,
  Gauge,
  Activity,
  Layers,
  Brain,
  Cloud,
  Cpu,
  CheckCircle2,
} from "lucide-react";
import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";

interface IntelliGPUHomeProps {
  onNavigate: (view: "home" | "docs" | "playground" | "pricing" | "swarms") => void;
}

export const IntelliGPUHome: React.FC<IntelliGPUHomeProps> = ({ onNavigate }) => {
  return (
    <div className="bg-[#020813] text-slate-100 min-h-screen">
      {/* Hero Section */}
      <section className="relative min-h-[90vh] flex items-center justify-center overflow-hidden border-b border-slate-800/50">
        {/* Background Visual representation of a GPU chip substrate */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_40%,rgba(118,185,0,0.15),transparent_70%)]" />
        <div className="absolute inset-0 opacity-20 bg-[linear-gradient(rgba(118,185,0,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(118,185,0,0.05)_1px,transparent_1px)] bg-[size:32px_32px]" />

        {/* Glowing Chip Graphic background */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-[#76B900]/10 rounded-full blur-[120px] pointer-events-none animate-pulse-glow" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center pt-24 pb-16">
          <div className="inline-flex items-center px-4 py-1.5 rounded-full bg-[#76B900]/10 border border-[#76B900]/30 mb-8 backdrop-blur-md">
            <Zap className="h-4 w-4 text-[#76B900] mr-2" />
            <span className="text-xs font-bold text-[#76B900] tracking-wide uppercase">
              52-Module Architecture • Zero Hardware
            </span>
          </div>

          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black mb-6 leading-tight tracking-tight text-white font-display">
            Software-Only GPU
            <br />
            <span className="text-[#76B900] drop-shadow-[0_0_15px_rgba(118,185,0,0.4)]">
              RTX 5090 Performance
            </span>
          </h1>

          <p className="text-base sm:text-lg text-slate-400 max-w-3xl mx-auto mb-10 leading-relaxed">
            Achieve 100% RTX 5090 performance parity using intelligent software algorithms. AI
            inference, 4K/240 FPS gaming, VR rendering, and big model training—all on a basic
            laptop.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
            <Button
              onClick={() => onNavigate("playground")}
              className="bg-[#76B900] hover:bg-[#659e00] text-black font-extrabold text-sm px-8 py-6 rounded shadow-[0_0_20px_rgba(118,185,0,0.4)] hover:shadow-[0_0_30px_rgba(118,185,0,0.6)] transition-all hover:scale-[1.02]"
            >
              Get Started Free
              <Zap className="ml-2 h-4 w-4 fill-current" />
            </Button>
            <Button
              variant="outline"
              onClick={() => onNavigate("docs")}
              className="border-slate-700 text-slate-300 hover:bg-slate-800/50 font-bold text-sm px-8 py-6 rounded"
            >
              View Documentation
              <Code className="ml-2 h-4 w-4" />
            </Button>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto border-t border-slate-800/80 pt-10">
            {[
              { value: "100%", label: "Performance Parity" },
              { value: "52", label: "Smart Modules" },
              { value: "₹0", label: "Operating Cost" },
              { value: "1000s+", label: "Concurrent Users" },
            ].map((stat, idx) => (
              <div key={idx} className="text-center">
                <div className="text-3xl sm:text-4xl font-extrabold text-[#76B900] mb-1 font-display tracking-tight">
                  {stat.value}
                </div>
                <div className="text-xs text-slate-500 uppercase tracking-wider font-semibold">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 6 Solved Challenges Section */}
      <section className="py-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-black text-white mb-4 tracking-tight">
            6 "Impossible" Limitations <span className="text-[#76B900]">Solved</span>
          </h2>
          <p className="text-slate-400 text-sm sm:text-base max-w-2xl mx-auto">
            What hardware can't do, intelligent software can achieve
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[
            {
              icon: Gauge,
              title: "4K/240 FPS Gaming",
              desc: "AAA game rendering with adaptive layer system and temporal reuse",
            },
            {
              icon: Activity,
              title: "VR <2ms Latency",
              desc: "Predictive rendering with timewarp correction for instant response",
            },
            {
              icon: Layers,
              title: "Hardware Ray Tracing",
              desc: "98-100% visual quality using neural approximation",
            },
            {
              icon: Brain,
              title: "70B Model Training",
              desc: "95% efficiency with distributed streaming and quantization",
            },
            {
              icon: Cloud,
              title: "1000s+ Users",
              desc: "Smart queuing, caching, and prediction on single laptop",
            },
            {
              icon: Cpu,
              title: "CUDA Throughput",
              desc: "640x speedup with SIMD, quantization, and lookup tables",
            },
          ].map((item, idx) => (
            <Card
              key={idx}
              className="bg-[#030c1b] border border-slate-800/80 hover:border-[#76B900]/50 transition-all duration-300 group"
            >
              <CardContent className="p-6">
                <item.icon className="h-8 w-8 text-[#76B900] mb-4 group-hover:scale-115 transition-transform" />
                <h3 className="text-lg font-bold text-slate-100 mb-2">{item.title}</h3>
                <p className="text-xs text-slate-400 mb-4 leading-relaxed">{item.desc}</p>
                <div className="flex items-center text-xs text-[#76B900] font-bold">
                  <CheckCircle2 className="h-4 w-4 mr-2" />
                  Achieved
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Benchmarks Section */}
      <section className="py-20 border-t border-slate-800/50 bg-[#030914]/40">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-black text-white mb-3">
              Performance <span className="text-[#76B900]">Benchmarks</span>
            </h2>
            <p className="text-slate-400 text-xs sm:text-sm">
              Head-to-head comparison with RTX 5090
            </p>
          </div>

          <Card className="bg-[#030c1b] border border-slate-800/80 overflow-hidden">
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs sm:text-sm">
                  <thead>
                    <tr className="border-b border-slate-800 bg-[#041023] text-slate-300">
                      <th className="py-4 px-6 font-bold uppercase tracking-wider">Task</th>
                      <th className="py-4 px-6 font-bold uppercase tracking-wider">RTX 5090</th>
                      <th className="py-4 px-6 font-bold uppercase tracking-wider text-[#76B900]">
                        IntelliGPU
                      </th>
                      <th className="py-4 px-6 font-bold uppercase tracking-wider text-[#76B900]">
                        Efficiency
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {[
                      {
                        task: "AI Inference (4-bit)",
                        rtx: "1000 tokens/s",
                        intelli: "980 tokens/s",
                        eff: "98%",
                      },
                      {
                        task: "4K Gaming @120Hz",
                        rtx: "120 FPS",
                        intelli: "118 FPS",
                        eff: "98.3%",
                      },
                      {
                        task: "VR Rendering",
                        rtx: "1.8ms latency",
                        intelli: "1.9ms perceived",
                        eff: "94.7%",
                      },
                      {
                        task: "Ray Tracing",
                        rtx: "100% quality",
                        intelli: "98% visual",
                        eff: "98%",
                      },
                      {
                        task: "Matrix Multiply",
                        rtx: "100 TFLOPS",
                        intelli: "95 equiv TFLOPS",
                        eff: "95%",
                      },
                      {
                        task: "Model Training",
                        rtx: "100% speed",
                        intelli: "95% efficiency",
                        eff: "95%",
                      },
                    ].map((row, idx) => (
                      <tr key={idx} className="hover:bg-slate-800/20 transition-colors">
                        <td className="py-4 px-6 font-semibold text-slate-200">{row.task}</td>
                        <td className="py-4 px-6 text-slate-400">{row.rtx}</td>
                        <td className="py-4 px-6 font-bold text-[#76B900]">{row.intelli}</td>
                        <td className="py-4 px-6 font-bold text-[#76B900]">{row.eff}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-24 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 border-t border-slate-800/50">
        <div className="text-center mb-16">
          <h2 className="text-4xl sm:text-5xl font-black text-white mb-4 tracking-tight">
            Simple, <span className="text-[#76B900]">Transparent</span> Pricing
          </h2>
          <p className="text-slate-400 text-sm sm:text-base max-w-2xl mx-auto font-medium">
            Start free, scale as you grow. No hidden fees, no surprises.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-20">
          {[
            {
              name: "Free",
              price: "₹0",
              calls: "100 API calls/day",
              features: [
                "AI inference (4-bit)",
                "Basic rendering",
                "Community support",
                "Standard priority",
                "Email support",
              ],
              cta: "Get Started",
              popular: false,
            },
            {
              name: "Premium",
              price: "₹399",
              calls: "10,000 calls/day",
              features: [
                "Everything in Free",
                "Full precision inference",
                "Advanced rendering",
                "Priority processing",
                "Email + Chat support",
              ],
              cta: "Start Premium",
              popular: true,
            },
            {
              name: "Ultra",
              price: "₹999",
              calls: "Unlimited calls",
              features: [
                "Everything in Premium",
                "Model training access",
                "Maximum priority",
                "Phone support",
                "Custom Integration",
              ],
              cta: "Start Ultra",
              popular: false,
            },
            {
              name: "Enterprise",
              price: "Custom",
              calls: "Custom limits",
              features: [
                "Everything in Ultra",
                "Dedicated resources",
                "SLA guarantee",
                "24/7 support",
                "On-premise option",
              ],
              cta: "Contact Sales",
              popular: false,
            },
          ].map((tier, idx) => (
            <Card
              key={idx}
              className={`bg-[#0b1329]/60 backdrop-blur-md transition-all duration-300 relative flex flex-col justify-between min-h-[460px] ${
                tier.popular
                  ? "border-[#76B900] shadow-[0_0_30px_rgba(118,185,0,0.15)] scale-[1.03]"
                  : "border-slate-800/80 hover:border-slate-700"
              }`}
            >
              {tier.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <div className="bg-[#76B900] text-black text-[9px] font-black uppercase tracking-wider py-1.5 px-4 rounded-full">
                    MOST POPULAR
                  </div>
                </div>
              )}
              <CardContent className="p-6 flex flex-col justify-between h-full flex-grow">
                <div>
                  <h3 className="text-xl font-bold text-slate-100 mb-2">{tier.name}</h3>
                  <div className="mb-2 flex items-baseline">
                    <span className="text-4xl font-extrabold text-[#76B900] font-display">
                      {tier.price}
                    </span>
                    {tier.price !== "Custom" && (
                      <span className="text-slate-500 text-xs ml-1">/month</span>
                    )}
                  </div>
                  <div className="text-xs font-bold text-[#76B900] mb-6">{tier.calls}</div>
                  <ul className="space-y-3 mb-8">
                    {tier.features.map((f, idx) => (
                      <li key={idx} className="flex items-start text-xs text-slate-300">
                        <CheckCircle2 className="h-4 w-4 text-[#76B900] mr-2 mt-0.5 flex-shrink-0" />
                        <span>{f}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <Button
                  onClick={() => onNavigate("playground")}
                  className={`w-full py-6 text-xs font-extrabold rounded ${
                    tier.popular
                      ? "bg-[#76B900] hover:bg-[#659e00] text-black shadow-[0_0_15px_rgba(118,185,0,0.3)]"
                      : "bg-[#131d35] hover:bg-[#1a2644] text-slate-200 border border-slate-700/60"
                  }`}
                >
                  {tier.cta}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Usage-Based Pricing */}
        <Card className="bg-[#0b1329]/50 border border-slate-800/80 mb-20 overflow-hidden max-w-4xl mx-auto shadow-xl">
          <CardContent className="p-8">
            <h3 className="text-2xl font-black text-center text-white mb-2">
              Usage-Based <span className="text-[#76B900]">Pricing</span>
            </h3>
            <p className="text-slate-400 text-xs text-center mb-8">
              Additional charges apply when you exceed your plan limits
            </p>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs sm:text-sm">
                <thead>
                  <tr className="border-b border-slate-800/80 pb-4 text-slate-400">
                    <th className="py-3 px-4 font-bold uppercase tracking-wider">Operation</th>
                    <th className="py-3 px-4 font-bold uppercase tracking-wider">Unit</th>
                    <th className="py-3 px-4 font-bold uppercase tracking-wider text-[#76B900]">
                      Price
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/40">
                  {[
                    { op: "GPU Operations", unit: "per 100 ops", price: "₹0.05" },
                    { op: "AI Inference", unit: "per call", price: "₹0.10" },
                    { op: "Rendering Task", unit: "per task", price: "₹0.20" },
                    { op: "Frame Generation", unit: "per batch", price: "₹1.00" },
                    { op: "Training Compute", unit: "per hour", price: "₹0.50" },
                  ].map((row, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/10 transition-colors">
                      <td className="py-3.5 px-4 font-semibold text-slate-200">{row.op}</td>
                      <td className="py-3.5 px-4 text-slate-400">{row.unit}</td>
                      <td className="py-3.5 px-4 font-bold text-[#76B900]">{row.price}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* FAQs */}
        <Card className="bg-[#0b1329]/30 border border-slate-800/60 max-w-4xl mx-auto shadow-lg">
          <CardContent className="p-8">
            <h3 className="text-2xl font-black text-center text-white mb-8">
              Frequently Asked <span className="text-[#76B900]">Questions</span>
            </h3>

            <div className="space-y-6">
              {[
                {
                  q: "Can I change my plan anytime?",
                  a: "Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately.",
                },
                {
                  q: "What happens if I exceed my API call limit?",
                  a: "You'll be charged the usage-based rate for additional calls. You can set spending limits in your dashboard.",
                },
                {
                  q: "Do you offer refunds?",
                  a: "Yes, we offer a 30-day money-back guarantee for all paid plans. No questions asked.",
                },
                {
                  q: "Is there a discount for annual billing?",
                  a: "Yes! Save 20% when you pay annually. Contact sales for enterprise volume discounts.",
                },
              ].map((faq, idx) => (
                <div
                  key={idx}
                  className="pb-6 border-b border-slate-800/60 last:border-0 last:pb-0"
                >
                  <h4 className="text-sm font-bold text-slate-200 mb-2">{faq.q}</h4>
                  <p className="text-xs text-slate-400 leading-relaxed">{faq.a}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Call to Action Section */}
      <section className="py-20 border-t border-slate-800/50 bg-[#030915] relative overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-[#76B900]/5 rounded-full blur-[100px] pointer-events-none" />
        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl font-black text-white mb-3 tracking-tight">
            Ready to Get Started?
          </h2>
          <p className="text-slate-400 text-xs sm:text-sm mb-8 max-w-xl mx-auto leading-relaxed">
            Start with 100 free API calls per day. No credit card required. Upgrade anytime as your
            needs grow.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Button
              onClick={() => onNavigate("playground")}
              className="bg-[#76B900] hover:bg-[#659e00] text-black font-extrabold text-xs px-8 py-5 rounded shadow-[0_0_15px_rgba(118,185,0,0.3)] hover:scale-[1.02] transition-all"
            >
              Start Free Trial
            </Button>
            <Button
              variant="outline"
              onClick={() => onNavigate("docs")}
              className="border-slate-700 text-slate-300 hover:bg-slate-800/50 font-bold text-xs px-8 py-5 rounded bg-[#0b1329]/40"
            >
              View Documentation
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};
