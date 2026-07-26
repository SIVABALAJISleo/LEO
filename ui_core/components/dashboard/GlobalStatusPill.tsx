import { cn } from "@/lib/utils";
import { SystemStatus } from "@/lib/types";

interface GlobalStatusPillProps {
  status: SystemStatus | string;
  agentOnline?: boolean;
}

export const GlobalStatusPill = ({ status, agentOnline }: GlobalStatusPillProps) => {
  const getStatusConfig = () => {
    // If agent is explicitly offline, show that
    if (agentOnline === false) {
      return {
        label: "Agent Offline",
        className: "bg-muted text-muted-foreground border-border",
        dot: "bg-muted-foreground",
      };
    }

    switch (status) {
      case "healthy":
        return {
          label: "System Healthy",
          className: "bg-primary/20 text-primary border-primary/30",
          dot: "bg-primary",
        };
      case "warning":
        return {
          label: "System Warning",
          className: "bg-yellow-500/20 text-yellow-500 border-yellow-500/30",
          dot: "bg-yellow-500",
        };
      case "critical":
        return {
          label: "System Critical",
          className: "bg-destructive/20 text-destructive border-destructive/30",
          dot: "bg-destructive",
        };
      default:
        return {
          label: "Awaiting Data",
          className: "bg-muted text-muted-foreground border-border",
          dot: "bg-muted-foreground",
        };
    }
  };

  const config = getStatusConfig();

  return (
    <div
      className={cn(
        "inline-flex items-center gap-2 px-4 py-2 rounded-full border text-sm font-medium",
        config.className,
      )}
    >
      <span className={cn("w-2 h-2 rounded-full animate-pulse", config.dot)} />
      {config.label}
    </div>
  );
};
