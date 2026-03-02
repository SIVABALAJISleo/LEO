import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { Alert } from '@/lib/types';
import { useAuth } from './AuthContext';
import { firebaseClient as supabase } from '@/integrations/firebase/client';

interface NotificationContextType {
  notifications: Alert[];
  unreadCount: number;
  markAsRead: (id: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  addNotification: (notification: Partial<Alert>) => void;
  clearAll: () => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [notifications, setNotifications] = useState<Alert[]>([]);
  const { user } = useAuth();

  const unreadCount = notifications.filter(n => !n.resolved).length;

  const fetchNotifications = useCallback(async () => {
    if (!user) return;
    try {
      const { data, error } = await supabase
        .from('alerts')
        .select('*')
        .eq('user_id', user.id)
        .order('created_at', { ascending: false })
        .limit(20);

      if (error) throw error;
      setNotifications(data || []);
    } catch (err) {
      console.error('Error fetching notifications:', err);
    }
  }, [user]);

  useEffect(() => {
    fetchNotifications();
  }, [fetchNotifications]);

  const markAsRead = async (id: string) => {
    try {
      const { error } = await supabase
        .from('alerts')
        .update({ resolved: true, resolved_at: new Date().toISOString() })
        .eq('id', id);

      if (error) throw error;
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, resolved: true } : n));
    } catch (err) {
      console.error('Error marking as read:', err);
    }
  };

  const markAllAsRead = async () => {
    if (!user) return;
    try {
      const { error } = await supabase
        .from('alerts')
        .update({ resolved: true, resolved_at: new Date().toISOString() })
        .eq('user_id', user.id)
        .eq('resolved', false);

      if (error) throw error;
      setNotifications(prev => prev.map(n => ({ ...n, resolved: true })));
    } catch (err) {
      console.error('Error marking all as read:', err);
    }
  };

  const addNotification = (notification: Partial<Alert>) => {
    const newNotify = {
      id: Math.random().toString(36).substr(2, 9),
      user_id: user?.id || 'anon',
      alert_type: 'system',
      severity: 'info',
      title: 'New Notification',
      message: '',
      resolved: false,
      created_at: new Date().toISOString(),
      ...notification
    } as Alert;

    setNotifications(prev => [newNotify, ...prev].slice(0, 50));
  };

  const clearAll = () => {
    setNotifications([]);
  };

  return (
    <NotificationContext.Provider value={{
      notifications,
      unreadCount,
      markAsRead,
      markAllAsRead,
      addNotification,
      clearAll
    }}>
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};
