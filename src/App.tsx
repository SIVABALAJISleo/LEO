import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { AuthRedirect } from "@/components/auth/AuthRedirect";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { SystemBanner } from "@/components/ui/SystemBanner";

// Public Pages
import Index from "./pages/Index";
import Documentation from "./pages/Documentation";
import Playground from "./pages/Playground";
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import Pricing from "./pages/Pricing";
import NotFound from "./pages/NotFound";

// Legal Pages
import TermsOfService from "./pages/legal/TermsOfService";
import PrivacyPolicy from "./pages/legal/PrivacyPolicy";
import RefundPolicy from "./pages/legal/RefundPolicy";
import Disclaimer from "./pages/legal/Disclaimer";
import Contact from "./pages/legal/Contact";
import StatusPage from "./pages/system/StatusPage";

// Auth Pages
import Login from "./pages/auth/Login";
import Signup from "./pages/auth/Signup";
import ForgotPassword from "./pages/auth/ForgotPassword";
import VerifyOtp from "./pages/auth/VerifyOtp";
import ResetPassword from "./pages/auth/ResetPassword";
import Onboarding from "./pages/auth/Onboarding";

// Dashboard Pages
import Dashboard from "./pages/Dashboard";
import ApiPlayground from "./pages/documentation/ApiPlayground";
import Guides from "./pages/documentation/Guides";

// Admin Pages
import HyperAdminQueue from "./pages/HyperAdminQueue";
import SystemStatus from "./pages/SystemStatus";
import SecretAdminPage from "./pages/SecretAdminPage";
import ProductionReadiness from "./pages/admin/ProductionReadiness";
import RuntimeProofs from "./pages/admin/RuntimeProofs";
import GpuBypassDemo from "./pages/GpuBypassDemo";
import SystemDashboard from "./pages/SystemDashboard";
import OrchestrationExplorer from "./pages/OrchestrationExplorer";

// Billing Pages
import PricingPlansPage from "./pages/billing/PricingPlansPage";
import UsagePricingCalculatorPage from "./pages/billing/UsagePricingCalculatorPage";
import EnterpriseQuoteRequestPage from "./pages/billing/EnterpriseQuoteRequestPage";
import BillingManagePage from "./pages/billing/BillingManagePage";
import AdminBillingDashboard from "./pages/billing/AdminBillingDashboard";

import { NotificationProvider } from "@/contexts/NotificationContext";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, refetchOnWindowFocus: false },
    mutations: { retry: 0 },
  },
});

const App = () => (
  <ErrorBoundary>
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <NotificationProvider>
          <TooltipProvider>
            <Toaster />
            <Sonner />
            <BrowserRouter>
              <SystemBanner />
              <Routes>
                {/* Public Routes */}
                <Route path="/" element={<Index />} />
                <Route path="/docs" element={<Documentation />} />
                <Route path="/documentation" element={<Navigate to="/docs" replace />} />
                <Route path="/playground" element={<Playground />} />
                <Route path="/pricing" element={<Navigate to="/billing/pricing" replace />} />
                <Route path="/documentation/api-playground" element={<ApiPlayground />} />
                <Route path="/documentation/guides" element={<Guides />} />

                {/* Legal Routes */}
                <Route path="/legal/terms" element={<TermsOfService />} />
                <Route path="/legal/privacy" element={<PrivacyPolicy />} />
                <Route path="/legal/refund" element={<RefundPolicy />} />
                <Route path="/legal/disclaimer" element={<Disclaimer />} />
                <Route path="/legal/contact" element={<Contact />} />
                {/* Convenience redirects */}
                <Route path="/terms" element={<Navigate to="/legal/terms" replace />} />
                <Route path="/privacy" element={<Navigate to="/legal/privacy" replace />} />
                <Route path="/contact" element={<Navigate to="/legal/contact" replace />} />

                {/* System Status */}
                <Route path="/system/status" element={<StatusPage />} />
                <Route path="/status" element={<Navigate to="/system/status" replace />} />

                {/* Billing Routes */}
                <Route path="/billing/pricing" element={<PricingPlansPage />} />
                <Route path="/billing/calculator" element={<UsagePricingCalculatorPage />} />
                <Route path="/billing/enterprise" element={<EnterpriseQuoteRequestPage />} />
                <Route path="/billing/manage" element={<ProtectedRoute><BillingManagePage /></ProtectedRoute>} />

                {/* Admin Billing Dashboard - Secret URL */}
                <Route path="/hyper-admin-billing-secret" element={<ProtectedRoute><AdminBillingDashboard /></ProtectedRoute>} />

                {/* Auth Routes - Redirect if already authenticated */}
                <Route path="/auth" element={<Navigate to="/auth/login" replace />} />
                <Route
                  path="/auth/login"
                  element={
                    <AuthRedirect>
                      <Login />
                    </AuthRedirect>
                  }
                />
                <Route
                  path="/auth/signup"
                  element={
                    <AuthRedirect>
                      <Signup />
                    </AuthRedirect>
                  }
                />
                <Route
                  path="/auth/forgot-password"
                  element={
                    <AuthRedirect>
                      <ForgotPassword />
                    </AuthRedirect>
                  }
                />
                <Route
                  path="/auth/verify-reset"
                  element={
                    <AuthRedirect>
                      <VerifyOtp />
                    </AuthRedirect>
                  }
                />
                <Route path="/auth/reset-password" element={<ResetPassword />} />
                <Route
                  path="/auth/onboarding"
                  element={
                    <ProtectedRoute>
                      <Onboarding />
                    </ProtectedRoute>
                  }
                />

                {/* Protected Dashboard Routes */}
                <Route
                  path="/dashboard"
                  element={<Navigate to="/dashboard/home" replace />}
                />
                <Route
                  path="/dashboard/*"
                  element={
                    <ProtectedRoute>
                      <Dashboard />
                    </ProtectedRoute>
                  }
                />

                {/* Admin Routes - Protected */}
                <Route
                  path="/hyper-admin-queue"
                  element={
                    <ProtectedRoute>
                      <HyperAdminQueue />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/admin/production-readiness"
                  element={
                    <ProtectedRoute>
                      <ProductionReadiness />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/admin/runtime-proofs"
                  element={
                    <ProtectedRoute>
                      <RuntimeProofs />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/system-status"
                  element={
                    <ProtectedRoute>
                      <SystemStatus />
                    </ProtectedRoute>
                  }
                />
                {/* Secret Admin Page - Not linked anywhere */}
                <Route
                  path="/hyper-admin-987654321-secret"
                  element={
                    <ProtectedRoute>
                      <SecretAdminPage />
                    </ProtectedRoute>
                  }
                />
                <Route path="/gpu-bypass-demo" element={<GpuBypassDemo />} />
                <Route
                  path="/admin/dashboard"
                  element={
                    <ProtectedRoute>
                      <SystemDashboard />
                    </ProtectedRoute>
                  }
                />

                <Route
                  path="/admin/explorer"
                  element={
                    <ProtectedRoute>
                      <OrchestrationExplorer />
                    </ProtectedRoute>
                  }
                />
                {/* Catch-all */}
                <Route path="*" element={<NotFound />} />
              </Routes>
            </BrowserRouter>
          </TooltipProvider>
        </NotificationProvider>
      </AuthProvider>
    </QueryClientProvider>
  </ErrorBoundary>
);

export default App;