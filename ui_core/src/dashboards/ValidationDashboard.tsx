import React, { useEffect, useState } from 'react';
import { generateEnterpriseAuditReport, EnterpriseAuditReport } from '../reporting/reportExporter';

export const ValidationDashboard: React.FC = () => {
  const [report, setReport] = useState<EnterpriseAuditReport | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchReport = async () => {
      setLoading(true);
      const data = await generateEnterpriseAuditReport();
      setReport(data);
      setLoading(false);
    };

    fetchReport();
  }, []);

  if (loading || !report) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-950 text-white">
        <div className="text-xl font-semibold animate-pulse">Running V18 Enterprise Validation Universe...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-200 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="flex justify-between items-end border-b border-gray-800 pb-4">
          <div>
            <h1 className="text-4xl font-bold text-white tracking-tight">{report.title}</h1>
            <p className="text-sm text-gray-500 mt-2">Generated at: {new Date(report.generatedAt).toLocaleString()}</p>
          </div>
          <button 
            onClick={() => window.print()}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg shadow-lg transition-colors"
          >
            Export to PDF
          </button>
        </div>

        {/* Top Level Scores */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <ScoreCard title="Overall Product Score" score={report.scores.overallProductScore} />
          <ScoreCard title="Enterprise AI Score" score={report.scores.enterpriseAiScore} />
          <ScoreCard title="Practical AI Score" score={report.scores.practicalAiScore} />
          <ScoreCard title="NVIDIA Relevance Reduction" score={report.scores.nvidiaRelevanceReductionScore} />
        </div>

        {/* Detail Scores */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 shadow-2xl">
          <h2 className="text-2xl font-semibold text-white mb-6">Component Quality Metrics</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            <MetricItem label="Architecture" value={report.scores.architectureScore} />
            <MetricItem label="Infrastructure" value={report.scores.infrastructureScore} />
            <MetricItem label="Reasoning" value={report.scores.reasoningScore} />
            <MetricItem label="Language" value={report.scores.languageScore} />
            <MetricItem label="Memory" value={report.scores.memoryScore} />
            <MetricItem label="Agent Swarm" value={report.scores.agentScore} />
            <MetricItem label="GraphRAG" value={report.scores.ragScore} />
            <MetricItem label="Research" value={report.scores.researchScore} />
            <MetricItem label="Security" value={report.scores.securityScore} />
            <MetricItem label="Reality Feedback" value={report.scores.realityScore} />
          </div>
        </div>

        {/* Textual Analysis */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <ListSection title="Strengths" items={report.strengths} color="text-green-400" />
          <ListSection title="Weaknesses" items={report.weaknesses} color="text-yellow-400" />
          <ListSection title="Bottlenecks" items={report.bottlenecks} color="text-orange-400" />
          <ListSection title="Failure Modes" items={report.failureModes} color="text-red-400" />
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 shadow-2xl">
          <h2 className="text-2xl font-semibold text-white mb-4">Improvement Priorities & Recommendations</h2>
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-blue-400 mb-2">Priorities</h3>
              <ul className="list-disc list-inside space-y-1 text-gray-300">
                {report.improvementPriorities.map((item, idx) => <li key={idx}>{item}</li>)}
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-medium text-purple-400 mb-2">Strategic Recommendations</h3>
              <ul className="list-disc list-inside space-y-1 text-gray-300">
                {report.recommendations.map((item, idx) => <li key={idx}>{item}</li>)}
              </ul>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

const ScoreCard = ({ title, score }: { title: string, score: number }) => (
  <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl shadow-lg flex flex-col items-center justify-center">
    <div className="text-sm text-gray-400 uppercase tracking-wider mb-2">{title}</div>
    <div className="text-4xl font-bold text-white">{score}%</div>
  </div>
);

const MetricItem = ({ label, value }: { label: string, value: number }) => (
  <div className="flex justify-between items-center border-b border-gray-800 py-2">
    <span className="text-gray-400">{label}</span>
    <span className="font-medium text-white">{value.toFixed(1)}%</span>
  </div>
);

const ListSection = ({ title, items, color }: { title: string, items: string[], color: string }) => (
  <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 shadow-lg">
    <h2 className={`text-xl font-semibold mb-4 ${color}`}>{title}</h2>
    <ul className="list-disc list-inside space-y-2 text-gray-300">
      {items.map((item, idx) => (
        <li key={idx} className="leading-relaxed">{item}</li>
      ))}
    </ul>
  </div>
);
