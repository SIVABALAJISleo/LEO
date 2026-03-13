import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AlertTriangle, RefreshCw, Home, ArrowRight } from 'lucide-react';
import { logError } from '@/lib/logging';
import { toExplainableError, type ExplainableError } from '@/lib/production';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  explainableError: ExplainableError | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
    explainableError: null,
  };

  public static getDerivedStateFromError(error: Error): Partial<State> {
    const explainableError = toExplainableError(error);
    return { hasError: true, error, explainableError };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ errorInfo });
    
    // Log the error to our logging service
    logError({
      message: error.message,
      stack: error.stack,
      componentName: errorInfo.componentStack?.split('\n')[1]?.trim() || 'Unknown',
      metadata: {
        componentStack: errorInfo.componentStack,
        url: window.location.href,
        userAgent: navigator.userAgent,
      },
    });
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null, explainableError: null });
  };

  private handleGoHome = () => {
    window.location.href = '/';
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      const { explainableError, error } = this.state;

      return (
        <div className="min-h-screen bg-background flex items-center justify-center p-4">
          <Card className="max-w-lg w-full p-8 text-center">
            <div className="flex justify-center mb-6">
              <div className="p-4 rounded-full bg-destructive/10">
                <AlertTriangle className="h-12 w-12 text-destructive" />
              </div>
            </div>
            
            <h1 className="text-2xl font-bold mb-2">
              {explainableError?.title || 'Something went wrong'}
            </h1>
            <p className="text-muted-foreground mb-4">
              {explainableError?.explanation || 'An unexpected error occurred. Our team has been notified.'}
            </p>

            {explainableError?.nextAction && (
              <div className="mb-6 p-4 bg-muted rounded-lg text-left">
                <p className="text-sm font-medium text-foreground flex items-center gap-2">
                  <ArrowRight className="h-4 w-4 text-primary" />
                  Next Step
                </p>
                <p className="text-sm text-muted-foreground mt-1">
                  {explainableError.nextAction}
                </p>
              </div>
            )}

            {process.env.NODE_ENV === 'development' && error && (
              <div className="mb-6 p-4 bg-muted rounded-lg text-left">
                <p className="font-mono text-xs text-muted-foreground mb-1">
                  Error Code: {explainableError?.code || 'UNKNOWN'}
                </p>
                <p className="font-mono text-sm text-destructive mb-2">
                  {error.message}
                </p>
                <pre className="text-xs text-muted-foreground overflow-auto max-h-32">
                  {error.stack}
                </pre>
              </div>
            )}

            <div className="flex gap-4 justify-center">
              <Button
                variant="outline"
                onClick={this.handleGoHome}
                className="gap-2"
              >
                <Home className="h-4 w-4" />
                Go Home
              </Button>
              <Button
                onClick={this.handleReset}
                className="gap-2"
              >
                <RefreshCw className="h-4 w-4" />
                Try Again
              </Button>
            </div>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
