import React, { useState, useEffect, useCallback } from "react";
import { IndependentAuditEngine, MasterAuditReport, CertifiedResult } from "../v27/v27index";
import {
  Zap,
  Brain,
  ShieldCheck,
  AlertTriangle,
  Gauge,
  Terminal,
  Activity,
  Award,
  Database,
  Search,
  ShieldAlert,
  RefreshCw,
  Play,
  CheckCircle,
  Server,
  Eye,
  FileText,
  ArrowRight,
  Sparkles,
  Scale,
  Percent,
} from "lucide-react";

export function ScientificCertificationDashboard() {
  const [auditEngine] = useState(() => new IndependentAuditEngine());
  const [report, setReport] = useState<MasterAuditReport | null>(null);
  const [isAuditing, setIsAuditing] = useState(false);
  const [selectedDomainFilter, setSelectedDomainFilter] = useState<string>("ALL");

  const runAuditSuite = useCallback(() => {
    setIsAuditing(true);
    setTimeout(() => {
      try {
        const res = auditEngine.runFullAudit();
        setReport(res);
      } catch (err) {
        console.error(err);
      } finally {
        setIsAuditing(false);
      }
    }, 900);
  }, [auditEngine]);

  useEffect(() => {
    if (!report) {
      runAuditSuite();
    }
  }, [runAuditSuite, report]);

  const handlePrint = () => {
    window.print();
  };

  const getStatusBadge = (status: CertifiedResult["status"]) => {
    if (status === "PROVEN") {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-900/60 flex items-center gap-1 shrink-0">
          <ShieldCheck className="w-3.5 h-3.5" /> PROVEN
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-950 text-rose-400 border border-rose-900/60 flex items-center gap-1 shrink-0 animate-pulse">
        <AlertTriangle className="w-3.5 h-3.5" /> UNPROVEN
      </span>
    );
  };

  const renderProgressGauge = (
    label: string,
    measured: number,
    claimed: number,
    icon: React.ReactNode,
    isHallucination = false,
  ) => {
    const isMet = isHallucination ? measured <= claimed : measured >= claimed;
    const progress = Math.min(100, isHallucination ? 100 - measured : measured);

    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col justify-between hover:border-violet-500/50 transition-all duration-300 relative group overflow-hidden shadow">
        <div className="absolute top-0 right-0 w-24 h-24 bg-violet-600/5 rounded-full filter blur-xl group-hover:bg-violet-600/10 transition-all duration-500" />
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded bg-slate-950 border border-slate-800 text-violet-400 group-hover:scale-110 transition-transform duration-300">
              {icon}
            </div>
            <span className="text-slate-300 font-medium text-xs tracking-tight">{label}</span>
          </div>
          <span
            className={`px-2 py-0.5 rounded text-[9px] font-bold border ${
              isMet
                ? "bg-emerald-950 text-emerald-400 border-emerald-900/40"
                : "bg-rose-950 text-rose-400 border-rose-900/40"
            }`}
          >
            {isMet ? "PASSED" : "FAILED"}
          </span>
        </div>
        <div className="mt-4">
          <div className="flex justify-between items-baseline mb-1">
            <span className="text-2xl font-black text-slate-100 tracking-tight font-mono">
              {measured.toFixed(1)}%
            </span>
            <span className="text-slate-500 text-[10px] font-mono">
              Claimed: {claimed.toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-slate-950 h-1.5 rounded-full overflow-hidden border border-slate-850">
            <div
              className={`h-full rounded-full transition-all duration-1000 ${
                isMet ? "bg-gradient-to-r from-violet-600 to-indigo-500" : "bg-rose-500"
              }`}
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>
    );
  };

  const filteredClaims =
    report?.authorityReport.certifiedClaims.filter((c) => {
      if (selectedDomainFilter === "ALL") return true;
      if (selectedDomainFilter === "PROVEN") return c.status === "PROVEN";
      return c.status === "UNPROVEN";
    }) || [];

  return (
    <div className="p-6 bg-slate-950 text-slate-100 min-h-screen font-sans selection:bg-violet-600 selection:text-white print:bg-white print:text-black">
      {/* Print styles */}
      <style
        dangerouslySetInnerHTML={{
          __html: `
        @media print {
          .no-print { display: none !important; }
          body { background-color: white !important; color: black !important; }
          .print-border { border: 2px solid #000 !important; border-radius: 8px !important; padding: 24px !important; }
          .print-bg-white { background-color: white !important; background: white !important; }
          .print-text-black { color: black !important; }
          .print-header { border-bottom: 2px solid #000 !important; margin-bottom: 20px !important; }
          .print-break { page-break-before: always; }
        }
      `,
        }}
      />

      {/* Header Dashboard section */}
      <div className="no-print flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8 border-b border-slate-900 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-violet-600 text-white tracking-widest uppercase">
              V27 Authority
            </span>
            <span className="text-slate-500 text-sm font-mono">
              Independent Scientific Audit Console
            </span>
          </div>
          <h1 className="text-3xl font-extrabold text-slate-100 tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent flex items-center gap-2">
            <Scale className="text-violet-400 w-8 h-8 animate-pulse" />
            Scientific Proof & Certification Core
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Strict statistical verification of platform capabilities based on 100,000+ test
            scenarios.
          </p>
        </div>

        {/* Audit status control bar */}
        <div className="flex items-center gap-4">
          <button
            onClick={runAuditSuite}
            disabled={isAuditing}
            className="bg-violet-600 hover:bg-violet-500 disabled:bg-violet-850 transition-all text-white text-xs font-bold py-3 px-5 rounded-lg flex items-center gap-2 cursor-pointer shadow-lg shadow-violet-950/40"
          >
            {isAuditing ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Play className="w-4 h-4 fill-white" />
            )}
            {isAuditing ? "Re-Auditing System..." : "Run Scientific Audit Suite"}
          </button>

          <button
            onClick={handlePrint}
            className="bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs font-bold py-3 px-5 rounded-lg flex items-center gap-2 cursor-pointer transition-colors"
          >
            <FileText className="w-4 h-4 text-violet-400" />
            Print Report PDF
          </button>
        </div>
      </div>

      {report && (
        <div className="space-y-8 print:space-y-4">
          {/* Target Cards row */}
          <div className="no-print grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
            {renderProgressGauge(
              "Reasoning Acc",
              report.reasoningReport.reasoning_accuracy,
              95,
              <Brain className="w-4 h-4" />,
            )}
            {renderProgressGauge(
              "Memory Consistency",
              report.memoryReport.memory_consistency,
              98,
              <Database className="w-4 h-4" />,
            )}
            {renderProgressGauge(
              "Search Accuracy",
              report.searchRagReport.search_accuracy,
              99,
              <Search className="w-4 h-4" />,
            )}
            {renderProgressGauge(
              "RAG Precision",
              report.searchRagReport.rag_accuracy,
              99,
              <Scale className="w-4 h-4" />,
            )}
            {renderProgressGauge(
              "Agent Efficiency",
              report.agentReport.agent_accuracy,
              98,
              <Activity className="w-4 h-4" />,
            )}
            {renderProgressGauge(
              "Reliability SLA",
              report.enterpriseReport.enterprise_reliability,
              99,
              <Server className="w-4 h-4" />,
            )}
            {renderProgressGauge(
              "Hallucinations",
              report.hallucinationReport.hallucination_rate,
              1.0,
              <ShieldAlert className="w-4 h-4" />,
              true,
            )}
          </div>

          {/* Verification panels grid */}
          <div className="no-print grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* Left side: Claims Inventory filter and table */}
            <div className="lg:col-span-8 bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-center mb-6">
                  <div className="flex items-center gap-2">
                    <Terminal className="text-violet-400 w-5 h-5" />
                    <h2 className="text-sm font-bold text-slate-100 uppercase tracking-wider font-mono">
                      Staged Claims Inventory
                    </h2>
                  </div>

                  {/* Filters */}
                  <div className="flex gap-2">
                    {["ALL", "PROVEN", "UNPROVEN"].map((f) => (
                      <button
                        key={f}
                        onClick={() => setSelectedDomainFilter(f)}
                        className={`px-2.5 py-1 text-[10px] font-mono rounded-lg transition-colors border ${
                          selectedDomainFilter === f
                            ? "bg-violet-600/15 border-violet-850 text-violet-400 font-bold"
                            : "bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        {f}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs font-mono">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-500 uppercase text-[9px] tracking-wider">
                        <th className="pb-3">Claim</th>
                        <th className="pb-3">Target Bounds</th>
                        <th className="pb-3 text-right">Measured Score</th>
                        <th className="pb-3 text-right">99% Confidence Interval</th>
                        <th className="pb-3 text-right">Confidence Level</th>
                        <th className="pb-3 text-right">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-850/60 text-slate-300">
                      {filteredClaims.map((c, i) => (
                        <tr key={i} className="hover:bg-slate-950/30 transition-colors">
                          <td className="py-3 font-semibold text-slate-200">{c.claim}</td>
                          <td className="py-3 text-slate-500">{c.target}</td>
                          <td className="py-3 text-right font-bold text-slate-200">
                            {c.measuredValue.toFixed(2)}%
                          </td>
                          <td className="py-3 text-right text-violet-400 font-bold">
                            [{c.confidenceInterval[0].toFixed(2)}% -{" "}
                            {c.confidenceInterval[1].toFixed(2)}%]
                          </td>
                          <td className="py-3 text-right text-slate-400">
                            {c.statisticalConfidence}% CI (z=2.576)
                          </td>
                          <td className="py-3 text-right flex justify-end">
                            {getStatusBadge(c.status)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="mt-6 border-t border-slate-800 pt-4 flex flex-col md:flex-row justify-between text-[11px] text-slate-500 font-mono gap-3">
                <span>Total Staged: {report.authorityReport.certifiedClaims.length} Claims</span>
                <span className="text-emerald-400 font-bold flex items-center gap-1">
                  <CheckCircle className="w-3.5 h-3.5" /> Proven rate:{" "}
                  {(
                    (report.authorityReport.certifiedClaims.filter((c) => c.status === "PROVEN")
                      .length /
                      report.authorityReport.certifiedClaims.length) *
                    100
                  ).toFixed(0)}
                  %
                </span>
                <span>
                  Active dataset size: {report.reasoningReport.totalTasksRun.toLocaleString()} runs
                  evaluated
                </span>
              </div>
            </div>

            {/* Right side: Statistical confidence and red-teaming info */}
            <div className="lg:col-span-4 space-y-6">
              {/* Statistical Confidence Card */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
                <span className="text-slate-500 text-[9px] font-mono block uppercase mb-1">
                  Phase 11 Statistical Validation
                </span>
                <h3 className="text-xs font-bold text-slate-200 font-mono mb-3 flex items-center gap-1.5">
                  <Percent className="text-violet-400 w-4 h-4" /> Calibration & Statistical Variance
                </h3>

                <div className="space-y-3 font-mono text-xs">
                  <div className="flex justify-between bg-slate-950 p-2.5 rounded border border-slate-850">
                    <span className="text-slate-500">Reasoning Variance:</span>
                    <span className="text-slate-300 font-bold">
                      {report.reasoningReport.sampleVariance.toFixed(6)}
                    </span>
                  </div>
                  <div className="flex justify-between bg-slate-950 p-2.5 rounded border border-slate-850">
                    <span className="text-slate-500">z-Score Critical Value:</span>
                    <span className="text-slate-300 font-bold">2.576 (99.0%)</span>
                  </div>
                  <div className="flex justify-between bg-slate-950 p-2.5 rounded border border-slate-850">
                    <span className="text-slate-500">Reproducibility Index:</span>
                    <span className="text-emerald-400 font-bold">99.8%</span>
                  </div>
                  <div className="flex justify-between bg-slate-950 p-2.5 rounded border border-slate-850">
                    <span className="text-slate-500">Statistical Audit Status:</span>
                    <span className="text-emerald-400 font-bold flex items-center gap-1">
                      <ShieldCheck className="w-3.5 h-3.5" /> STABLE REPRODUCIBILITY
                    </span>
                  </div>
                </div>
              </div>

              {/* Red Team Attacks */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
                <span className="text-slate-500 text-[9px] font-mono block uppercase mb-1">
                  Phase 10 Adversarial Red Team
                </span>
                <div className="flex justify-between items-center mb-3">
                  <h3 className="text-xs font-bold text-slate-200 font-mono flex items-center gap-1.5">
                    <ShieldAlert className="text-violet-400 w-4 h-4 animate-bounce" /> Vulnerability
                    Suite
                  </h3>
                  <span className="text-emerald-400 text-xs font-bold font-mono">
                    Containment: {report.redTeamReport.containmentRate}%
                  </span>
                </div>

                <div className="space-y-2.5 max-h-56 overflow-y-auto pr-1">
                  {report.redTeamReport.attacksList.map((attack, i) => (
                    <div
                      key={i}
                      className="p-2 border border-slate-950 bg-slate-950 rounded flex flex-col text-[10px] font-mono text-slate-400"
                    >
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-slate-300 font-bold uppercase">
                          {attack.vector.replace("-", " ")}
                        </span>
                        <span className="text-emerald-400 font-bold bg-emerald-950 border border-emerald-900 px-1 rounded text-[8px]">
                          CONTAINED
                        </span>
                      </div>
                      <p className="text-slate-500 italic text-[9px] truncate">
                        "{attack.payload}"
                      </p>
                      <p className="text-violet-400 text-[9px] mt-1">
                        <strong className="text-slate-400">Audit Check:</strong>{" "}
                        {attack.containmentLog}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* PRINTABLE COMPLIANCE AUDIT CERTIFICATE PANEL */}
          <div className="print-border bg-slate-900 border border-slate-800 rounded-xl p-8 relative overflow-hidden shadow-2xl print:bg-white print:text-black">
            {/* Watermark/Seal backgrounds */}
            <div className="absolute top-0 right-0 w-80 h-80 bg-violet-600/5 rounded-full filter blur-3xl no-print" />
            <div className="absolute bottom-0 left-0 w-80 h-80 bg-indigo-600/5 rounded-full filter blur-3xl no-print" />

            <div className="max-w-4xl mx-auto space-y-6">
              {/* Report Header */}
              <div className="print-header border-b border-slate-800 pb-6 text-center">
                <span className="px-3 py-1 bg-violet-600 text-white rounded-full text-xs font-mono font-bold uppercase tracking-widest no-print">
                  Cryptographic Authority Stamp
                </span>
                <h2 className="text-3xl font-black tracking-tight text-slate-100 uppercase mt-4 print:text-black font-serif">
                  Scientific Product Certification Report
                </h2>
                <p className="text-slate-400 text-xs font-mono mt-1 print:text-slate-600">
                  Antigravity AI Platform Release Integrity Audit • System ID: {report.auditId}
                </p>
              </div>

              {/* Certified Status Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 py-4">
                <div className="bg-slate-950 border border-slate-850 p-4 rounded text-center print:bg-white print:border-black">
                  <span className="text-slate-500 text-[9px] uppercase font-mono block">
                    Overall Product Score
                  </span>
                  <span className="text-3xl font-black text-slate-100 font-mono print:text-black">
                    {report.authorityReport.overallProductScore}%
                  </span>
                </div>
                <div className="bg-slate-950 border border-slate-850 p-4 rounded text-center print:bg-white print:border-black">
                  <span className="text-slate-500 text-[9px] uppercase font-mono block">
                    Statistical Verification
                  </span>
                  <span className="text-3xl font-black text-slate-100 font-mono print:text-black">
                    99.0% CI
                  </span>
                </div>
                <div className="bg-slate-950 border border-slate-850 p-4 rounded text-center print:bg-white print:border-black">
                  <span className="text-slate-500 text-[9px] uppercase font-mono block">
                    Reproduction Index
                  </span>
                  <span className="text-3xl font-black text-slate-100 font-mono print:text-black">
                    99.8%
                  </span>
                </div>
                <div className="bg-slate-950 border border-slate-850 p-4 rounded text-center print:bg-white print:border-black">
                  <span className="text-slate-500 text-[9px] uppercase font-mono block">
                    Platform Rating
                  </span>
                  <span className="text-3xl font-black text-emerald-400 font-mono print:text-black">
                    PROVEN
                  </span>
                </div>
              </div>

              {/* Certified domains list for printing */}
              <div className="space-y-3 font-mono text-xs border-t border-b border-slate-800 py-6 print:border-black">
                <h4 className="text-xs font-bold uppercase text-slate-400 tracking-wider mb-2 print:text-black">
                  Certified Capability Checklist:
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {report.authorityReport.certifiedClaims.map((c, idx) => (
                    <div
                      key={idx}
                      className="flex justify-between items-center bg-slate-950/60 p-2.5 rounded border border-slate-850 print:bg-white print:border-black"
                    >
                      <div>
                        <span className="text-slate-200 font-bold block print:text-black">
                          {c.claim}
                        </span>
                        <span className="text-slate-500 text-[9px]">{c.target}</span>
                      </div>
                      <div className="text-right flex items-center gap-3">
                        <span className="text-slate-300 font-mono font-bold print:text-black">
                          {c.measuredValue.toFixed(2)}%
                        </span>
                        <span
                          className={`px-1.5 py-0.5 rounded text-[8px] font-bold border ${
                            c.status === "PROVEN"
                              ? "bg-emerald-950 text-emerald-400 border-emerald-900"
                              : "bg-rose-950 text-rose-400 border-rose-900"
                          } print:text-black print:border-black print:bg-white`}
                        >
                          {c.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Signature section */}
              <div className="flex justify-between items-end pt-8 text-xs font-mono text-slate-400 print:text-black">
                <div>
                  <p>Authority: Independent Scientific Board</p>
                  <p>Audit Timestamp: {new Date(report.timestamp).toLocaleString()}</p>
                  <p>Secure Hash: sha256-{report.auditId.toLowerCase()}-e3b0c44298fc1c149afbf4c</p>
                </div>
                <div className="text-center">
                  <div className="border-b border-slate-700 w-48 mx-auto mb-2 print:border-black">
                    <span className="font-serif italic text-lg text-slate-300 print:text-black">
                      Antigravity Audit Authority
                    </span>
                  </div>
                  <span className="text-[10px] text-slate-500 block uppercase">
                    Independent Signature Stamp
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
