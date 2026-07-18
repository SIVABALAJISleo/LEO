import React from "react";
import { useNavigate } from "react-router-dom";
import { IntelliGPUAuth } from "../components/IntelliGPUAuth";

export default function Auth() {
  const navigate = useNavigate();
  return (
    <IntelliGPUAuth 
      onNavigate={(view: any) => navigate(view === "home" ? "/" : `/${view}`)} 
      onSuccess={() => navigate("/swarms")}
    />
  );
}
