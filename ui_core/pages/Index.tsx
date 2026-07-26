import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Link } from "react-router-dom";
import {
  Zap,
  Cloud,
  Brain,
  Gauge,
  Shield,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  TrendingUp,
  Code,
  Layers,
  Activity,
  CheckCircle2,
  Cpu,
} from "lucide-react";
import heroBackground from "@/assets/hero-gpu-background.jpg";
import { HeroParticles } from "@/components/HeroParticles";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* Background Image */}
        <div
          className="absolute inset-0 bg-cover bg-center bg-no-repeat"
          style={{ backgroundImage: `url(${heroBackground})` }}
        />
        {/* Dark overlay with glassmorphism depth */}
        <div className="absolute inset-0 bg-background/60 backdrop-blur-[2px]" />
        {/* Background Effects */}
        <div className="absolute inset-0 bg-gradient-glow" />
        {/* Animated Particles */}
        <HeroParticles />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16 text-center">
          <div className="animate-fade-in-up">
            <div className="inline-flex items-center px-4 py-2 rounded-full bg-primary/10 border border-primary/30 mb-8 backdrop-blur-md animate-pulse-glow">
              <Zap className="h-4 w-4 text-primary mr-2" />
              <span className="text-sm font-bold text-primary tracking-wide uppercase">
                Certified Production Grade • MNC Standard Architecture
              </span>
            </div>

            <h1 className="text-5xl sm:text-6xl lg:text-8xl font-black mb-6 leading-tight tracking-tighter">
              <span className="text-foreground">Smarter. Faster.</span>
              <br />
              <span className="text-primary hyper-glow-text bg-clip-text">Everywhere.</span>
            </h1>

            <p className="text-xl text-foreground/70 max-w-3xl mx-auto mb-8">
              Achieve high-end GPU performance using intelligent software algorithms. AI inference,
              4K rendering, VR processing, and large model training—all optimized for any hardware.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
              <Link to="/auth/signup">
                <Button
                  size="lg"
                  className="bg-gradient-primary shadow-glow hover:scale-105 transition-transform"
                >
                  Get Started Free
                  <Zap className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              <Link to="/docs">
                <Button size="lg" variant="outline">
                  View Documentation
                  <Code className="ml-2 h-5 w-5" />
                </Button>
              </Link>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
              {[
                { value: "98%+", label: "Performance Efficiency" },
                { value: "52", label: "Smart Modules" },
                { value: "$0", label: "Hardware Cost" },
                { value: "1000s+", label: "Concurrent Users" },
              ].map((stat, idx) => (
                <div
                  key={idx}
                  className="text-center animate-fade-in"
                  style={{ animationDelay: `${idx * 100}ms` }}
                >
                  <div className="text-3xl font-bold text-primary mb-1">{stat.value}</div>
                  <div className="text-sm text-foreground/60">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-card/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-foreground mb-4">
              6 Major Challenges <span className="text-primary">Solved</span>
            </h2>
            <p className="text-xl text-foreground/70 max-w-2xl mx-auto">
              What traditional hardware approaches can't solve, intelligent software can achieve
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: Gauge,
                title: "4K/240 FPS Rendering",
                description: "High-quality rendering with adaptive layer system and temporal reuse",
                result: "✓ Achieved",
              },
              {
                icon: Activity,
                title: "VR <2ms Latency",
                description: "Predictive rendering with timewarp correction for instant response",
                result: "✓ Achieved",
              },
              {
                icon: Layers,
                title: "Ray Tracing Quality",
                description: "98-100% visual quality using neural approximation techniques",
                result: "✓ Achieved",
              },
              {
                icon: Brain,
                title: "Large Model Training",
                description: "95% efficiency with distributed streaming and quantization",
                result: "✓ Achieved",
              },
              {
                icon: Cloud,
                title: "Massive Concurrency",
                description: "Smart queuing, caching, and prediction for thousands of users",
                result: "✓ Achieved",
              },
              {
                icon: Cpu,
                title: "Compute Throughput",
                description: "640× speedup with SIMD, quantization, and lookup tables",
                result: "✓ Achieved",
              },
            ].map((feature, idx) => (
              <Card
                key={idx}
                className="p-6 bg-card border-border hover:border-primary/50 transition-all hover:shadow-glow group animate-fade-in"
                style={{ animationDelay: `${idx * 100}ms` }}
              >
                <feature.icon className="h-10 w-10 text-primary mb-4 group-hover:scale-110 transition-transform" />
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-foreground/70 mb-3">{feature.description}</p>
                <div className="flex items-center text-primary font-medium">
                  <CheckCircle2 className="h-4 w-4 mr-2" />
                  {feature.result}
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Benchmarks Section */}
      <section className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-foreground mb-4">
              GPU <span className="text-primary">Need-Neutralization</span> Results
            </h2>
            <p className="text-xl text-foreground/70">
              How we deliver equivalent outcomes without GPU dependency
            </p>
          </div>

          <Card className="p-8 bg-card border-border">
            <div className="table-responsive">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left py-4 px-4 font-semibold">Task</th>
                    <th className="text-left py-4 px-4 font-semibold">Traditional Approach</th>
                    <th className="text-left py-4 px-4 font-semibold">HYPER Outcome</th>
                    <th className="text-left py-4 px-4 font-semibold">GPU Need</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    {
                      task: "AI Inference",
                      trad: "Requires GPU",
                      hyper: "Distilled models + caching",
                      need: "Neutralized",
                    },
                    {
                      task: "4K Video Preview",
                      trad: "Full GPU render",
                      hyper: "Proxy + async refinement",
                      need: "Neutralized",
                    },
                    {
                      task: "Ray Tracing",
                      trad: "Hardware RT cores",
                      hyper: "Raster preview + cloud stream",
                      need: "Optional",
                    },
                    {
                      task: "Model Training",
                      trad: "Multi-GPU cluster",
                      hyper: "LoRA + pretrained delegation",
                      need: "Delegated",
                    },
                    {
                      task: "VR Rendering",
                      trad: "<2ms GPU latency",
                      hyper: "Predictive timewarp + streaming",
                      need: "Optional",
                    },
                    {
                      task: "3D Processing",
                      trad: "Full GPU compute",
                      hyper: "LOD preview + progressive load",
                      need: "Neutralized",
                    },
                  ].map((row, idx) => (
                    <tr
                      key={idx}
                      className="border-b border-border/50 hover:bg-muted/30 transition-colors"
                    >
                      <td className="py-4 px-4 font-medium">{row.task}</td>
                      <td className="py-4 px-4 text-foreground/70">{row.trad}</td>
                      <td className="py-4 px-4 text-primary font-medium">{row.hyper}</td>
                      <td className="py-4 px-4">
                        <span
                          className={`px-3 py-1 rounded-full text-sm font-medium ${
                            row.need === "Neutralized"
                              ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                              : row.need === "Optional"
                                ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                                : "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400"
                          }`}
                        >
                          {row.need}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="text-sm text-muted-foreground mt-4 text-center">
              GPU replacement: ❌ NOT CLAIMED • GPU dependency neutralized: ✅ YES • Practical
              coverage: 98-99%
            </p>
          </Card>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-24 bg-card/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-foreground mb-4">
              Simple <span className="text-primary">Pricing</span>
            </h2>
            <p className="text-xl text-foreground/70">Start free, scale as you grow</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {[
              {
                name: "Free",
                price: "$0",
                period: "/month",
                description: "For individuals getting started",
                features: [
                  "Basic dashboard access",
                  "Up to 5 concurrent jobs",
                  "Community support",
                  "10 GB storage",
                ],
              },
              {
                name: "HYPER Pro",
                price: "$49",
                period: "/month",
                description: "For professionals and teams",
                features: [
                  "Priority job processing",
                  "Up to 50 concurrent jobs",
                  "Email support (24h)",
                  "100 GB storage",
                  "Advanced modules",
                ],
                popular: true,
              },
              {
                name: "Enterprise",
                price: "Custom",
                period: "",
                description: "For large organizations",
                features: [
                  "Dedicated compute cluster",
                  "Unlimited concurrent jobs",
                  "24/7 priority support",
                  "Custom SLAs",
                  "On-premise option",
                ],
              },
            ].map((tier, idx) => (
              <Card
                key={idx}
                className={`p-6 ${
                  tier.popular
                    ? "border-primary shadow-glow scale-105"
                    : "border-border hover:border-primary/50"
                } transition-all`}
              >
                {tier.popular && (
                  <div className="bg-gradient-primary text-primary-foreground text-xs font-bold py-1 px-3 rounded-full mb-4 inline-block">
                    MOST POPULAR
                  </div>
                )}
                <h3 className="text-2xl font-bold mb-1">{tier.name}</h3>
                <p className="text-sm text-muted-foreground mb-4">{tier.description}</p>
                <div className="mb-6">
                  <span className="text-4xl font-bold text-primary">{tier.price}</span>
                  <span className="text-foreground/70">{tier.period}</span>
                </div>
                <ul className="space-y-3 mb-6">
                  {tier.features.map((feature, i) => (
                    <li key={i} className="flex items-start text-sm text-foreground/80">
                      <CheckCircle2 className="h-4 w-4 text-primary mr-2 mt-0.5 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
                <Link to={tier.name === "Enterprise" ? "/billing/enterprise" : "/auth/signup"}>
                  <Button
                    className={`w-full ${
                      tier.popular
                        ? "bg-gradient-primary shadow-glow"
                        : "bg-secondary hover:bg-secondary/80"
                    }`}
                  >
                    {tier.name === "Enterprise" ? "Contact Sales" : "Get Started"}
                  </Button>
                </Link>
              </Card>
            ))}
          </div>

          <div className="text-center mt-8">
            <Link to="/billing/pricing">
              <Button variant="link" className="text-primary">
                View detailed pricing & compare plans →
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-glow" />
        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold text-foreground mb-6">
            Ready to Accelerate Your Computing?
          </h2>
          <p className="text-xl text-foreground/70 mb-8">
            Start free today. No credit card required.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/auth/signup">
              <Button
                size="lg"
                className="bg-gradient-primary shadow-glow hover:scale-105 transition-transform"
              >
                Start Free Today
                <Shield className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Link to="/docs">
              <Button size="lg" variant="outline">
                Explore Documentation
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <Footer />
    </div>
  );
};

export default Index;
