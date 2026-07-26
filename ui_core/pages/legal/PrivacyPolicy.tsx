import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Footer } from "@/components/Footer";
import { Navbar } from "@/components/Navbar";

const PRIVACY_VERSION = "1.0.0";
const EFFECTIVE_DATE = "2026-01-09";

const PrivacyPolicy = () => {
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
          <h1>Privacy Policy</h1>
          <p className="text-muted-foreground">
            Version {PRIVACY_VERSION} · Effective {EFFECTIVE_DATE}
          </p>

          <h2>1. Information We Collect</h2>

          <h3>Account Information</h3>
          <p>When you create an account, we collect:</p>
          <ul>
            <li>Email address</li>
            <li>Name (optional)</li>
            <li>Company name (optional)</li>
          </ul>

          <h3>Usage Data</h3>
          <p>We automatically collect:</p>
          <ul>
            <li>Job submission and processing history</li>
            <li>Performance metrics and logs</li>
            <li>Device and browser information</li>
            <li>IP address</li>
          </ul>

          <h3>Job Data</h3>
          <p>
            We process the input data you submit for jobs. This data is used solely to provide the
            Service and is not shared with third parties.
          </p>

          <h2>2. How We Use Your Information</h2>
          <ul>
            <li>To provide and maintain the Service</li>
            <li>To process and complete your jobs</li>
            <li>To send important service notifications</li>
            <li>To improve and optimize the Service</li>
            <li>To detect and prevent abuse</li>
          </ul>

          <h2>3. Data Retention</h2>
          <ul>
            <li>Account data: Retained while your account is active</li>
            <li>Job data: Retained for 30 days after completion</li>
            <li>Logs: Retained for 90 days</li>
            <li>Audit records: Retained for 1 year</li>
          </ul>

          <h2>4. Data Security</h2>
          <p>We implement industry-standard security measures including:</p>
          <ul>
            <li>Encryption in transit (TLS)</li>
            <li>Encryption at rest</li>
            <li>Access controls and authentication</li>
            <li>Regular security audits</li>
          </ul>

          <h2>5. Your Rights</h2>
          <p>You have the right to:</p>
          <ul>
            <li>Access your personal data</li>
            <li>Request correction of inaccurate data</li>
            <li>Request deletion of your data</li>
            <li>Export your data</li>
            <li>Opt out of marketing communications</li>
          </ul>

          <h2>6. Third-Party Services</h2>
          <p>We use the following third-party services:</p>
          <ul>
            <li>Payment processing (Stripe, Razorpay)</li>
            <li>Analytics (privacy-focused)</li>
            <li>Infrastructure providers</li>
          </ul>

          <h2>7. Cookies</h2>
          <p>
            We use essential cookies for authentication and session management. We do not use
            tracking cookies for advertising.
          </p>

          <h2>8. Children's Privacy</h2>
          <p>
            The Service is not intended for users under 18. We do not knowingly collect data from
            children.
          </p>

          <h2>9. Changes to This Policy</h2>
          <p>We will notify you of significant changes via email or in-app notification.</p>

          <h2>10. Contact Us</h2>
          <p>
            For privacy inquiries:{" "}
            <a href="mailto:privacy@hyper.app" className="text-primary hover:underline">
              privacy@hyper.app
            </a>
          </p>

          <div className="mt-12 p-4 bg-muted rounded-lg">
            <p className="text-sm text-muted-foreground">
              Document Hash: {btoa(PRIVACY_VERSION + EFFECTIVE_DATE).slice(0, 16)}
            </p>
          </div>
        </article>
      </div>
      <Footer />
    </div>
  );
};

export default PrivacyPolicy;
