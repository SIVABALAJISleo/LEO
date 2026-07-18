import React from "react";
import { CheckCircle } from "lucide-react";

export default function Pricing() {
  const plans = [
    {
      name: "Developer Core",
      price: "$0",
      period: "forever",
      desc: "Perfect for local debugging and standalone optimizations on standard i5/i7 hardware.",
      features: [
        "Local Ollama Model integration",
        "BNN Speculative draft compiler",
        "VSA Crystallizer V2 Cache (up to 50k keys)",
        "Direct CPU and baseline Intel iGPU offloads",
        "Community Discord support"
      ]
    },
    {
      name: "Enterprise Substrate",
      price: "$299",
      period: "per node / month",
      desc: "For production scaling and frontier reasoning models under high concurrency.",
      features: [
        "Full Colibri C-Engine & GLM-5.2 execution support",
        "Intel CAT L3 pinned cache partitions",
        "Fourier Attention 2D FFT optimizations (95% coefficient pruning)",
        "oneAPI Zero-Copy Unified Shared Memory (USM) streams",
        "Unlimited VSA crystallized keys",
        "Premium SLA & direct team integrations"
      ],
      popular: true
    }
  ];

  return (
    <div className="min-h-screen bg-[#040814] py-24 px-6 relative overflow-hidden">
      {/* Glow effects */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-[#76B900]/10 rounded-full blur-[120px] pointer-events-none" />

      <div className="max-w-5xl mx-auto space-y-16 relative z-10">
        <div className="text-center space-y-4">
          <h1 className="text-4xl md:text-5xl font-black uppercase tracking-tight text-white leading-none">
            MNC-Grade GPU Competitiveness <br />
            <span className="bg-gradient-to-r from-[#76B900] to-white bg-clip-text text-transparent">
              Flexible Pricing
            </span>
          </h1>
          <p className="text-slate-400 max-w-xl mx-auto text-sm">
            Scale LEO's 6 Silicon Breakthroughs dynamically from standalone developer setups to enterprise-ready clusters.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {plans.map((plan, idx) => (
            <div 
              key={idx} 
              className={`bg-[#0b1329]/40 border rounded-2xl p-8 flex flex-col justify-between transition-all relative ${
                plan.popular 
                  ? "border-[#76B900] shadow-[0_0_30px_rgba(118,185,0,0.15)] scale-105" 
                  : "border-slate-800 hover:border-slate-700"
              }`}
            >
              {plan.popular && (
                <span className="absolute -top-3.5 left-1/2 -translate-x-1/2 bg-[#76B900] text-black font-extrabold text-[10px] uppercase tracking-widest px-3 py-1 rounded-full shadow-md">
                  Most Popular
                </span>
              )}

              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-bold text-white uppercase tracking-wider">{plan.name}</h3>
                  <p className="text-slate-500 text-xs mt-1 leading-relaxed">{plan.desc}</p>
                </div>

                <div className="flex items-baseline gap-1 text-white">
                  <span className="text-4xl font-black">{plan.price}</span>
                  <span className="text-slate-500 text-xs font-semibold">/ {plan.period}</span>
                </div>

                <ul className="space-y-3.5 border-t border-slate-800/80 pt-6">
                  {plan.features.map((feature, fIdx) => (
                    <li key={fIdx} className="flex items-start gap-2.5 text-xs text-slate-300 leading-normal">
                      <CheckCircle className="h-4 w-4 text-[#76B900] shrink-0 mt-0.5" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="pt-8">
                <button 
                  className={`w-full py-3 rounded-lg text-xs font-extrabold uppercase tracking-wider transition-all transform active:scale-[0.98] ${
                    plan.popular
                      ? "bg-[#76B900] hover:bg-[#8CD000] text-black shadow-[0_0_15px_rgba(118,185,0,0.3)]"
                      : "border border-slate-700 hover:border-slate-500 text-white bg-white/5 hover:bg-white/10"
                  }`}
                >
                  Get Started
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
