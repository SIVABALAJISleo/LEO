import React from "react";
import { useNavigate } from "react-router-dom";
import { IntelliGPUOnboarding } from "../components/IntelliGPUOnboarding";

export default function Onboarding() {
  const navigate = useNavigate();
  return (
    <IntelliGPUOnboarding
      onNavigate={(view: any) => navigate(view === "home" ? "/" : `/${view}`)}
      onComplete={() => navigate("/swarms")}
    />
  );
}
