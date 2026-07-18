import React, { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { LeoStatusProvider } from "./contexts/LeoStatusContext";

// Layouts
import PublicLayout from "./layouts/PublicLayout";
import AdminLayout from "./layouts/AdminLayout";

// Public Pages
import Home from "./pages/Home";
import Documentation from "./pages/Documentation";
import Playground from "./pages/Playground";
import Auth from "./pages/Auth";
import Onboarding from "./pages/Onboarding";
import Pricing from "./pages/Pricing";
import NotFound from "./pages/NotFound";

// Admin / Dashboard Pages
import AdminDashboard from "./admin/AdminDashboard";
import AdminRoutes from "./admin/AdminRoutes";

import "./index.css";

function SwarmDashboardRoute() {
  const [activeSection, setActiveSection] = useState("dashboard");
  return (
    <AdminDashboard activeSection={activeSection} setActiveSection={setActiveSection} />
  );
}

export default function App() {
  return (
    <LeoStatusProvider>
      <BrowserRouter>
        <Routes>
          {/* Public routes - wrapped in PublicLayout (Navbar + Footer) */}
          <Route element={<PublicLayout />}>
            <Route index element={<Home />} />
            <Route path="documentation" element={<Documentation />} />
            <Route path="playground" element={<Playground />} />
            <Route path="pricing" element={<Pricing />} />
            <Route path="auth" element={<Auth />} />
            <Route path="onboarding" element={<Onboarding />} />
          </Route>

          {/* Admin / Dashboard routes */}
          <Route path="admin" element={<AdminLayout />}>
            <Route index element={<Navigate to="/swarms" replace />} />
            <Route path="*" element={<AdminRoutes />} />
          </Route>

          <Route path="swarms" element={<SwarmDashboardRoute />} />

          {/* 404 Route */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </LeoStatusProvider>
  );
}