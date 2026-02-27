import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { SidebarTrigger } from '@/components/ui/sidebar';
import { Plus, List, Settings, Bell } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { ComputeSafetyBadge } from './ComputeSafetyBadge';
import { NotificationPopover } from './NotificationPopover';

export const DashboardHeader = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const currentDate = format(new Date(), 'EEEE, MMMM d, yyyy');

  // Display username from profile, fallback to email username part
  const displayName = user?.username || user?.email?.split('@')[0] || 'User';

  return (
    <header className="h-16 border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-10">
      <div className="h-full px-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <SidebarTrigger className="lg:hidden" />
          <div>
            <h1 className="text-lg font-semibold">Welcome back, {displayName}</h1>
            <p className="text-sm text-muted-foreground">{currentDate}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Safe-Compute Badge */}
          <ComputeSafetyBadge />

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate('/dashboard/jobs')}
              className="hidden sm:flex"
            >
              <List className="h-4 w-4 mr-2" />
              View Jobs
            </Button>
            <Button
              size="sm"
              className="bg-gradient-primary shadow-glow"
              onClick={() => navigate('/dashboard/jobs?new=true')}
            >
              <Plus className="h-4 w-4 mr-2" />
              New Job
            </Button>

            <NotificationPopover />

            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate('/dashboard/settings')}
            >
              <Settings className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
};