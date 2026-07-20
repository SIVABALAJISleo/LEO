import { AlertTriangle, WifiOff } from "lucide-react";
import type { ReactNode } from "react";

/** Simple animated skeleton block. */
export function Skeleton({ className = "" }: { className?: string }) {
  return (
    <div
      className={`animate-pulse bg-surface ${className}`}
      aria-hidden="true"
      role="presentation"
    />
  );
}

/** Grid of metric-tile skeletons that mirrors the dashboard layout. */
export function TileSkeletonGrid({ count = 6 }: { count?: number }) {
  return (
    <div
      className="grid gap-px bg-border sm:grid-cols-2 lg:grid-cols-3"
      aria-busy="true"
      aria-label="Loading metrics"
    >
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="bg-background p-6">
          <Skeleton className="h-3 w-24" />
          <Skeleton className="mt-4 h-10 w-32" />
        </div>
      ))}
    </div>
  );
}

/** Row skeletons for list-style views (memory, KG results). */
export function ListSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div aria-busy="true" aria-label="Loading">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="border-b border-border last:border-0 p-4">
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="mt-2 h-3 w-1/2" />
        </div>
      ))}
    </div>
  );
}

/** Consistent error banner used across authenticated pages. */
export function ErrorState({
  title = "Backend unavailable",
  message,
  onRetry,
  icon: Icon = WifiOff,
}: {
  title?: string;
  message?: string;
  onRetry?: () => void;
  icon?: typeof AlertTriangle;
}) {
  return (
    <div role="alert" className="border border-border bg-surface p-6 flex items-start gap-4">
      <Icon className="h-5 w-5 text-leo shrink-0 mt-0.5" aria-hidden="true" />
      <div className="flex-1 min-w-0">
        <div className="font-display font-bold">{title}</div>
        <p className="mt-1 text-sm text-muted-foreground">
          {message ??
            "Check that your LEO backend is running and the API base URL in Settings is correct."}
        </p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="mt-4 border border-border px-4 py-2 text-xs font-semibold hover:border-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
          >
            Retry
          </button>
        )}
      </div>
    </div>
  );
}

/** Empty state for lists with no results. */
export function EmptyState({
  title,
  body,
  action,
}: {
  title: string;
  body?: string;
  action?: ReactNode;
}) {
  return (
    <div className="border border-dashed border-border p-10 text-center">
      <div className="font-display text-lg font-bold">{title}</div>
      {body && <p className="mt-2 text-sm text-muted-foreground">{body}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
