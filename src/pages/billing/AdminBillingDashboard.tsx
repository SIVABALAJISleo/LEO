import { useState, useEffect } from 'react';
import { firebaseClient as supabase } from '@/integrations/firebase/client';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  DollarSign, 
  TrendingUp, 
  Users, 
  AlertTriangle, 
  RefreshCw,
  CheckCircle,
  XCircle,
  Clock,
  CreditCard,
  ShieldAlert,
  Loader2
} from 'lucide-react';
import { formatDistanceToNow, format } from 'date-fns';
import { useAdminRole } from '@/hooks/useAdminRole';

interface Payment {
  id: string;
  user_id: string;
  provider: string;
  amount: number;
  currency: string;
  plan: string;
  status: string;
  transaction_id: string | null;
  created_at: string;
}

interface WebhookEvent {
  id: string;
  provider: string;
  event_type: string;
  event_id: string;
  processed: boolean;
  error_message: string | null;
  created_at: string;
}

interface Subscription {
  id: string;
  user_id: string;
  plan: string;
  status: string;
  created_at: string;
}

export default function AdminBillingDashboard() {
  const { isAdmin, isLoading: roleLoading } = useAdminRole();
  const [payments, setPayments] = useState<Payment[]>([]);
  const [webhooks, setWebhooks] = useState<WebhookEvent[]>([]);
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async () => {
    try {
      const [paymentsRes, webhooksRes, subscriptionsRes] = await Promise.all([
        supabase.from('payments').select('*').order('created_at', { ascending: false }).limit(100),
        supabase.from('payment_webhook_events').select('*').order('created_at', { ascending: false }).limit(50),
        supabase.from('billing_subscriptions').select('*').order('created_at', { ascending: false }).limit(100),
      ]);

      if (paymentsRes.data) setPayments(paymentsRes.data as Payment[]);
      if (webhooksRes.data) setWebhooks(webhooksRes.data as WebhookEvent[]);
      if (subscriptionsRes.data) setSubscriptions(subscriptionsRes.data as Subscription[]);
    } catch (err) {
      console.error('Admin billing fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAdmin && !roleLoading) {
      fetchData();
      const interval = setInterval(fetchData, 30000);
      return () => clearInterval(interval);
    }
  }, [isAdmin, roleLoading]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchData();
    setRefreshing(false);
  };

  if (roleLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!isAdmin) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <ShieldAlert className="w-16 h-16 mx-auto text-destructive mb-4" />
            <CardTitle>Access Denied</CardTitle>
            <CardDescription>Admin privileges required.</CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <Button onClick={() => window.location.href = '/dashboard'}>
              Return to Dashboard
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Calculate stats
  const totalRevenue = payments
    .filter(p => p.status === 'succeeded')
    .reduce((sum, p) => sum + Number(p.amount), 0);
  const monthlyRevenue = payments
    .filter(p => p.status === 'succeeded' && new Date(p.created_at).getMonth() === new Date().getMonth())
    .reduce((sum, p) => sum + Number(p.amount), 0);
  const failedPayments = payments.filter(p => p.status === 'failed');
  const pendingPayments = payments.filter(p => p.status === 'pending');
  const refundedPayments = payments.filter(p => p.status === 'refunded');
  const activeSubscriptions = subscriptions.filter(s => s.status === 'active');
  const webhookErrors = webhooks.filter(w => w.error_message);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'succeeded': return <Badge className="bg-green-500/20 text-green-500">Succeeded</Badge>;
      case 'failed': return <Badge variant="destructive">Failed</Badge>;
      case 'pending': return <Badge variant="secondary">Pending</Badge>;
      case 'refunded': return <Badge className="bg-orange-500/20 text-orange-500">Refunded</Badge>;
      default: return <Badge variant="outline">{status}</Badge>;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-primary">Billing Dashboard</h1>
            <p className="text-muted-foreground">Admin-only • Read-only view</p>
          </div>
          <Button variant="outline" size="sm" onClick={handleRefresh} disabled={refreshing}>
            <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid gap-4 md:grid-cols-5">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <DollarSign className="h-4 w-4" /> Total Revenue
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">{formatCurrency(totalRevenue)}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <TrendingUp className="h-4 w-4" /> This Month
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(monthlyRevenue)}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Users className="h-4 w-4" /> Active Subs
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-500">{activeSubscriptions.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <XCircle className="h-4 w-4" /> Failed
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-destructive">{failedPayments.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <AlertTriangle className="h-4 w-4" /> Refunds
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-500">{refundedPayments.length}</div>
            </CardContent>
          </Card>
        </div>

        {/* Tables */}
        <Tabs defaultValue="payments">
          <TabsList>
            <TabsTrigger value="payments">Payments ({payments.length})</TabsTrigger>
            <TabsTrigger value="subscriptions">Subscriptions ({subscriptions.length})</TabsTrigger>
            <TabsTrigger value="webhooks">Webhooks ({webhooks.length})</TabsTrigger>
          </TabsList>

          <TabsContent value="payments">
            <Card>
              <CardContent className="p-0">
                <ScrollArea className="h-[400px]">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>ID</TableHead>
                        <TableHead>Provider</TableHead>
                        <TableHead>Plan</TableHead>
                        <TableHead>Amount</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Date</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {payments.map(payment => (
                        <TableRow key={payment.id}>
                          <TableCell className="font-mono text-xs">{payment.id.slice(0, 8)}...</TableCell>
                          <TableCell>
                            <Badge variant="outline">{payment.provider}</Badge>
                          </TableCell>
                          <TableCell className="capitalize">{payment.plan}</TableCell>
                          <TableCell>{formatCurrency(payment.amount)}</TableCell>
                          <TableCell>{getStatusBadge(payment.status)}</TableCell>
                          <TableCell className="text-xs text-muted-foreground">
                            {formatDistanceToNow(new Date(payment.created_at), { addSuffix: true })}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="subscriptions">
            <Card>
              <CardContent className="p-0">
                <ScrollArea className="h-[400px]">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>User ID</TableHead>
                        <TableHead>Plan</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Created</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {subscriptions.map(sub => (
                        <TableRow key={sub.id}>
                          <TableCell className="font-mono text-xs">{sub.user_id.slice(0, 8)}...</TableCell>
                          <TableCell className="capitalize">{sub.plan}</TableCell>
                          <TableCell>
                            <Badge variant={sub.status === 'active' ? 'default' : 'secondary'}>
                              {sub.status}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-xs text-muted-foreground">
                            {format(new Date(sub.created_at), 'PPP')}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="webhooks">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Webhook Health</CardTitle>
                <CardDescription>
                  {webhookErrors.length === 0 
                    ? <span className="text-green-500">All webhooks processed successfully</span>
                    : <span className="text-destructive">{webhookErrors.length} errors detected</span>
                  }
                </CardDescription>
              </CardHeader>
              <CardContent className="p-0">
                <ScrollArea className="h-[300px]">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Provider</TableHead>
                        <TableHead>Event</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Time</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {webhooks.map(webhook => (
                        <TableRow key={webhook.id}>
                          <TableCell>
                            <Badge variant="outline">{webhook.provider}</Badge>
                          </TableCell>
                          <TableCell className="font-mono text-xs">{webhook.event_type}</TableCell>
                          <TableCell>
                            {webhook.error_message 
                              ? <Badge variant="destructive">Error</Badge>
                              : <Badge className="bg-green-500/20 text-green-500">OK</Badge>
                            }
                          </TableCell>
                          <TableCell className="text-xs text-muted-foreground">
                            {formatDistanceToNow(new Date(webhook.created_at), { addSuffix: true })}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
