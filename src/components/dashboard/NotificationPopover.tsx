import React from 'react';
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from '@/components/ui/popover';
import { Button } from '@/components/ui/button';
import { Bell, Check, Trash2, AlertCircle, AlertTriangle, Info, XCircle } from 'lucide-react';
import { useNotifications } from '@/contexts/NotificationContext';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '@/lib/utils';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';

export const NotificationPopover = () => {
    const { notifications, unreadCount, markAsRead, markAllAsRead, clearAll } = useNotifications();

    const getSeverityConfig = (severity: string) => {
        switch (severity) {
            case 'critical':
                return { icon: XCircle, className: 'text-destructive', bg: 'bg-destructive/10' };
            case 'error':
                return { icon: AlertCircle, className: 'text-red-500', bg: 'bg-red-500/10' };
            case 'warning':
                return { icon: AlertTriangle, className: 'text-yellow-500', bg: 'bg-yellow-500/10' };
            default:
                return { icon: Info, className: 'text-blue-500', bg: 'bg-blue-500/10' };
        }
    };

    return (
        <Popover>
            <PopoverTrigger asChild>
                <Button variant="ghost" size="icon" className="relative group">
                    <Bell className="h-5 w-5 transition-transform group-hover:rotate-12" />
                    {unreadCount > 0 && (
                        <span className="absolute -top-1 -right-1 h-4 w-4 bg-destructive rounded-full text-[10px] font-bold flex items-center justify-center text-destructive-foreground animate-in zoom-in duration-300">
                            {unreadCount > 9 ? '9+' : unreadCount}
                        </span>
                    )}
                </Button>
            </PopoverTrigger>
            <PopoverContent className="w-80 p-0 mr-4" align="end">
                <div className="flex items-center justify-between p-4 border-b">
                    <h3 className="font-semibold text-sm">Notifications</h3>
                    <div className="flex gap-2">
                        {unreadCount > 0 && (
                            <Button
                                variant="ghost"
                                size="sm"
                                className="h-8 text-xs px-2"
                                onClick={() => markAllAsRead()}
                            >
                                <Check className="h-3 w-3 mr-1" />
                                Read All
                            </Button>
                        )}
                        <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 text-xs px-2 text-destructive hover:text-destructive hover:bg-destructive/10"
                            onClick={() => clearAll()}
                        >
                            <Trash2 className="h-3 w-3" />
                        </Button>
                    </div>
                </div>

                <ScrollArea className="h-[400px]">
                    {notifications.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-40 text-muted-foreground">
                            <Bell className="h-8 w-8 mb-2 opacity-20" />
                            <p className="text-sm">No new notifications</p>
                        </div>
                    ) : (
                        <div className="divide-y divide-border">
                            {notifications.map((notification) => {
                                const config = getSeverityConfig(notification.severity);
                                const Icon = config.icon;

                                return (
                                    <div
                                        key={notification.id}
                                        className={cn(
                                            "p-4 transition-colors relative group",
                                            !notification.resolved ? "bg-accent/30" : "opacity-70"
                                        )}
                                    >
                                        {!notification.resolved && (
                                            <span className="absolute left-1 top-1/2 -translate-y-1/2 w-1 h-8 bg-primary rounded-full" />
                                        )}
                                        <div className="flex gap-3">
                                            <div className={cn("mt-1 p-1 rounded-full", config.bg)}>
                                                <Icon className={cn("h-4 w-4", config.className)} />
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-center justify-between mb-0.5">
                                                    <p className="text-sm font-medium leading-none truncate pr-4">
                                                        {notification.title}
                                                    </p>
                                                    <span className="text-[10px] text-muted-foreground whitespace-nowrap">
                                                        {formatDistanceToNow(new Date(notification.created_at), { addSuffix: true })}
                                                    </span>
                                                </div>
                                                <p className="text-xs text-muted-foreground leading-relaxed">
                                                    {notification.message}
                                                </p>
                                                {!notification.resolved && (
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        className="h-6 mt-2 text-[10px] px-2"
                                                        onClick={() => markAsRead(notification.id)}
                                                    >
                                                        Mark as read
                                                    </Button>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </ScrollArea>
                <div className="p-2 border-t">
                    <Button variant="ghost" className="w-full text-xs h-8 justify-center opacity-70">
                        View All History
                    </Button>
                </div>
            </PopoverContent>
        </Popover>
    );
};
