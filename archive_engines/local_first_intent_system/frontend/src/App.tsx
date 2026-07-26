import { useState, useEffect } from "react";
import { Zap, Database, RefreshCw, ShieldCheck, X, ChevronRight, Binary } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import * as Y from "yjs";
import { LocalIntentEngine } from "./engine";
import type { Node, NodeType } from "./engine";

// --- LOCAL ENGINE INSTANCE ---
const engine = new LocalIntentEngine();

// --- CRDT SYNC SIMULATION ---
const doc = new Y.Doc();
const syncState = doc.getMap("sync_state");

export default function App() {
  const [selectedBlocks, setSelectedBlocks] = useState<Node[]>([]);
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState<Node[]>([]);
  const [isPaletteOpen, setIsPaletteOpen] = useState(false);
  const [syncCount, setSyncCount] = useState(0);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Sync simulation loop
  useEffect(() => {
    const interval = setInterval(() => {
      syncState.set("last_sync", Date.now());
      setSyncCount((prev) => prev + 1);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  // Update suggestions based on current chain
  useEffect(() => {
    const typeOrder: NodeType[] = ["ENTITY", "METRIC", "TIME", "CONDITION"];
    const currentType = typeOrder[selectedBlocks.length];

    if (currentType && isPaletteOpen) {
      const prevId =
        selectedBlocks.length > 0 ? selectedBlocks[selectedBlocks.length - 1].id : undefined;
      const options = engine.getNodesByType(currentType, prevId);
      setSuggestions(options.filter((n) => n.name.toLowerCase().includes(query.toLowerCase())));
    } else {
      setSuggestions([]);
    }
  }, [selectedBlocks, query, isPaletteOpen]);

  const handleSelect = (node: Node) => {
    const newChain = [...selectedBlocks, node];
    setSelectedBlocks(newChain);
    setQuery("");

    if (newChain.length === 4) {
      executeDeterministic(newChain);
      setIsPaletteOpen(false);
    }
  };

  const executeDeterministic = (chain: Node[]) => {
    const res = engine.execute(chain.map((n) => n.id));
    if (res.status === "SUCCESS") {
      setResult(res.result);
      setError(null);
    } else {
      setError(res.error || "UNKNOWN_ERROR");
      setResult(null);
    }
  };

  const removeBlock = (index: number) => {
    setSelectedBlocks(selectedBlocks.slice(0, index));
    setResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-[#08080a] text-zinc-100 font-mono selection:bg-brand/30">
      {/* Background Grid */}
      <div className="fixed inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none" />

      <div className="relative max-w-5xl mx-auto pt-16 px-8">
        {/* Top Status Bar */}
        <div className="flex justify-between items-center mb-12 text-[10px] uppercase tracking-[0.2em] text-zinc-500">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5 text-brand">
              <Database size={10} /> Local_Engine: Active
            </span>
            <span className="flex items-center gap-1.5">
              <RefreshCw size={10} className={syncCount > 0 ? "animate-spin-slow" : ""} />
              Sync_Pulse: {syncCount % 100}
            </span>
          </div>
          <div className="flex items-center gap-1.5 text-zinc-600">
            <ShieldCheck size={10} /> Determinism_Guard: v5.2
          </div>
        </div>

        {/* Hero Section */}
        <div className="mb-12">
          <h1 className="text-3xl font-bold tracking-tight mb-2 flex items-center gap-3">
            <Binary className="text-brand" size={32} />
            INTENT_REIFICATION_CORE
          </h1>
          <p className="text-xs text-zinc-500 max-w-xl leading-relaxed">
            Local-first execution system. Zero natural language ambiguity. Meaning is aligned at the
            boundary through forced structural reification.
          </p>
        </div>

        {/* Main Intent Area */}
        <div className="bg-[#121216] border border-zinc-800 rounded-lg p-6 shadow-2xl mb-8">
          <div className="flex flex-wrap items-center gap-4 min-h-[48px]">
            <AnimatePresence>
              {selectedBlocks.map((block, i) => (
                <motion.div
                  key={block.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-center gap-2 px-3 py-1 bg-zinc-900 border border-zinc-700 rounded text-xs transition-colors hover:border-brand"
                >
                  <span className="text-zinc-600 font-bold">{block.type[0]}</span>
                  <span className="text-brand font-medium">{block.name}</span>
                  <button
                    onClick={() => removeBlock(i)}
                    className="text-zinc-700 hover:text-white ml-1"
                  >
                    <X size={12} />
                  </button>
                </motion.div>
              ))}
            </AnimatePresence>

            {selectedBlocks.length < 4 && (
              <div className="flex-grow relative">
                <input
                  value={query}
                  onChange={(e) => {
                    setQuery(e.target.value);
                    setIsPaletteOpen(true);
                  }}
                  onFocus={() => setIsPaletteOpen(true)}
                  className="w-full bg-transparent border-none outline-none text-zinc-400 placeholder:text-zinc-800 text-sm"
                  placeholder={
                    selectedBlocks.length === 0
                      ? "Identify System (Search...)"
                      : "Align Next Intent Block..."
                  }
                />

                {/* Palette */}
                <AnimatePresence>
                  {isPaletteOpen && suggestions.length > 0 && (
                    <motion.div
                      initial={{ opacity: 0, y: 5 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: 5 }}
                      className="absolute top-full left-0 mt-4 w-72 bg-[#121216] border border-zinc-800 rounded-md shadow-2xl z-50 overflow-hidden"
                    >
                      <div className="px-3 py-2 bg-zinc-900/50 text-[9px] uppercase tracking-widest text-zinc-600 border-b border-zinc-800">
                        Available Path Extensions
                      </div>
                      {suggestions.map((node) => (
                        <button
                          key={node.id}
                          onClick={() => handleSelect(node)}
                          className="w-full text-left px-4 py-3 hover:bg-brand/5 group flex items-center justify-between border-b border-zinc-800/50 last:border-none"
                        >
                          <span className="text-xs group-hover:text-brand transition-colors tracking-tight">
                            {node.name}
                          </span>
                          <ChevronRight
                            size={12}
                            className="text-zinc-800 group-hover:text-brand"
                          />
                        </button>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            )}
          </div>
        </div>

        {/* Output Diagnostics */}
        <AnimatePresence>
          {result && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="grid grid-cols-3 gap-6"
            >
              <div className="col-span-2 bg-[#0c0c0e] border border-zinc-800 rounded-lg p-8">
                <div className="flex items-center gap-3 text-brand mb-6">
                  <Zap size={18} />
                  <span className="text-xs font-bold uppercase tracking-widest">
                    Execution Result // Resolved
                  </span>
                </div>
                <div className="space-y-4">
                  <div className="text-4xl font-bold tracking-tighter text-white">
                    {result.data}
                  </div>
                  <div className="flex flex-wrap gap-4 pt-6 border-t border-zinc-900">
                    {result.trace.map((step: string, i: number) => (
                      <div key={i} className="flex items-center gap-2 text-[10px] text-zinc-500">
                        <span className="opacity-30">0{i + 1}</span> {step}
                        {i < result.trace.length - 1 && <ChevronRight size={8} />}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="bg-[#0c0c0e] border border-zinc-800 rounded-lg p-6">
                <h4 className="text-[9px] uppercase tracking-widest text-zinc-600 mb-6">
                  Local_Stats
                </h4>
                <div className="space-y-4 text-[10px]">
                  <div className="flex justify-between">
                    <span className="text-zinc-600">ID_PARITY</span>
                    <span className="text-brand">DETERMINISTIC</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-zinc-600">RESOLUTION_LATENCY</span>
                    <span className="text-zinc-400">0.042ms</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-zinc-600">SOURCE</span>
                    <span className="text-zinc-400 underline">WASM_CORE_0</span>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {error && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-6 bg-red-500/5 border border-red-500/20 rounded-lg text-red-500"
            >
              <div className="text-[10px] font-bold uppercase tracking-[0.2em] mb-2 flex items-center gap-2">
                <X size={14} /> Critical_Failure_Boundary
              </div>
              <div className="text-xs opacity-70 leading-relaxed font-mono">
                {error}: The requested intent sequence violated the deterministic graph schema. No
                reasoning recovery permitted.
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
