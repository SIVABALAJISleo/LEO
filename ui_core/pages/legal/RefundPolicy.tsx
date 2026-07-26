import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Footer } from "@/components/Footer";
import { Navbar } from "@/components/Navbar";

const REFUND_VERSION = "1.0.0";
const EFFECTIVE_DATE = "2026-01-09";

const RefundPolicy = () => {
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
          <h1>Refund Policy</h1>
          <p className="text-muted-foreground">
            Version {REFUND_VERSION} · Effective {EFFECTIVE_DATE}
          </p>

          <h2>1. Subscription Refunds</h2>

          <h3>Monthly Subscriptions</h3>
          <p>You may cancel your monthly subscription at any time. Upon cancellation:</p>
          <ul>
            <li>Your subscription remains active until the end of the billing period</li>
            <li>No partial refunds are provided for unused time</li>
            <li>You retain access to your data for 30 days after cancellation</li>
          </ul>

          <h3>Annual Subscriptions</h3>
          <p>
            Annual subscriptions may be eligible for a prorated refund within the first 30 days.
            After 30 days, refunds are handled on a case-by-case basis.
          </p>

          <h2>2. Usage-Based Charges</h2>
          <p>
            Usage-based charges (compute time, API calls) are non-refundable once consumed. However,
            we may issue credits for:
          </p>
          <ul>
            <li>System errors that caused job failures</li>
            <li>Billing errors on our part</li>
            <li>Service outages exceeding our SLA</li>
          </ul>

          <h2>3. Eligible Refund Requests</h2>
          <p>We will consider refunds for:</p>
          <ul>
            <li>Duplicate charges</li>
            <li>Unauthorized charges (with fraud verification)</li>
            <li>Service significantly different from advertised</li>
            <li>Extended service outages</li>
          </ul>

          <h2>4. How to Request a Refund</h2>
          <ol>
            <li>
              Email{" "}
              <a href="mailto:billing@hyper.app" className="text-primary hover:underline">
                billing@hyper.app
              </a>{" "}
              with your request
            </li>
            <li>Include your account email and transaction ID</li>
            <li>Describe the reason for your refund request</li>
            <li>We will respond within 3 business days</li>
          </ol>

          <h2>5. Refund Timeline</h2>
          <ul>
            <li>Credit card refunds: 5-10 business days</li>
            <li>Account credits: Immediate</li>
            <li>Bank transfers: 10-15 business days</li>
          </ul>

          <h2>6. Non-Refundable Items</h2>
          <ul>
            <li>Setup fees (if applicable)</li>
            <li>Custom development work</li>
            <li>Already-consumed compute resources</li>
            <li>Third-party fees</li>
          </ul>

          <h2>7. Chargebacks</h2>
          <p>
            If you initiate a chargeback without first contacting us, we reserve the right to
            suspend your account pending resolution.
          </p>

          <h2>8. Contact</h2>
          <p>
            For billing questions:{" "}
            <a href="mailto:billing@hyper.app" className="text-primary hover:underline">
              billing@hyper.app
            </a>
          </p>

          <div className="mt-12 p-4 bg-muted rounded-lg">
            <p className="text-sm text-muted-foreground">
              Document Hash: {btoa(REFUND_VERSION + EFFECTIVE_DATE).slice(0, 16)}
            </p>
          </div>
        </article>
      </div>
      <Footer />
    </div>
  );
};

export default RefundPolicy;
