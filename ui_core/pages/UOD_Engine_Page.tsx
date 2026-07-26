import React from "react";
import { NodeGraph } from "../components/uod/NodeGraph";
import { DynamicSchemaPanel } from "../components/uod/DynamicSchemaPanel";
import { Network, Terminal, Settings, Share2, Layers } from "lucide-react";

const UOD_Engine_Page = () => {
  return (
    <div className="flex flex-col h-screen w-full bg-slate-950 overflow-hidden font-sans">
      {/* Header */}
      <header className="h-14 border-b border-slate-800 flex items-center justify-between px-4 bg-slate-950/80 backdrop-blur-md z-10">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600/20 p-1.5 rounded-lg border border-blue-500/30">
            <Layers className="text-blue-500" size={18} />
          </div>
          <div>
            <h1 className="text-sm font-bold text-slate-100 uppercase tracking-widest leading-none mb-1">
              Universal Ontology Engine
            </h1>
            <p className="text-[10px] text-slate-500 font-mono tracking-tighter">
              DETERMINISTIC ALGEBRAIC DATAFLOW | AUTH: SYSTEM_ARCHITECT
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex px-3 py-1 bg-slate-900 rounded-full border border-slate-800 items-center gap-2 mr-4">
            <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
            <span className="text-[10px] text-emerald-500 font-bold uppercase tracking-wider">
              DuckDB WASM ACTIVE
            </span>
          </div>
          <button className="p-2 text-slate-400 hover:text-white transition-colors">
            <Share2 size={16} />
          </button>
          <button className="p-2 text-slate-400 hover:text-white transition-colors">
            <Settings size={16} />
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex flex-1 overflow-hidden">
        {/* Left Side: Sidebar */}
        <DynamicSchemaPanel />

        {/* Center: Node Graph */}
        <div className="flex-1 relative">
          <NodeGraph />
        </div>

        {/* Bottom / Right Floating: Console or Info (Optional) */}
        <div className="absolute bottom-6 right-6 flex flex-col gap-2 pointer-events-none">
          <div className="bg-slate-900/80 backdrop-blur-md border border-slate-700 p-3 rounded-lg shadow-2xl pointer-events-auto min-w-[200px]">
            <div className="flex items-center gap-2 text-blue-400 font-bold text-[10px] uppercase tracking-widest mb-2">
              <Terminal size={12} /> System Log
            </div>
            <div className="font-mono text-[9px] text-slate-400 space-y-1">
              <div className="text-emerald-500/80">[INFO] Loaded global_registry v1.2</div>
              <div>[INFO] DuckDB mounted in RAM</div>
              <div>[WAIT] Awaiting Node Execution...</div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer Info bar */}
      <footer className="h-6 bg-blue-600 text-white flex items-center px-3 justify-between text-[9px] font-bold uppercase tracking-widest">
        <span>MODE: ALGEBRAIC_TRANSFORMATION</span>
        <div className="flex gap-4">
          <span>LATENCY: 0.12ms</span>
          <span>MEMORY: 124MB</span>
          <span>STABILITY: 100%</span>
        </div>
      </footer>
    </div>
  );
};

export default UOD_Engine_Page;
