/**
 * Quick Stats - Summary statistics cards for dashboard
 * Shows key metrics at a glance with trend indicators
 */

import { Card, CardContent } from '@/components/ui/card';
import { 
  Zap, 
  Clock, 
  CheckCircle2, 
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Minus
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface StatCard {
  label: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon: typeof Zap;
  iconColor: string;
}

interface QuickStatsProps {
  totalJobs: number;
  completedJobs: number;
  activeJobs: number;
  failedJobs: number;
  avgLatency?: number;
  successRate?: number;
  className?: string;
}

export const QuickStats = ({ 
  totalJobs, 
  completedJobs, 
  activeJobs, 
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  failedJobs,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  avgLatency = 0,
  successRate,
  className 
}: QuickStatsProps) => {
  const calculatedSuccessRate = successRate ?? (totalJobs > 0 
    ? Math.round((completedJobs / totalJobs) * 100) 
    : 0);

  const stats: StatCard[] = [
    {
      label: 'Total Jobs',
      value: totalJobs,
      icon: Zap,
      iconColor: 'text-primary',
    },
    {
      label: 'Active',
      value: activeJobs,
      icon: Clock,
      iconColor: 'text-blue-500',
    },
    {
      label: 'Completed',
      value: completedJobs,
      icon: CheckCircle2,
      iconColor: 'text-green-500',
    },
    {
      label: 'Success Rate',
      value: `${calculatedSuccessRate}%`,
      change: calculatedSuccessRate >= 90 ? 1 : calculatedSuccessRate >= 70 ? 0 : -1,
      icon: calculatedSuccessRate >= 90 ? TrendingUp : calculatedSuccessRate >= 70 ? Minus : TrendingDown,
      iconColor: calculatedSuccessRate >= 90 
        ? 'text-green-500' 
        : calculatedSuccessRate >= 70 
        ? 'text-yellow-500' 
        : 'text-red-500',
    },
  ];

  return (
    <div className={cn('grid grid-cols-2 lg:grid-cols-4 gap-4', className)}>
      {stats.map((stat) => (
        <Card key={stat.label} className="bg-card border-border">
          <CardContent className="pt-4 pb-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">{stat.label}</p>
                <p className="text-2xl font-bold mt-1">{stat.value}</p>
              </div>
              <div className={cn('p-2 rounded-lg bg-muted/50', stat.iconColor)}>
                <stat.icon className="h-5 w-5" />
              </div>
            </div>
            {stat.change !== undefined && (
              <div className={cn(
                'text-xs mt-2 flex items-center gap-1',
                stat.change > 0 ? 'text-green-500' : stat.change < 0 ? 'text-red-500' : 'text-yellow-500'
              )}>
                {stat.change > 0 ? (
                  <><TrendingUp className="h-3 w-3" /> Excellent</>
                ) : stat.change < 0 ? (
                  <><TrendingDown className="h-3 w-3" /> Needs attention</>
                ) : (
                  <><Minus className="h-3 w-3" /> Normal</>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default QuickStats;
