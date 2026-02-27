// Authority Required Badge - Shows when authority approval is needed
// Displays: label, reason, what software prepared, next steps

import { Shield, AlertTriangle, Lock, HelpCircle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { 
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { 
  authorityBoundaryEngine, 
  type AuthorityBoundaryCheck,
  type AuthorityBoundaryType 
} from '@/lib/safeCompute/AuthorityBoundaryEngine';

interface AuthorityBadgeProps {
  check: AuthorityBoundaryCheck;
  showDetails?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const BOUNDARY_CONFIG: Record<AuthorityBoundaryType, {
  icon: typeof Shield;
  label: string;
  color: string;
}> = {
  'SAFETY_CRITICAL': {
    icon: AlertTriangle,
    label: 'Safety Critical',
    color: 'bg-red-100 text-red-800 border-red-300',
  },
  'LEGAL_FINALITY': {
    icon: Lock,
    label: 'Legal Authority',
    color: 'bg-amber-100 text-amber-800 border-amber-300',
  },
  'REALTIME_AUTHORITY': {
    icon: Shield,
    label: 'Realtime Authority',
    color: 'bg-orange-100 text-orange-800 border-orange-300',
  },
  'NEVER_SEEN_PHYSICS': {
    icon: HelpCircle,
    label: 'Novel Physics',
    color: 'bg-purple-100 text-purple-800 border-purple-300',
  },
  'PHYSICS_OK': {
    icon: Shield,
    label: 'Software OK',
    color: 'bg-green-100 text-green-800 border-green-300',
  },
};

export const AuthorityBadge = ({ check, showDetails = false, size = 'md' }: AuthorityBadgeProps) => {
  const config = BOUNDARY_CONFIG[check.classification.boundaryType];
  const Icon = config.icon;
  const uiDisplay = authorityBoundaryEngine.getUIDisplay(check);

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-2.5 py-1',
    lg: 'text-base px-3 py-1.5',
  };

  if (!check.authorityRequired) {
    return (
      <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
        <Icon className="w-3 h-3 mr-1" />
        Software Executed
      </Badge>
    );
  }

  return (
    <Tooltip>
      <TooltipTrigger>
        <Badge 
          variant="outline" 
          className={`${config.color} ${sizeClasses[size]} cursor-help`}
        >
          <Icon className="w-3 h-3 mr-1" />
          Authority Required
        </Badge>
      </TooltipTrigger>
      <TooltipContent className="max-w-sm">
        <div className="space-y-2">
          <p className="font-medium">{config.label}</p>
          <p className="text-sm text-muted-foreground">
            {check.classification.reason}
          </p>
          
          {showDetails && (
            <>
              <div>
                <p className="text-xs font-medium text-muted-foreground">Software Prepared:</p>
                <ul className="text-xs list-disc list-inside">
                  {check.softwarePrepared.slice(0, 3).map((action, i) => (
                    <li key={i}>{action}</li>
                  ))}
                </ul>
              </div>
              
              {check.handoffTarget && (
                <p className="text-xs">
                  <span className="font-medium">Handoff to:</span> {check.handoffTarget}
                </p>
              )}
            </>
          )}
        </div>
      </TooltipContent>
    </Tooltip>
  );
};

// Inline authority notice for forms/actions
interface AuthorityNoticeProps {
  boundaryType: AuthorityBoundaryType;
  compact?: boolean;
}

export const AuthorityNotice = ({ boundaryType, compact = false }: AuthorityNoticeProps) => {
  if (boundaryType === 'PHYSICS_OK') {
    return null;
  }

  const config = BOUNDARY_CONFIG[boundaryType];
  const Icon = config.icon;

  if (compact) {
    return (
      <div className={`flex items-center gap-1 text-xs ${config.color} rounded px-2 py-1`}>
        <Icon className="w-3 h-3" />
        <span>Authority Required</span>
      </div>
    );
  }

  return (
    <div className={`border rounded-lg p-3 ${config.color}`}>
      <div className="flex items-start gap-2">
        <Icon className="w-5 h-5 mt-0.5 flex-shrink-0" />
        <div>
          <p className="font-medium">{config.label} - Authority Required</p>
          <p className="text-sm mt-1">
            Software has prepared all available data but cannot be the final authority.
            Human or certified system approval is required.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuthorityBadge;
