import React, { Component, ErrorInfo, ReactNode } from 'react';
import { nvidiaTokens } from '../design_system/nvidiaTokens';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('LEO Quantum Error Boundary caught an exception:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div
          style={{
            minHeight: '100vh',
            background: nvidiaTokens.colors.primary.black,
            color: nvidiaTokens.colors.primary.white,
            fontFamily: nvidiaTokens.typography.fontFamily.primary,
          }}
          className="flex flex-col items-center justify-center p-6 text-center space-y-6"
        >
          <div className="p-4 rounded-full bg-red-500/10 border border-red-500/30 text-red-400">
            <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>

          <div className="space-y-2 max-w-md">
            <h1
              className="text-2xl font-bold tracking-tight"
              style={{ color: nvidiaTokens.colors.accent.nvidiaGreen }}
            >
              Quantum Runtime Excursion Captured
            </h1>
            <p className="text-xs text-slate-400 font-mono">
              {this.state.error?.message || 'An unexpected rendering error occurred inside the LEO execution kernel.'}
            </p>
          </div>

          <button
            onClick={() => window.location.reload()}
            style={{
              background: nvidiaTokens.colors.accent.nvidiaGreen,
              color: nvidiaTokens.colors.primary.black,
              fontFamily: nvidiaTokens.typography.fontFamily.primary,
              fontWeight: nvidiaTokens.typography.fontWeight.bold,
            }}
            className="px-6 py-2.5 rounded uppercase tracking-wider text-xs cursor-pointer hover:bg-emerald-400 transition-colors duration-200"
          >
            Reload Quantum Session
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
