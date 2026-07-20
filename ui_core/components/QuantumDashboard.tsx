import React, { useState, useEffect } from 'react';
import { nvidiaTokens } from '../design_system/nvidiaTokens';
import { QuantumButton } from './QuantumButton';
import { Cpu, Database, Activity, Shield, Zap, RefreshCw, BarChart2, Layers, Server } from 'lucide-react';

export const QuantumDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState({
    computeAvoided: '99.3%',
    wattsSaved: '490 kW',
    cacheLatency: '2.3 ms',
    activeEntities: '52,410',
    totalRequests: '1,720,490',
  });

  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setMetrics((prev) => ({
        ...prev,
        totalRequests: (parseInt(prev.totalRequests.replace(/,/g, '')) + 15).toLocaleString(),
      }));
      setIsRefreshing(false);
    }, 600);
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        background: nvidiaTokens.colors.primary.black,
        color: nvidiaTokens.colors.primary.white,
        fontFamily: nvidiaTokens.typography.fontFamily.primary,
      }}
      className="p-6 md:p-10 space-y-8"
    >
      {/* Top Bar Header */}
      <header className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-white/10 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <span
              className="text-2xl font-black uppercase tracking-widest"
              style={{ color: nvidiaTokens.colors.accent.nvidiaGreen }}
            >
              LEO AI
            </span>
            <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono font-bold">
              QUANTUM V∞ ENGINE
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Local-first MNC-Grade Inference Runtime · Intel CPU + iGPU Parity
          </p>
        </div>

        <div className="flex items-center gap-3">
          <QuantumButton variant="secondary" size="small" onClick={handleRefresh} disabled={isRefreshing}>
            <RefreshCw className={`h-3.5 w-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
            Refresh Telemetry
          </QuantumButton>
          <QuantumButton variant="primary" size="small">
            + Deploy Pipeline
          </QuantumButton>
        </div>
      </header>

      {/* Hero Glassmorphic Panel */}
      <section
        style={{
          background: 'linear-gradient(135deg, rgba(10,10,10,0.95) 0%, rgba(26,26,26,0.8) 100%)',
          border: '1px solid rgba(118, 185, 0, 0.2)',
          boxShadow: '0 20px 40px rgba(0,0,0,0.6)',
        }}
        className="relative rounded-xl p-8 overflow-hidden backdrop-blur-md"
      >
        <div
          style={{
            background: nvidiaTokens.colors.gradients.glow,
          }}
          className="absolute inset-0 pointer-events-none"
        />
        <div className="relative z-10 space-y-4 max-w-3xl">
          <span className="text-xs font-mono font-bold tracking-widest text-[#76b900] uppercase">
            // Zero-Hardware GPU Emulation Layer
          </span>
          <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight">
            Full-power AI on <span style={{ color: nvidiaTokens.colors.accent.nvidiaGreen }}>commodity hardware.</span>
          </h1>
          <p className="text-sm md:text-base text-slate-300 leading-relaxed font-normal">
            Bypassing traditional GPU walls through software-first intelligence. 99.3% compute avoided via
            semantic caching, topological hypergraph reasoning, and vectorized ternary execution.
          </p>
        </div>
      </section>

      {/* Stats Counter Strip */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Compute Avoided', value: metrics.computeAvoided, icon: Zap },
          { label: 'GPU Watts Saved', value: metrics.wattsSaved, icon: Activity },
          { label: 'Cache Latency', value: metrics.cacheLatency, icon: Cpu },
          { label: 'Total Served', value: metrics.totalRequests, icon: Server },
        ].map((stat, idx) => {
          const Icon = stat.icon;
          return (
            <div
              key={idx}
              style={{
                background: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
              }}
              className="p-5 rounded-lg space-y-2 hover:border-[#76b900]/40 transition-all duration-300"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400 font-mono font-semibold uppercase tracking-wider">
                  {stat.label}
                </span>
                <Icon className="h-4 w-4 text-[#76b900]" />
              </div>
              <div className="text-2xl font-black text-white font-mono tracking-tight">{stat.value}</div>
            </div>
          );
        })}
      </div>

      {/* Main Feature Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          {
            title: 'Topological Hypergraph',
            description: '50K+ entities with 120K+ multi-hop interference relationships for instant 2.3ms context synthesis.',
            icon: Database,
            badge: 'GraphRAG Core',
          },
          {
            title: 'Adaptive Model Cascade',
            description: 'Dynamic TF-IDF & VSA routing bypassing heavy LLM inference for 99%+ of queries.',
            icon: Layers,
            badge: 'MoE Router',
          },
          {
            title: 'Zero-Hardware iGPU Runtime',
            description: 'OneAPI Zero-Copy memory pinning & BitNet 1.58-bit SIMD acceleration on Intel Iris Xe.',
            icon: Shield,
            badge: 'OpenVINO SIMD',
          },
        ].map((card, idx) => {
          const Icon = card.icon;
          return (
            <div
              key={idx}
              style={{
                background: 'linear-gradient(135deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 100%)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
              }}
              className="p-6 rounded-xl space-y-4 hover:border-[#76b900]/50 hover:-translate-y-1 transition-all duration-300 shadow-xl"
            >
              <div className="flex items-center justify-between">
                <Icon className="h-6 w-6 text-[#76b900]" />
                <span className="text-[10px] font-mono font-extrabold uppercase px-2 py-0.5 rounded bg-[#76b900]/10 text-[#76b900] border border-[#76b900]/20">
                  {card.badge}
                </span>
              </div>
              <h3 className="text-lg font-bold text-white">{card.title}</h3>
              <p className="text-xs text-slate-400 leading-relaxed font-normal">{card.description}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
};
