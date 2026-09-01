import React, { useState } from "react";
import {
  NVIDIA_GPU_DATABASE,
  HOST_HARDWARE,
  calculateGpuComparison,
  type NvidiaGpuSpec,
} from "@/lib/nvidia-gpu-database";
import {
  Search,
  Sliders,
  Zap,
  ShieldCheck,
  Flame,
  ArrowUpDown,
  Download,
  Info,
  Server,
  Layers,
  Sparkles,
  CheckCircle2,
} from "lucide-react";

export function NvidiaGpuMatrix() {
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedClass, setSelectedClass] = useState<string>("ALL");
  const [selectedEra, setSelectedEra] = useState<string>("ALL");
  const [breakthroughMode, setBreakthroughMode] = useState<boolean>(true);
  const [sortField, setSortField] = useState<keyof NvidiaGpuSpec>("year");
  const [sortAsc, setSortAsc] = useState<boolean>(false);

  const eras = [
    { id: "ALL", label: "All Eras (1995–2025)" },
    { id: "PRE_CUDA", label: "Pre-CUDA (1995–2005)" },
    { id: "CUDA_ERA", label: "CUDA / Fermi / Kepler (2006–2015)" },
    { id: "PASCAL_TURING", label: "Pascal / Volta / Turing (2016–2019)" },
    { id: "AMPERE_ADA", label: "Ampere / Ada / Hopper (2020–2023)" },
    { id: "BLACKWELL", label: "Blackwell Era (2024–2025)" },
  ];

  const filteredGpus = NVIDIA_GPU_DATABASE.filter((gpu) => {
    const matchesClass = selectedClass === "ALL" || gpu.marketClass === selectedClass;
    let matchesEra = true;
    if (selectedEra === "PRE_CUDA") matchesEra = gpu.year <= 2005;
    else if (selectedEra === "CUDA_ERA") matchesEra = gpu.year >= 2006 && gpu.year <= 2015;
    else if (selectedEra === "PASCAL_TURING") matchesEra = gpu.year >= 2016 && gpu.year <= 2019;
    else if (selectedEra === "AMPERE_ADA") matchesEra = gpu.year >= 2020 && gpu.year <= 2023;
    else if (selectedEra === "BLACKWELL") matchesEra = gpu.year >= 2024;

    const matchesSearch =
      gpu.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      gpu.architecture.toLowerCase().includes(searchQuery.toLowerCase()) ||
      gpu.keyInnovation.toLowerCase().includes(searchQuery.toLowerCase());

    return matchesClass && matchesEra && matchesSearch;
  });

  const sortedGpus = [...filteredGpus].sort((a, b) => {
    const valA = a[sortField];
    const valB = b[sortField];
    if (typeof valA === "number" && typeof valB === "number") {
      return sortAsc ? valA - valB : valB - valA;
    }
    return sortAsc
      ? String(valA).localeCompare(String(valB))
      : String(valB).localeCompare(String(valA));
  });

  const handleSort = (field: keyof NvidiaGpuSpec) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false);
    }
  };

  const handleExportCsv = () => {
    const headers =
      "ID,Name,Architecture,Year,Class,FP32_GFLOPS,Memory_BW_GBs,VRAM_GB,CUDA_Cores,TDP_Watts,Raw_Silicon_Parity_Pct,Contract_Parity_Pct\n";
    const rows = sortedGpus
      .map((gpu) => {
        const comp = calculateGpuComparison(gpu, HOST_HARDWARE, breakthroughMode);
        return `"${gpu.id}","${gpu.name}","${gpu.architecture}",${gpu.year},"${gpu.marketClass}",${gpu.fp32Gflops},${gpu.memoryBandwidthGBs},${gpu.vramGB},${gpu.cudaCores},${gpu.tdpWatts},"${comp.rawSiliconParityPct}%","${comp.contractParityPct}%"`;
      })
      .join("\n");

    const blob = new Blob([headers + rows], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `NVIDIA_GPU_MATRIX_1995_2025.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  return (
    <div className="space-y-6 font-mono text-xs">
      {/* Header & Controls */}
      <div className="rounded-xl border border-cyan-500/30 bg-black/80 p-6 backdrop-blur space-y-5">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-cyan-400 font-bold text-xs uppercase tracking-wider">
              <Server className="h-4 w-4" /> Full Historical Spectrum (1995–2025)
            </div>
            <h2 className="text-xl md:text-2xl font-bold font-sans text-foreground mt-1">
              NVIDIA GPU Historical Comparison Matrix
            </h2>
            <p className="text-muted-foreground text-xs font-sans mt-1">
              Evaluating 30 years of GPU architectures against the Intel Core i5-12450H host
              baseline.
            </p>
          </div>

          {/* Mode Switcher */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 bg-zinc-950 border border-border/80 p-1.5 rounded-lg">
              <button
                onClick={() => setBreakthroughMode(false)}
                className={`px-3 py-1.5 rounded text-xs font-bold transition-all ${
                  !breakthroughMode
                    ? "bg-red-500/20 text-red-400 border border-red-500/40"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Raw Silicon Deficit
              </button>
              <button
                onClick={() => setBreakthroughMode(true)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-bold transition-all ${
                  breakthroughMode
                    ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-[0_0_15px_rgba(0,240,255,0.2)]"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                <Sparkles className="h-3.5 w-3.5 text-cyan-400" />
                Breakthrough Contract Parity
              </button>
            </div>

            <button
              onClick={handleExportCsv}
              className="flex items-center gap-1.5 bg-zinc-900 border border-border/80 hover:bg-zinc-800 px-3 py-2 rounded-lg text-muted-foreground hover:text-foreground"
            >
              <Download className="h-3.5 w-3.5" /> CSV
            </button>
          </div>
        </div>

        {/* Filters and Search Bar */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2 border-t border-border/40">
          <div className="relative">
            <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search chip name, architecture, innovation..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-zinc-950 border border-border/80 rounded-lg pl-9 pr-3 py-2 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-cyan-500/50"
            />
          </div>

          <div className="flex items-center gap-1 bg-zinc-950 border border-border/80 p-1 rounded-lg">
            {["ALL", "Consumer", "Workstation", "Datacenter"].map((cls) => (
              <button
                key={cls}
                onClick={() => setSelectedClass(cls)}
                className={`flex-1 py-1.5 rounded text-[11px] transition-colors ${
                  selectedClass === cls
                    ? "bg-zinc-800 text-foreground font-bold"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {cls}
              </button>
            ))}
          </div>

          <select
            value={selectedEra}
            onChange={(e) => setSelectedEra(e.target.value)}
            className="bg-zinc-950 border border-border/80 rounded-lg px-3 py-2 text-xs text-foreground focus:outline-none focus:border-cyan-500/50 font-mono"
          >
            {eras.map((era) => (
              <option key={era.id} value={era.id}>
                {era.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Host Hardware Profile Banner */}
      <div className="rounded-lg border border-border/60 bg-zinc-950 p-4 grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
        <div>
          <span className="text-[10px] text-muted-foreground uppercase">Host CPU</span>
          <p className="font-bold text-foreground">{HOST_HARDWARE.cpuName}</p>
        </div>
        <div>
          <span className="text-[10px] text-muted-foreground uppercase">Integrated iGPU</span>
          <p className="font-bold text-foreground">
            {HOST_HARDWARE.igpuName} ({HOST_HARDWARE.fp32Gflops} GFLOPS)
          </p>
        </div>
        <div>
          <span className="text-[10px] text-muted-foreground uppercase">System Memory</span>
          <p className="font-bold text-cyan-400">
            {HOST_HARDWARE.ramGB} GB DDR5 ({HOST_HARDWARE.memoryBandwidthGBs} GB/s)
          </p>
        </div>
        <div>
          <span className="text-[10px] text-muted-foreground uppercase">
            Fixed-Function Acceleration
          </span>
          <p className="font-bold text-emerald-400">QuickSync QSV + GNA 3.0</p>
        </div>
      </div>

      {/* Interactive GPU Table */}
      <div className="rounded-xl border border-border/60 bg-black/90 overflow-hidden backdrop-blur">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-border/60 bg-zinc-950 text-[11px] uppercase text-muted-foreground font-bold">
                <th
                  onClick={() => handleSort("name")}
                  className="p-3.5 cursor-pointer hover:text-foreground"
                >
                  GPU Model <ArrowUpDown className="inline h-3 w-3 ml-1" />
                </th>
                <th
                  onClick={() => handleSort("architecture")}
                  className="p-3.5 cursor-pointer hover:text-foreground"
                >
                  Architecture
                </th>
                <th
                  onClick={() => handleSort("year")}
                  className="p-3.5 cursor-pointer hover:text-foreground"
                >
                  Year <ArrowUpDown className="inline h-3 w-3 ml-1" />
                </th>
                <th
                  onClick={() => handleSort("marketClass")}
                  className="p-3.5 cursor-pointer hover:text-foreground"
                >
                  Class
                </th>
                <th
                  onClick={() => handleSort("fp32Gflops")}
                  className="p-3.5 cursor-pointer hover:text-foreground"
                >
                  FP32 FLOPS <ArrowUpDown className="inline h-3 w-3 ml-1" />
                </th>
                <th
                  onClick={() => handleSort("memoryBandwidthGBs")}
                  className="p-3.5 cursor-pointer hover:text-foreground"
                >
                  Memory BW <ArrowUpDown className="inline h-3 w-3 ml-1" />
                </th>
                <th
                  onClick={() => handleSort("vramGB")}
                  className="p-3.5 cursor-pointer hover:text-foreground"
                >
                  VRAM
                </th>
                <th
                  onClick={() => handleSort("tdpWatts")}
                  className="p-3.5 cursor-pointer hover:text-foreground"
                >
                  TDP
                </th>
                <th className="p-3.5 text-right font-bold text-cyan-400">
                  {breakthroughMode ? "Contract Parity" : "Raw Deficit"}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/30">
              {sortedGpus.map((gpu) => {
                const comp = calculateGpuComparison(gpu, HOST_HARDWARE, breakthroughMode);
                const isSuperFast = gpu.fp32Gflops > 50000;
                return (
                  <tr key={gpu.id} className="hover:bg-zinc-900/60 transition-colors group text-xs">
                    <td className="p-3.5 font-bold text-foreground flex flex-col">
                      <span>{gpu.name}</span>
                      <span className="text-[10px] text-muted-foreground font-normal group-hover:text-cyan-400/80 transition-colors">
                        {gpu.keyInnovation}
                      </span>
                    </td>
                    <td className="p-3.5 text-muted-foreground">{gpu.architecture}</td>
                    <td className="p-3.5 text-foreground">{gpu.year}</td>
                    <td className="p-3.5">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          gpu.marketClass === "Datacenter"
                            ? "bg-purple-500/20 text-purple-400 border border-purple-500/30"
                            : gpu.marketClass === "Workstation"
                              ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                              : "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30"
                        }`}
                      >
                        {gpu.marketClass}
                      </span>
                    </td>
                    <td className="p-3.5 font-mono text-foreground">
                      {gpu.fp32Gflops >= 1000
                        ? `${(gpu.fp32Gflops / 1000).toFixed(1)} TFLOPS`
                        : `${gpu.fp32Gflops.toFixed(1)} GFLOPS`}
                    </td>
                    <td className="p-3.5 font-mono text-muted-foreground">
                      {gpu.memoryBandwidthGBs >= 1000
                        ? `${(gpu.memoryBandwidthGBs / 1000).toFixed(2)} TB/s`
                        : `${gpu.memoryBandwidthGBs.toFixed(1)} GB/s`}
                    </td>
                    <td className="p-3.5 font-mono text-muted-foreground">
                      {gpu.vramGB >= 1 ? `${gpu.vramGB} GB` : `${Math.round(gpu.vramGB * 1000)} MB`}
                    </td>
                    <td className="p-3.5 text-muted-foreground">{gpu.tdpWatts} W</td>
                    <td className="p-3.5 text-right font-bold font-mono">
                      {breakthroughMode ? (
                        <div className="inline-flex items-center gap-1 text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded border border-emerald-500/30 shadow-[0_0_10px_rgba(0,255,136,0.1)]">
                          <CheckCircle2 className="h-3 w-3" />
                          <span>100% PARITY</span>
                        </div>
                      ) : (
                        <div className="inline-flex flex-col items-end">
                          <span
                            className={`${
                              comp.rawSiliconParityPct < 5.0
                                ? "text-red-400"
                                : comp.rawSiliconParityPct < 50.0
                                  ? "text-amber-400"
                                  : "text-emerald-400"
                            }`}
                          >
                            {comp.rawSiliconParityPct}% Raw
                          </span>
                          <span className="text-[10px] text-muted-foreground">
                            ({comp.workReductionNeeded}x Deficit)
                          </span>
                        </div>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
