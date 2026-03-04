import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { CheckCircle2, Zap, TrendingUp, Shield } from "lucide-react";
import { Link } from "react-router-dom";

const Pricing = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-display font-bold mb-4">
            Simple, <span className="text-primary">Transparent</span> Pricing
          </h1>
          <p className="text-xl text-foreground/70 max-w-2xl mx-auto">
            Start free, scale as you grow. No hidden fees, no surprises.
          </p>
        </div>

        {/* Pricing Tiers */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-16">
          {[
            {
              name: "Free",
              price: "$0",
              period: "/month",
              calls: "5 concurrent jobs",
              features: [
                "Basic dashboard access",
                "Standard processing",
                "Community support",
                "10 GB storage",
              ],
              cta: "Get Started",
              highlighted: false,
            },
            {
              name: "HYPER Pro",
              price: "$49–$85",
              period: "/month",
              calls: "100 concurrent jobs",
              targetUsers: "Developers · Creators · Indie teams",
              features: [
                "Optimized shared outcomes",
                "Priority processing queue",
                "Advanced optimization modules",
                "500 GB storage",
                "Full API access",
              ],
              cta: "Start Pro",
              highlighted: true,
            },
            {
              name: "HYPER Heavy",
              price: "$249–$499",
              period: "/month",
              calls: "Unlimited jobs",
              targetUsers: "AI teams · Studios · Research orgs",
              features: [
                "Priority outcome delivery",
                "Deterministic execution",
                "Compliance & audit support",
                "24/7 priority support",
                "SLA guarantee (99.9%)",
              ],
              cta: "Start Heavy",
              highlighted: false,
            },
            {
              name: "Enterprise",
              price: "Custom",
              period: "",
              calls: "Custom configuration",
              features: [
                "Everything in Heavy",
                "On-premise deployment",
                "Custom SLAs",
                "Dedicated infrastructure",
                "White-glove onboarding",
              ],
              cta: "Contact Sales",
              highlighted: false,
            },
          ].map((tier, idx) => (
            <Card
              key={idx}
              className={`p-6 ${
                tier.highlighted
                  ? "border-primary shadow-glow scale-105 relative"
                  : "border-border hover:border-primary/50"
              } transition-all`}
            >
              {tier.highlighted && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <div className="bg-gradient-primary text-primary-foreground text-xs font-bold py-1.5 px-4 rounded-full">
                    MOST POPULAR
                  </div>
                </div>
              )}
              
              <h3 className="text-2xl font-bold mb-2">{tier.name}</h3>
              {tier.targetUsers && (
                <p className="text-xs text-foreground/60 mb-2">{tier.targetUsers}</p>
              )}
              <div className="mb-4">
                <span className="text-3xl font-display font-bold text-primary">{tier.price}</span>
                <span className="text-foreground/70">{tier.period}</span>
              </div>
              <p className="text-sm font-medium text-primary mb-6">{tier.calls}</p>
              
              <ul className="space-y-3 mb-8">
                {tier.features.map((feature, i) => (
                  <li key={i} className="flex items-start text-sm text-foreground/80">
                    <CheckCircle2 className="h-4 w-4 text-primary mr-2 mt-0.5 flex-shrink-0" />
                    {feature}
                  </li>
                ))}
              </ul>

              <Link to={tier.name === 'Enterprise' ? '/billing/enterprise' : '/auth/signup'}>
                <Button
                  className={`w-full ${
                    tier.highlighted
                      ? "bg-gradient-primary shadow-glow"
                      : "bg-secondary hover:bg-secondary/80"
                  }`}
                >
                  {tier.cta}
                </Button>
              </Link>
            </Card>
          ))}
        </div>

        {/* Usage-Based Pricing */}
        <Card className="p-8 mb-16 bg-card border-border">
          <h2 className="text-3xl font-bold mb-6 text-center">
            Usage-Based <span className="text-primary">Pricing</span>
          </h2>
          <p className="text-center text-foreground/70 mb-8">
            Additional charges apply when you exceed your plan limits
          </p>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 font-semibold">Operation</th>
                  <th className="text-left py-3 px-4 font-semibold">Unit</th>
                  <th className="text-right py-3 px-4 font-semibold">Price</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { operation: "GPU Operations", unit: "per 100 ops", price: "$0.0006" },
                  { operation: "AI Inference", unit: "per call", price: "$0.001" },
                  { operation: "Rendering Task", unit: "per task", price: "$0.002" },
                  { operation: "Frame Generation", unit: "per batch", price: "$0.012" },
                  { operation: "Training Compute", unit: "per hour", price: "$0.006" },
                ].map((row, idx) => (
                  <tr key={idx} className="border-b border-border/50 hover:bg-muted/30 transition-colors">
                    <td className="py-3 px-4 font-medium">{row.operation}</td>
                    <td className="py-3 px-4 text-foreground/70">{row.unit}</td>
                    <td className="py-3 px-4 text-right text-primary font-semibold">{row.price}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        {/* FAQ */}
        <Card className="p-8 mb-16 bg-card border-border">
          <h2 className="text-3xl font-bold mb-8 text-center">
            Frequently Asked <span className="text-primary">Questions</span>
          </h2>

          <div className="space-y-6 max-w-3xl mx-auto">
            {[
              {
                q: "Can I change my plan anytime?",
                a: "Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately.",
              },
              {
                q: "What happens if I exceed my API call limit?",
                a: "You'll be charged the usage-based rate for additional calls. You can set spending limits in your dashboard.",
              },
              {
                q: "Do you offer refunds?",
                a: "Yes, we offer a 30-day money-back guarantee for all paid plans. No questions asked.",
              },
              {
                q: "Is there a discount for annual billing?",
                a: "Yes! Save 20% when you pay annually. Contact sales for enterprise volume discounts.",
              },
            ].map((faq, idx) => (
              <div key={idx} className="pb-6 border-b border-border last:border-0">
                <h3 className="text-lg font-semibold mb-2">{faq.q}</h3>
                <p className="text-foreground/70">{faq.a}</p>
              </div>
            ))}
          </div>
        </Card>

        {/* CTA Section */}
        <Card className="p-12 bg-gradient-glow border-border text-center">
          <h2 className="text-3xl font-display font-bold mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-foreground/70 mb-8 max-w-2xl mx-auto">
            Start with 100 free API calls per day. No credit card required.
            Upgrade anytime as your needs grow.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/auth/signup">
              <Button size="lg" className="bg-gradient-primary shadow-glow">
                <Zap className="mr-2 h-5 w-5" />
                Start Free Trial
              </Button>
            </Link>
            <Link to="/docs">
              <Button size="lg" variant="outline">
                View Documentation
              </Button>
            </Link>
          </div>
        </Card>

        <Footer />
      </div>
    </div>
  );
};

export default Pricing;
