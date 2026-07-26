import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Footer } from "@/components/Footer";
import { Navbar } from "@/components/Navbar";

const TERMS_VERSION = "1.0.0";
const EFFECTIVE_DATE = "2026-01-09";

const TermsOfService = () => {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />
      <div className="flex-1 max-w-4xl mx-auto px-4 py-12 pt-24">
        <Link to="/">
          <Button variant="ghost" className="mb-8">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Home
          </Button>
        </Link>

        <article className="prose prose-slate dark:prose-invert max-w-none">
          <h1>Terms of Service</h1>
          <p className="text-muted-foreground">
            Version {TERMS_VERSION} · Effective {EFFECTIVE_DATE}
          </p>

          <h2>1. Acceptance of Terms</h2>
          <p>
            By accessing or using the HYPER platform ("Service"), you agree to be bound by these
            Terms of Service. If you do not agree to these terms, you may not use the Service.
          </p>

          <h2>2. Description of Service</h2>
          <p>
            HYPER provides GPU optimization and computation services through a cloud-based platform.
            The Service includes job processing, performance optimization, and related tools.
          </p>

          <h2>3. User Accounts</h2>
          <p>You are responsible for:</p>
          <ul>
            <li>Maintaining the confidentiality of your account credentials</li>
            <li>All activities that occur under your account</li>
            <li>Notifying us immediately of any unauthorized use</li>
          </ul>

          <h2>4. Acceptable Use</h2>
          <p>You agree not to:</p>
          <ul>
            <li>Use the Service for any illegal or unauthorized purpose</li>
            <li>Attempt to gain unauthorized access to any part of the Service</li>
            <li>Interfere with or disrupt the Service</li>
            <li>Submit malicious code or attempt to exploit vulnerabilities</li>
            <li>Exceed your allocated resource quotas</li>
          </ul>

          <h2>5. Service Availability</h2>
          <p>
            The Service is provided on an "as-is" and "as-available" basis. We do not guarantee
            uninterrupted access. The Service is currently in <strong>beta</strong> status, and
            features may change without notice.
          </p>

          <h2>6. Data and Privacy</h2>
          <p>
            Your use of the Service is subject to our{" "}
            <Link to="/legal/privacy" className="text-primary hover:underline">
              Privacy Policy
            </Link>
            . By using the Service, you consent to the collection and use of data as described.
          </p>

          <h2>7. Payment Terms</h2>
          <p>
            Paid subscriptions are billed in advance. Refund eligibility is described in our{" "}
            <Link to="/legal/refund" className="text-primary hover:underline">
              Refund Policy
            </Link>
            .
          </p>

          <h2>8. Limitation of Liability</h2>
          <p>
            To the maximum extent permitted by law, HYPER shall not be liable for any indirect,
            incidental, special, consequential, or punitive damages arising from your use of the
            Service.
          </p>

          <h2>9. Changes to Terms</h2>
          <p>
            We may modify these terms at any time. Continued use of the Service after changes
            constitutes acceptance of the new terms.
          </p>

          <h2>10. Contact</h2>
          <p>
            For questions about these terms, contact us at{" "}
            <a href="mailto:legal@hyper.app" className="text-primary hover:underline">
              legal@hyper.app
            </a>
          </p>

          <div className="mt-12 p-4 bg-muted rounded-lg">
            <p className="text-sm text-muted-foreground">
              Document Hash: {btoa(TERMS_VERSION + EFFECTIVE_DATE).slice(0, 16)}
            </p>
          </div>
        </article>
      </div>
      <Footer />
    </div>
  );
};

export default TermsOfService;
