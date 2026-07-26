import React, { useState, useEffect } from "react";
import { Search, Tag, Info, AlertCircle, ShieldCheck } from "lucide-react";

interface Property {
  property_name: string;
  data_type: string;
  unit?: string;
  domain_tag: string;
  description: string;
}

export const DynamicSchemaPanel = () => {
  const [properties, setProperties] = useState<any[]>([]);
  const [search, setSearch] = useState("");

  // Mock fetching from global_registry (In a real app, this would be an API call)
  useEffect(() => {
    setProperties([
      { property_name: "revenue", data_type: "float", unit: "USD", domain_tag: "finance" },
      { property_name: "expense", data_type: "float", unit: "USD", domain_tag: "finance" },
      { property_name: "conversion_rate", data_type: "float", unit: "%", domain_tag: "marketing" },
      { property_name: "temperature", data_type: "float", unit: "°C", domain_tag: "iot" },
      { property_name: "user_id", data_type: "string", domain_tag: "identity" },
      { property_name: "timestamp", data_type: "datetime", domain_tag: "core" },
    ]);
  }, []);

  const filtered = properties.filter(
    (p) =>
      p.property_name.toLowerCase().includes(search.toLowerCase()) ||
      p.domain_tag.toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <div className="flex flex-col h-full bg-slate-900 border-r border-slate-700 w-72 text-white">
      <div className="p-4 border-b border-slate-700 bg-slate-950/50">
        <div className="flex items-center gap-2 mb-4">
          <ShieldCheck className="text-emerald-400" size={20} />
          <h2 className="font-bold text-sm uppercase tracking-tighter text-emerald-400">
            Global Ontology
          </h2>
        </div>
        <div className="relative">
          <Search className="absolute left-2 top-2.5 text-slate-500" size={14} />
          <input
            type="text"
            placeholder="Search properties..."
            className="w-full bg-slate-800 border border-slate-700 rounded-md py-1.5 pl-8 pr-2 text-xs focus:ring-1 focus:ring-blue-500 outline-none transition-all"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-1 custom-scrollbar">
        {filtered.map((prop) => (
          <div
            key={prop.property_name}
            draggable
            onDragStart={(e) => e.dataTransfer.setData("uod_property", JSON.stringify(prop))}
            className="group p-2 rounded-md hover:bg-slate-800 border border-transparent hover:border-slate-700 cursor-grab active:cursor-grabbing transition-all"
          >
            <div className="flex items-center justify-between mb-1">
              <span className="font-mono text-[11px] font-bold text-blue-400">
                {prop.property_name}
              </span>
              <span className="text-[9px] bg-slate-700 px-1.5 py-0.5 rounded text-slate-300 uppercase">
                {prop.data_type}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[9px] text-slate-500 flex items-center gap-1">
                <Tag size={10} /> {prop.domain_tag}
              </span>
              {prop.unit && (
                <span className="text-[9px] text-amber-500/80 font-bold">[{prop.unit}]</span>
              )}
            </div>
          </div>
        ))}
        {filtered.length === 0 && (
          <div className="p-8 text-center">
            <AlertCircle className="mx-auto mb-2 text-slate-600" size={24} />
            <p className="text-xs text-slate-500">No properties found.</p>
          </div>
        )}
      </div>

      <div className="p-4 bg-slate-950/30 text-[10px] text-slate-500 border-t border-slate-800/50">
        <div className="flex items-center gap-2 mb-1 text-slate-400 font-bold uppercase tracking-widest leading-none">
          <Info size={10} /> Governance
        </div>
        v1.2.4 Deployment | 248 Total Properties
      </div>
    </div>
  );
};
