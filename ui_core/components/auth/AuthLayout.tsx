import { Link } from 'react-router-dom';
import { Cpu } from 'lucide-react';
import { Card } from '@/components/ui/card';

interface AuthLayoutProps {
  children: React.ReactNode;
  title: string;
  description: string;
}

export const AuthLayout = ({ children, title, description }: AuthLayoutProps) => {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-gradient-glow" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,hsl(88_72%_50%/0.1),transparent_50%)]" />

      <Card className="relative w-full max-w-md p-8 bg-card border-border shadow-card animate-fade-in">
        <Link to="/" className="flex items-center justify-center space-x-2 mb-8 group">
          <Cpu className="h-8 w-8 text-primary group-hover:animate-float" />
          <span className="text-2xl font-display font-bold">
            HYPER
          </span>
        </Link>

        <h2 className="text-3xl font-display font-bold text-center mb-2">
          {title}
        </h2>
        <p className="text-foreground/60 text-center mb-8">
          {description}
        </p>

        {children}

        <div className="mt-8 pt-8 border-t border-border text-center text-sm text-foreground/60">
          <Link to="/" className="hover:text-primary transition-colors">
            ← Back to home
          </Link>
        </div>
      </Card>
    </div>
  );
};
