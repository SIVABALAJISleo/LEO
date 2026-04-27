import { Link } from 'react-router-dom';
import { ArrowLeft, Mail, MessageSquare, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Footer } from '@/components/Footer';
import { Navbar } from '@/components/Navbar';

const CONTACT_VERSION = '1.0.0';

const Contact = () => {
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
          <h1>Contact Us</h1>
          <p className="text-muted-foreground">
            Version {CONTACT_VERSION}
          </p>

          <div className="grid gap-6 md:grid-cols-2 not-prose mt-8">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Mail className="h-5 w-5 text-primary" />
                  General Inquiries
                </CardTitle>
                <CardDescription>
                  For general questions and information
                </CardDescription>
              </CardHeader>
              <CardContent>
                <a 
                  href="mailto:hello@hyper.app" 
                  className="text-primary hover:underline font-medium"
                >
                  hello@hyper.app
                </a>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="h-5 w-5 text-primary" />
                  Technical Support
                </CardTitle>
                <CardDescription>
                  For technical issues and bug reports
                </CardDescription>
              </CardHeader>
              <CardContent>
                <a 
                  href="mailto:support@hyper.app" 
                  className="text-primary hover:underline font-medium"
                >
                  support@hyper.app
                </a>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Mail className="h-5 w-5 text-primary" />
                  Billing Questions
                </CardTitle>
                <CardDescription>
                  For payment and subscription inquiries
                </CardDescription>
              </CardHeader>
              <CardContent>
                <a 
                  href="mailto:billing@hyper.app" 
                  className="text-primary hover:underline font-medium"
                >
                  billing@hyper.app
                </a>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5 text-primary" />
                  Response Time
                </CardTitle>
                <CardDescription>
                  Expected response times
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  We typically respond within 24-48 business hours.
                </p>
              </CardContent>
            </Card>
          </div>

          <h2 className="mt-12">Legal Notices</h2>
          <p>
            For legal inquiries, please contact{' '}
            <a href="mailto:legal@hyper.app" className="text-primary hover:underline">
              legal@hyper.app
            </a>
          </p>

          <h2>Related Pages</h2>
          <ul>
            <li>
              <Link to="/legal/terms" className="text-primary hover:underline">
                Terms of Service
              </Link>
            </li>
            <li>
              <Link to="/legal/privacy" className="text-primary hover:underline">
                Privacy Policy
              </Link>
            </li>
            <li>
              <Link to="/legal/refund" className="text-primary hover:underline">
                Refund Policy
              </Link>
            </li>
            <li>
              <Link to="/system/status" className="text-primary hover:underline">
                System Status
              </Link>
            </li>
          </ul>
        </article>
      </div>
      <Footer />
    </div>
  );
};

export default Contact;
