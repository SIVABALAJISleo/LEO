import React from "react";
import { useNavigate } from "react-router-dom";
import { IntelliGPUHome } from "../components/IntelliGPUHome";

export default function Home() {
  const navigate = useNavigate();
  return <IntelliGPUHome onNavigate={(view: any) => navigate(view === "home" ? "/" : `/${view}`)} />;
}
