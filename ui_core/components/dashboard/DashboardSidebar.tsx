import { NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarHeader,
  SidebarFooter,
  useSidebar,
} from '@/components/ui/sidebar';
import { Button } from '@/components/ui/button';
import {
  Cpu,
  LayoutDashboard,
  Briefcase,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  Box,
  Settings2,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  BarChart3,
  Settings,
  LogOut,
  ChevronLeft,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  Users,
  Brain,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  TrendingUp,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  Cloud,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  Database,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  Atom,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  Layers,
  Activity,
  Shield,
  DollarSign,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  PieChart,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  Sparkles,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  Store,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  Building2,
  AlertTriangle,
  Eye,
  Microscope

} from 'lucide-react';
import { cn } from '@/lib/utils';

const mainNavItems = [
  { title: 'Dashboard', url: '/dashboard/home', icon: LayoutDashboard },
  { title: 'Vision Intelligence', url: '/dashboard/vision', icon: Eye },
  { title: 'JEPA Architectures', url: '/dashboard/jepa', icon: Microscope },
  { title: 'SOTA Models', url: '/dashboard/sota', icon: Cpu },
  { title: 'Orchestration', url: '/dashboard/orchestration', icon: Brain },
  { title: 'Telemetry', url: '/dashboard/telemetry', icon: Activity },
  { title: 'Inference', url: '/dashboard/inference', icon: Briefcase },
  { title: 'GPU Bypass', url: '/dashboard/gpu-bypass', icon: Cpu },
  { title: 'Modules', url: '/dashboard/modules', icon: Settings2 },
];

const advancedNavItems = [
  { title: 'Security', url: '/dashboard/advanced/security', icon: Shield },
  { title: 'Cost Analytics', url: '/dashboard/advanced/cost-analytics', icon: DollarSign },
  { title: 'Disaster Recovery', url: '/dashboard/advanced/disaster-recovery', icon: AlertTriangle },
];

const settingsNavItems = [
  { title: 'Settings', url: '/dashboard/settings', icon: Settings },
];

export const DashboardSidebar = () => {
  const { state, toggleSidebar } = useSidebar();
  const collapsed = state === 'collapsed';
  const location = useLocation();
  const { signOut } = useAuth();

  const isActive = (path: string) => location.pathname === path;

  const renderNavItem = (item: { title: string; url: string; icon: React.ComponentType<{ className?: string }> }) => (
    <SidebarMenuItem key={item.title}>
      <SidebarMenuButton asChild isActive={isActive(item.url)}>
        <NavLink
          to={item.url}
          className={cn(
            'flex items-center gap-3 px-3 py-2 rounded-md transition-colors',
            isActive(item.url)
              ? 'bg-primary/20 text-primary'
              : 'text-sidebar-foreground hover:bg-sidebar-accent'
          )}
        >
          <item.icon className="h-5 w-5 flex-shrink-0" />
          {!collapsed && <span className="truncate">{item.title}</span>}
        </NavLink>
      </SidebarMenuButton>
    </SidebarMenuItem>
  );

  return (
    <Sidebar
      className={cn(
        'border-r border-sidebar-border bg-sidebar-background transition-all duration-300',
        collapsed ? 'w-16' : 'w-64'
      )}
      collapsible="icon"
    >
      <SidebarHeader className="p-4 border-b border-sidebar-border">
        <div className="flex items-center justify-between">
          <NavLink to="/" className="flex items-center space-x-2 group">
            <Cpu className="h-8 w-8 text-primary" />
            {!collapsed && (
              <span className="text-xl font-display font-bold">
                HYPER
              </span>
            )}
          </NavLink>
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleSidebar}
            className="h-8 w-8"
          >
            <ChevronLeft className={cn(
              'h-4 w-4 transition-transform',
              collapsed && 'rotate-180'
            )} />
          </Button>
        </div>
      </SidebarHeader>

      <SidebarContent className="px-2 py-4 overflow-y-auto">
        <SidebarGroup>
          <SidebarGroupLabel className={cn(collapsed && 'sr-only')}>
            Main
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {mainNavItems.map(renderNavItem)}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup className="mt-4">
          <SidebarGroupLabel className={cn(collapsed && 'sr-only')}>
            Advanced
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {advancedNavItems.map(renderNavItem)}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup className="mt-4">
          <SidebarGroupLabel className={cn(collapsed && 'sr-only')}>
            Settings
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {settingsNavItems.map(renderNavItem)}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="p-2 border-t border-sidebar-border">
        <Button
          variant="ghost"
          className={cn(
            'w-full justify-start text-sidebar-foreground hover:text-destructive',
            collapsed && 'justify-center'
          )}
          onClick={signOut}
        >
          <LogOut className="h-5 w-5" />
          {!collapsed && <span className="ml-3">Sign Out</span>}
        </Button>
      </SidebarFooter>
    </Sidebar>
  );
};
