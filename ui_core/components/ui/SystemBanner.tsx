import { useEffect, useState } from "react";
import { AlertTriangle, XCircle, Info, X } from "lucide-react";
import { incidentStateMachine } from "@/lib/production/IncidentStateMachine";

interface SystemBannerProps {
  dismissible?: boolean;
}

export const SystemBanner = ({ dismissible = true }: SystemBannerProps) => {
  const [banner, setBanner] = useState(incidentStateMachine.getStatusBanner());
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      const newBanner = incidentStateMachine.getStatusBanner();
      setBanner(newBanner);
      // Reset dismissed state if severity changes
      if (newBanner.severity !== banner.severity) {
        setDismissed(false);
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [banner.severity]);

  if (!banner.visible || dismissed) {
    return null;
  }

  const getIcon = () => {
    switch (banner.severity) {
      case "error":
        return <XCircle className="h-4 w-4" />;
      case "warning":
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <Info className="h-4 w-4" />;
    }
  };

  const getBgClass = () => {
    switch (banner.severity) {
      case "error":
        return "bg-destructive text-destructive-foreground";
      case "warning":
        return "bg-yellow-500 text-yellow-950";
      default:
        return "bg-primary text-primary-foreground";
    }
  };

  return (
    <div className={`w-full px-4 py-2 ${getBgClass()}`}>
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-2">
          {getIcon()}
          <span className="text-sm font-medium">{banner.message}</span>
        </div>
        {dismissible && (
          <button
            onClick={() => setDismissed(true)}
            className="p-1 hover:opacity-70 transition-opacity"
            aria-label="Dismiss"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
};
