import React, { useState, useEffect } from 'react';
import { generateMasterReport, MasterReport } from '../failure_hunting/calculators/masterReportGenerator';
import { ShieldAlert, Crosshair, AlertTriangle, Cpu, BrainCircuit, Bug, FileOutput } from 'lucide-react';

export function FailureHuntingDashboard() {
    const [report, setReport] = useState<MasterReport | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchReport = async () => {
            const data = await generateMasterReport();
            setReport(data);
            setLoading(false);
        };
        fetchReport();
    }, []);

    const handlePrint = () => {
        window.print();
    };

    if (loading || !report) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-red-500 animate-pulse bg-black/90 p-10">
                <Crosshair className="w-16 h-16 mb-4 animate-spin-slow" />
                <h2 className="text-2xl font-bold uppercase tracking-widest text-red-600">Hunting Weaknesses...</h2>
                <p className="text-red-400/70 text-sm mt-2 font-mono">Running Adversarial Failure Injections</p>
            </div>
        );
    }

    return (
        <div className="bg-black text-red-100 min-h-screen p-8 font-mono print:bg-white print:text-black">
            <style dangerouslySetInnerHTML={{__html: `
                @media print {
                    .no-print { display: none !important; }
                    body { background-color: white !important; }
                    .print-break { page-break-before: always; }
                }
            `}} />

            <div className="max-w-6xl mx-auto space-y-8">
                {/* Header */}
                <header className="flex justify-between items-center border-b border-red-900/50 pb-6 print:border-black">
                    <div>
                        <h1 className="text-4xl font-black tracking-tighter text-red-600 print:text-black flex items-center gap-3">
                            <ShieldAlert className="w-10 h-10" />
                            BALANCE GAP MASTER REPORT
                        </h1>
                        <p className="text-red-500/70 uppercase text-sm tracking-widest mt-2 print:text-gray-700">
                            Failure Discovery & Adversarial Vulnerability Audit
                        </p>
                    </div>
                    <button 
                        onClick={handlePrint}
                        className="no-print flex items-center gap-2 bg-red-900/40 hover:bg-red-800/60 border border-red-700 text-red-300 px-6 py-3 rounded uppercase text-sm font-bold transition-all"
                    >
                        <FileOutput className="w-4 h-4" />
                        Export PDF
                    </button>
                </header>

                {/* Score Grid */}
                <section>
                    <h2 className="text-2xl font-bold mb-4 flex items-center gap-2 text-red-500 print:text-black">
                        <Cpu className="w-6 h-6" /> System Integrity Scores
                    </h2>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {Object.entries(report.scores).map(([key, value]) => (
                            <div key={key} className="bg-red-950/20 border border-red-900/30 p-4 rounded print:border-gray-300 print:bg-white">
                                <div className="text-red-400/70 text-xs uppercase mb-1 print:text-gray-600">
                                    {key.replace(/([A-Z])/g, ' $1').trim()}
                                </div>
                                <div className="text-3xl font-black text-red-100 print:text-black">
                                    {value.toFixed(1)}%
                                </div>
                            </div>
                        ))}
                    </div>
                </section>

                <div className="grid md:grid-cols-2 gap-8 print-break">
                    {/* Top Weaknesses */}
                    <section>
                        <h2 className="text-xl font-bold mb-4 flex items-center gap-2 text-orange-500 print:text-black">
                            <AlertTriangle className="w-5 h-5" /> Critical Weaknesses
                        </h2>
                        <ul className="space-y-3">
                            {report.topWeaknesses.map((weakness, i) => (
                                <li key={i} className="bg-orange-950/20 border-l-4 border-orange-600 p-3 text-sm text-orange-200 print:text-black print:border-gray-800">
                                    {weakness}
                                </li>
                            ))}
                        </ul>
                    </section>

                    {/* Bottlenecks */}
                    <section>
                        <h2 className="text-xl font-bold mb-4 flex items-center gap-2 text-red-500 print:text-black">
                            <Bug className="w-5 h-5" /> Architectural Bottlenecks
                        </h2>
                        <ul className="space-y-3">
                            {report.topBottlenecks.map((bottleneck, i) => (
                                <li key={i} className="bg-red-950/20 border-l-4 border-red-600 p-3 text-sm text-red-200 print:text-black print:border-gray-800">
                                    {bottleneck}
                                </li>
                            ))}
                        </ul>
                    </section>
                </div>

                <div className="grid md:grid-cols-2 gap-8 print-break">
                    {/* Limiting Factors */}
                    <section>
                        <h2 className="text-xl font-bold mb-4 flex items-center gap-2 text-yellow-500 print:text-black">
                            <BrainCircuit className="w-5 h-5" /> Limiting Factors
                        </h2>
                        <ul className="space-y-3">
                            {report.limitingFactors.map((factor, i) => (
                                <li key={i} className="bg-yellow-950/20 border-l-4 border-yellow-600 p-3 text-sm text-yellow-200 print:text-black print:border-gray-800">
                                    {factor}
                                </li>
                            ))}
                        </ul>
                    </section>

                    {/* ROI & Estimated Ceiling */}
                    <section>
                        <h2 className="text-xl font-bold mb-4 flex items-center gap-2 text-green-500 print:text-black">
                            Target Ceiling & Next ROI
                        </h2>
                        <div className="bg-green-950/20 border border-green-900/50 p-6 rounded mb-6 print:border-gray-400">
                            <div className="text-green-400 text-sm uppercase mb-2 print:text-gray-600">Estimated Ceiling After Fixes</div>
                            <div className="text-5xl font-black text-green-400 print:text-black">{report.estimatedCeilingAfterFixes}%</div>
                        </div>
                        <ul className="space-y-2">
                            {report.nextHighestRoi.map((roi, i) => (
                                <li key={i} className="text-green-300 text-sm font-bold print:text-gray-800">
                                    {roi}
                                </li>
                            ))}
                        </ul>
                    </section>
                </div>

            </div>
        </div>
    );
}
