import React, { useState, useEffect, useRef } from "react";
import {
  Search,
  Command,
  Layers,
  Clock,
  Activity,
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
  X,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import clsx from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export default function App() {
  const [nodes, setNodes] = useState([]);
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [selectedBlocks, setSelectedBlocks] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  useEffect(() => {
    fetch("http://localhost:3001/api/nodes")
      .then((res) => res.json())
      .then((data) => setNodes(data))
      .catch((err) => console.error("Backend not running?"));
  }, []);

  useEffect(() => {
    if (query.length > 0) {
      const typeSequence = ["ENTITY", "METRIC", "TIME", "CONDITION"];
      const nextType = typeSequence[selectedBlocks.length];

      const filtered = nodes.filter(
        (n) => n.type === nextType && n.name.toLowerCase().includes(query.toLowerCase()),
      );
      setSuggestions(filtered);
    } else {
      setSuggestions([]);
    }
  }, [query, selectedBlocks, nodes]);

  const handleSelect = (node) => {
    const newBlocks = [...selectedBlocks, node];
    setSelectedBlocks(newBlocks);
    setQuery("");
    setIsOpen(false);

    if (newBlocks.length === 4) {
      resolveQuery(newBlocks);
    }
  };

  const resolveQuery = (blocks) => {
    const uuids = blocks.map((b) => b.id);
    fetch("http://localhost:3001/api/resolve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ uuids }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.status === "SUCCESS") {
          setResult(data.result);
          setError(null);
        } else {
          setError(data.message);
          setResult(null);
        }
      });
  };

  const removeBlock = (index) => {
    setSelectedBlocks(selectedBlocks.slice(0, index));
    setResult(null);
    setError(null);
  };

  const getIcon = (type) => {
    switch (type) {
      case "ENTITY":
        return <Layers size={14} />;
      case "METRIC":
        return <Activity size={14} />;
      case "TIME":
        return <Clock size={14} />;
      case "CONDITION":
        return <AlertTriangle size={14} />;
      default:
        return <Command size={14} />;
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0c] text-white font-sans selection:bg-cyan-500/30">
      <div className="max-w-4xl mx-auto pt-20 px-6">
        {/* Header */}
        <div className="flex flex-col space-y-2 mb-12">
          <h1 className="text-4xl font-bold tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
            DETERMINISTIC_QUERY_GRAPH
          </h1>
          <p className="text-zinc-500 text-sm font-medium tracking-tight">
            POST-LANGUAGE SEMANTIC SYSTEM // ZERO_AMBIGUITY_CORE
          </p>
        </div>

        {/* Intent Block Area */}
        <div className="flex flex-wrap items-center gap-3 p-4 bg-zinc-900/50 border border-zinc-800 rounded-xl mb-8 min-h-[72px]">
          <AnimatePresence>
            {selectedBlocks.map((block, i) => (
              <motion.div
                key={block.id}
                initial={{ opacity: 0, scale: 0.9, x: -10 }}
                animate={{ opacity: 1, scale: 1, x: 0 }}
                exit={{ opacity: 0, scale: 0.9, x: 10 }}
                className={cn(
                  "flex items-center gap-2 px-3 py-1.5 rounded-full border text-sm font-semibold",
                  block.type === "ENTITY" && "bg-cyan-500/10 border-cyan-500/50 text-cyan-400",
                  block.type === "METRIC" && "bg-blue-500/10 border-blue-500/50 text-blue-400",
                  block.type === "TIME" && "bg-purple-500/10 border-purple-500/50 text-purple-400",
                  block.type === "CONDITION" &&
                    "bg-amber-500/10 border-amber-500/50 text-amber-400",
                )}
              >
                {getIcon(block.type)}
                {block.name}
                <button
                  onClick={() => removeBlock(i)}
                  className="hover:text-white transition-colors"
                >
                  <X size={14} />
                </button>
              </motion.div>
            ))}
          </AnimatePresence>

          {selectedBlocks.length < 4 && (
            <div className="relative flex-grow min-w-[200px]">
              <div className="flex items-center gap-3 text-zinc-500 group">
                <Search size={18} className="group-focus-within:text-cyan-400 transition-colors" />
                <input
                  ref={inputRef}
                  value={query}
                  onChange={(e) => {
                    setQuery(e.target.value);
                    setIsOpen(true);
                  }}
                  onFocus={() => setIsOpen(true)}
                  placeholder={
                    selectedBlocks.length === 0
                      ? "Select Entity (e.g. ALPHA_NODE)..."
                      : selectedBlocks.length === 1
                        ? "Select Metric..."
                        : selectedBlocks.length === 2
                          ? "Select Time Window..."
                          : "Select Condition Severity..."
                  }
                  className="bg-transparent border-none outline-none text-sm w-full placeholder:text-zinc-700"
                />
              </div>

              {/* Suggestions Palette */}
              <AnimatePresence>
                {isOpen && suggestions.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    className="absolute top-full left-0 right-0 mt-4 bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden shadow-2xl z-50 p-2"
                  >
                    {suggestions.map((node) => (
                      <button
                        key={node.id}
                        onClick={() => handleSelect(node)}
                        className="w-full flex items-center justify-between p-3 hover:bg-zinc-800/50 rounded-lg transition-all group"
                      >
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-zinc-800 rounded-lg group-hover:bg-cyan-500/20 group-hover:text-cyan-400 transition-all">
                            {getIcon(node.type)}
                          </div>
                          <div className="flex flex-col items-start">
                            <span className="font-bold text-sm tracking-tight">{node.name}</span>
                            <span className="text-[10px] text-zinc-500 uppercase tracking-widest">
                              {node.type}
                            </span>
                          </div>
                        </div>
                        <ChevronRight
                          size={14}
                          className="text-zinc-700 group-hover:text-cyan-400"
                        />
                      </button>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}
        </div>

        {/* Results Area */}
        <AnimatePresence mode="wait">
          {result && (
            <motion.div
              layout
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="p-6 bg-cyan-500/5 border border-cyan-500/20 rounded-2xl"
            >
              <div className="flex items-center gap-2 text-cyan-400 mb-4 font-bold text-xs uppercase tracking-widest">
                <CheckCircle2 size={16} />
                Deterministic Resolution Success
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-zinc-500 text-[10px] uppercase tracking-[0.2em] mb-4">
                    Execution Trace
                  </h3>
                  <div className="flex flex-col gap-2">
                    {result.trace.map((step, i) => (
                      <div key={i} className="flex items-center gap-3 text-sm">
                        <div className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                        <span className="font-mono text-zinc-300">{step}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h3 className="text-zinc-500 text-[10px] uppercase tracking-[0.2em] mb-4">
                    Resolved Data
                  </h3>
                  <div className="text-4xl font-bold tracking-tighter mb-1">
                    {result.data.value}{" "}
                    <span className="text-lg text-zinc-500 font-normal">{result.data.unit}</span>
                  </div>
                  <p className="text-xs text-zinc-500 border-t border-zinc-800 pt-4 mt-4">
                    {result.outcome}
                  </p>
                </div>
              </div>
            </motion.div>
          )}

          {error && (
            <motion.div
              layout
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="p-6 bg-red-500/5 border border-red-500/20 rounded-2xl flex items-center gap-4 text-red-400"
            >
              <AlertTriangle size={24} />
              <div>
                <div className="font-bold text-sm uppercase tracking-wider">Validation Error</div>
                <div className="text-sm opacity-80">{error}</div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
