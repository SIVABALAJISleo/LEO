import { Link, useLocation } from "react-router-dom";
import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Home, ArrowLeft, Search, Zap, BookOpen, HelpCircle } from "lucide-react";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error("404 Error: User attempted to access non-existent route:", location.pathname);
  }, [location.pathname]);

  const suggestions = [
    {
      title: "Dashboard",
      description: "View your GPU optimization dashboard",
      href: "/dashboard/home",
      icon: Zap,
    },
    {
      title: "Documentation",
      description: "Learn about HYPER's features",
      href: "/docs",
      icon: BookOpen,
    },
    {
      title: "Contact Support",
      description: "Get help from our team",
      href: "/legal/contact",
      icon: HelpCircle,
    },
  ];

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />
      
      <main className="flex-1 flex items-center justify-center py-20">
        <div className="max-w-2xl mx-auto px-4 text-center">
          {/* 404 Graphic */}
          <div className="relative mb-8">
            <div className="text-[10rem] font-bold text-primary/10 select-none leading-none">
              404
            </div>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="bg-primary/10 rounded-full p-6">
                <Search className="h-16 w-16 text-primary animate-pulse" />
              </div>
            </div>
          </div>

          {/* Message */}
          <h1 className="text-3xl font-bold mb-4">Page Not Found</h1>
          <p className="text-lg text-muted-foreground mb-8 max-w-md mx-auto">
            The page you're looking for doesn't exist or has been moved. 
            Let's get you back on track.
          </p>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
            <Link to="/">
              <Button size="lg" className="bg-gradient-primary shadow-glow">
                <Home className="mr-2 h-5 w-5" />
                Go Home
              </Button>
            </Link>
            <Button 
              size="lg" 
              variant="outline" 
              onClick={() => window.history.back()}
            >
              <ArrowLeft className="mr-2 h-5 w-5" />
              Go Back
            </Button>
          </div>

          {/* Quick Links */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {suggestions.map((suggestion) => (
              <Link key={suggestion.href} to={suggestion.href}>
                <Card className="h-full bg-card border-border hover:border-primary/50 transition-all hover:shadow-glow cursor-pointer">
                  <CardHeader className="pb-2">
                    <suggestion.icon className="h-8 w-8 text-primary mb-2" />
                    <CardTitle className="text-lg">{suggestion.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription>{suggestion.description}</CardDescription>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>

          {/* Attempted Path */}
          <div className="mt-12 p-4 bg-muted/50 rounded-lg">
            <p className="text-sm text-muted-foreground">
              Attempted path: <code className="text-primary">{location.pathname}</code>
            </p>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default NotFound;
