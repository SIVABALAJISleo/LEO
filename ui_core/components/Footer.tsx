import { Link } from 'react-router-dom';
import { Zap, Github, Twitter, Linkedin, Mail } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="border-t border-border bg-card/50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
          {/* Brand */}
          <div className="col-span-2 md:col-span-1">
            <Link to="/" className="flex items-center space-x-2 mb-4">
              <Zap className="h-6 w-6 text-primary" />
              <span className="text-lg font-bold">HYPER</span>
            </Link>
            <p className="text-sm text-muted-foreground mb-4">
              GPU Need-Elimination Platform. Smarter. Faster. Everywhere.
            </p>
            <div className="flex items-center space-x-3">
              <a href="#" className="text-muted-foreground hover:text-primary transition-colors">
                <Twitter className="h-5 w-5" />
              </a>
              <a href="#" className="text-muted-foreground hover:text-primary transition-colors">
                <Github className="h-5 w-5" />
              </a>
              <a href="#" className="text-muted-foreground hover:text-primary transition-colors">
                <Linkedin className="h-5 w-5" />
              </a>
              <a href="mailto:hello@hyper.app" className="text-muted-foreground hover:text-primary transition-colors">
                <Mail className="h-5 w-5" />
              </a>
            </div>
          </div>

          {/* Product */}
          <div>
            <h3 className="font-semibold mb-4">Product</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/pricing" className="text-muted-foreground hover:text-foreground transition-colors">
                  Pricing
                </Link>
              </li>
              <li>
                <Link to="/docs" className="text-muted-foreground hover:text-foreground transition-colors">
                  Documentation
                </Link>
              </li>
              <li>
                <Link to="/playground" className="text-muted-foreground hover:text-foreground transition-colors">
                  API Playground
                </Link>
              </li>
              <li>
                <Link to="/system/status" className="text-muted-foreground hover:text-foreground transition-colors">
                  System Status
                </Link>
              </li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h3 className="font-semibold mb-4">Company</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/legal/contact" className="text-muted-foreground hover:text-foreground transition-colors">
                  Contact
                </Link>
              </li>
              <li>
                <Link to="/billing/enterprise" className="text-muted-foreground hover:text-foreground transition-colors">
                  Enterprise
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h3 className="font-semibold mb-4">Legal</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/legal/terms" className="text-muted-foreground hover:text-foreground transition-colors">
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link to="/legal/privacy" className="text-muted-foreground hover:text-foreground transition-colors">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link to="/legal/refund" className="text-muted-foreground hover:text-foreground transition-colors">
                  Refund Policy
                </Link>
              </li>
              <li>
                <Link to="/legal/disclaimer" className="text-muted-foreground hover:text-foreground transition-colors">
                  Disclaimer
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom */}
        <div className="pt-8 border-t border-border flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-sm text-muted-foreground">
            © {new Date().getFullYear()} HYPER. All rights reserved.
          </p>
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            <span>v1.0.0 STABLE</span>
            <span>•</span>
            <span>97-98% Production Ready</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export { Footer };
