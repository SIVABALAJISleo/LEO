import React, { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { LeoStatusProvider } from "./contexts/LeoStatusContext";

// Layouts
import PublicLayout from "./layouts/PublicLayout";
import AdminLayout from "./layouts/AdminLayout";

// Public Pages (Lazy Loaded)
const Home = React.lazy(() => import("./pages/Home"));
const Documentation = React.lazy(() => import("./pages/Documentation"));
const Playground = React.lazy(() => import("./pages/Playground"));
const Auth = React.lazy(() => import("./pages/Auth"));
const Onboarding = React.lazy(() => import("./pages/Onboarding"));
const Pricing = React.lazy(() => import("./pages/Pricing"));
const NotFound = React.lazy(() => import("./pages/NotFound"));

// Admin / Dashboard Pages (Lazy Loaded)
const AdminDashboard = React.lazy(() => import("./admin/AdminDashboard"));
const AdminRoutes = React.lazy(() => import("./admin/AdminRoutes"));

import "./index.css";

function PageLoader() {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#76B900]"></div>
    </div>
  );
}

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
        <React.Suspense fallback={<PageLoader />}>
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
        </React.Suspense>
      </BrowserRouter>
    </LeoStatusProvider>
  );
}