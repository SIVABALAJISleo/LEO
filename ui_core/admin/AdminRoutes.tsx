import React from "react";
import { Routes, Route, useParams, Navigate } from "react-router-dom";
import AdminDashboard from "./AdminDashboard";

// Import modern dashboards
import { ValidationDashboard } from "../src/dashboards/ValidationDashboard";
import { FailureHuntingDashboard } from "../src/dashboards/FailureHuntingDashboard";
import { QualityAmplifierDashboard } from "../src/dashboards/QualityAmplifierDashboard";
import { FrontierOptimizationDashboard } from "../src/dashboards/FrontierOptimizationDashboard";
import { ConvergenceDashboard } from "../src/dashboards/ConvergenceDashboard";
import { CertificationDashboard } from "../src/dashboards/CertificationDashboard";
import { RealityExecutionDashboard } from "../src/dashboards/RealityExecutionDashboard";
import { ScientificCertificationDashboard } from "../src/dashboards/ScientificCertificationDashboard";
import { ScientificValidationDashboard } from "../src/dashboards/ScientificValidationDashboard";
import { FrontierIntelligenceDashboard } from "../src/dashboards/FrontierIntelligenceDashboard";
import { FrontierIntelligenceDashboardV2 } from "../src/dashboards/FrontierIntelligenceDashboardV2";
import { ComputeIrrelevanceDashboard } from "../src/dashboards/ComputeIrrelevanceDashboard";
import { EngineeringCeilingDashboard } from "../src/dashboards/EngineeringCeilingDashboard";
import { RealityLearningDashboard } from "../src/dashboards/RealityLearningDashboard";
import { ComputeIrrelevanceV33Dashboard } from "../src/dashboards/ComputeIrrelevanceV33Dashboard";
import { ComputeIrrelevanceV34Dashboard } from "../src/dashboards/ComputeIrrelevanceV34Dashboard";
import { LEOAIv35Scoreboard } from "../src/dashboards/LEOAIv35Scoreboard";
import { LEOAIv36Dashboard } from "../src/dashboards/LEOAIv36Dashboard";
import { LEOAIv37Dashboard } from "../src/dashboards/LEOAIv37Dashboard";
import { LEOAIv38Dashboard } from "../src/dashboards/LEOAIv38Dashboard";
import { LEOAIv40Dashboard } from "../src/dashboards/LEOAIv40Dashboard";
import { LEOAIvInfinityDashboard } from "../src/dashboards/LEOAIvInfinityDashboard";
import { V42Dashboard } from "../components/v42/V42Dashboard";
import { OmegaDashboard } from "../src/v43/dashboard/OmegaDashboard";
import { SingularityDashboard } from "../src/v45/dashboard/SingularityDashboard";

// Import Legacy Cognitive Dashboards
import LegacyCognitiveDashboards from "./dashboards/LegacyCognitiveDashboards";

function LegacyTabWrapper() {
  const { tabId } = useParams<{ tabId: string }>();

  // Determine element to render based on URL parameter
  switch (tabId) {
    case "swarm":
    case "cognitive":
    case "v14super":
    case "v15substrate":
    case "v16substrate":
    case "v17dominance":
    case "debate":
    case "quality":
    case "benchmarks":
    case "devops":
      return <LegacyCognitiveDashboards activeTab={tabId} />;

    case "v18validation":
      return <ValidationDashboard />;
    case "failureHunting":
      return <FailureHuntingDashboard />;
    case "v22quality":
      return <QualityAmplifierDashboard />;
    case "v23frontier":
      return <FrontierOptimizationDashboard />;
    case "v24convergence":
      return <ConvergenceDashboard />;
    case "v25certification":
      return <CertificationDashboard />;
    case "v26reality":
      return <RealityExecutionDashboard />;
    case "v27certification":
      return <ScientificCertificationDashboard />;
    case "v28validation":
      return <ScientificValidationDashboard />;
    case "v29frontier":
      return <FrontierIntelligenceDashboard />;
    case "v30frontier":
      return <FrontierIntelligenceDashboardV2 />;
    case "v31irrelevance":
      return <ComputeIrrelevanceDashboard />;
    case "v32ceiling":
      return <EngineeringCeilingDashboard />;
    case "v32reality":
      return <RealityLearningDashboard />;
    case "v33compute":
      return <ComputeIrrelevanceV33Dashboard />;
    case "v34compute":
      return <ComputeIrrelevanceV34Dashboard />;
    case "v35parity":
      return <LEOAIv35Scoreboard />;
    case "v36ceiling":
      return <LEOAIv36Dashboard />;
    case "v37evolution":
      return <LEOAIv37Dashboard />;
    case "v38architecture":
      return <LEOAIv38Dashboard />;
    case "v40ultimate":
      return <LEOAIv40Dashboard />;
    case "vinfinity":
      return <LEOAIvInfinityDashboard />;
    case "v42irrelevance":
      return <V42Dashboard />;
    case "v43omega":
      return <OmegaDashboard />;
    case "v45singularity":
      return <SingularityDashboard />;

    default:
      return <Navigate to="/admin" replace />;
  }
}

export default function AdminRoutes() {
  return (
    <Routes>
      <Route
        path="legacy/:tabId"
        element={
          <AdminDashboard activeSection="legacy">
            <LegacyTabWrapper />
          </AdminDashboard>
        }
      />
      <Route path="*" element={<Navigate to="/admin" replace />} />
    </Routes>
  );
}
