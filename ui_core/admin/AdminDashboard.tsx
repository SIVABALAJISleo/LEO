import React from "react";
import { useNavigate } from "react-router-dom";
import { IntelliGPUDashboard } from "../components/IntelliGPUDashboard";

interface AdminDashboardProps {
  activeSection?: string;
  setActiveSection?: (sec: string) => void;
  children?: React.ReactNode;
}

export default function AdminDashboard({ activeSection, setActiveSection, children }: AdminDashboardProps) {
  const navigate = useNavigate();
  return (
    <IntelliGPUDashboard
      onSignOut={() => navigate("/")}
      onNavigateToLegacy={() => navigate("/admin/legacy/swarm")}
      activeSection={activeSection}
      setActiveSection={setActiveSection}
    >
      {children}
    </IntelliGPUDashboard>
  );
}
