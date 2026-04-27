import { Link } from 'react-router-dom';
import { ArrowLeft, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Footer } from '@/components/Footer';
import { Navbar } from '@/components/Navbar';

const DISCLAIMER_VERSION = '1.0.0';
const EFFECTIVE_DATE = '2026-01-09';

const Disclaimer = () => {
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
          <h1>Disclaimer</h1>
          <p className="text-muted-foreground">
            Version {DISCLAIMER_VERSION} · Effective {EFFECTIVE_DATE}
          </p>

          <Alert variant="default" className="my-6">
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>Beta Service</AlertTitle>
            <AlertDescription>
              HYPER is currently in beta. Features and performance may vary.
            </AlertDescription>
          </Alert>

          <h2>1. Service Disclaimer</h2>
          <p>
            THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND,
            EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO IMPLIED WARRANTIES OF
            MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.
          </p>

          <h2>2. No Guarantee of Results</h2>
          <p>
            We do not guarantee specific performance improvements, cost savings, or outcomes.
            Results depend on many factors including your workload characteristics, input data,
            and configuration.
          </p>

          <h2>3. Beta Features</h2>
          <p>
            Certain features are marked as "beta" or "experimental." These features:
          </p>
          <ul>
            <li>May be modified or discontinued without notice</li>
            <li>May have limited support</li>
            <li>Should not be relied upon for critical production workloads</li>
          </ul>

          <h2>4. Third-Party Content</h2>
          <p>
            The Service may integrate with or link to third-party services. We are not
            responsible for the availability, accuracy, or content of these services.
          </p>

          <h2>5. Accuracy of Information</h2>
          <p>
            While we strive to provide accurate information, we make no warranties about the
            completeness, reliability, or accuracy of information on this site or produced
            by the Service.
          </p>

          <h2>6. Professional Advice</h2>
          <p>
            The Service is not a substitute for professional advice. You should consult
            appropriate professionals for specific advice related to your circumstances.
          </p>

          <h2>7. Uptime and Availability</h2>
          <p>
            We do not guarantee 100% uptime. While we strive for high availability, the
            Service may be temporarily unavailable for maintenance, updates, or unexpected issues.
          </p>

          <h2>8. Data Loss</h2>
          <p>
            While we implement data protection measures, we are not responsible for data loss.
            You are responsible for maintaining your own backups.
          </p>

          <h2>9. Limitation of Liability</h2>
          <p>
            IN NO EVENT SHALL HYPER, ITS OFFICERS, DIRECTORS, EMPLOYEES, OR AGENTS BE LIABLE
            FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES ARISING
            FROM YOUR USE OF THE SERVICE.
          </p>

          <h2>10. Indemnification</h2>
          <p>
            You agree to indemnify and hold harmless HYPER from any claims arising from your
            use of the Service or violation of these terms.
          </p>

          <h2>11. Changes</h2>
          <p>
            We reserve the right to modify this disclaimer at any time. Changes are effective
            upon posting.
          </p>

          <div className="mt-12 p-4 bg-muted rounded-lg">
            <p className="text-sm text-muted-foreground">
              Document Hash: {btoa(DISCLAIMER_VERSION + EFFECTIVE_DATE).slice(0, 16)}
            </p>
          </div>
        </article>
      </div>
      <Footer />
    </div>
  );
};

export default Disclaimer;
