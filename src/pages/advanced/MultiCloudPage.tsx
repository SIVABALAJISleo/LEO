import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Cloud, Globe, Zap, DollarSign, Plus, Trash2, Settings } from 'lucide-react';
import { useMultiCloudData, CLOUD_PROVIDERS_LIST, ROUTING_MODES, REGIONS } from '@/hooks/useMultiCloudData';
import { LoadingState } from '@/components/ui/loading-state';
import { EmptyState } from '@/components/ui/empty-state';

const MultiCloudPage = () => {
  const { providers, failoverLogs, routingRules, isLoading, addProvider, updateProvider, deleteProvider, createRoutingRule, toggleRoutingRule, getProviderStats, getBestProvider } = useMultiCloudData();
  const [newProvider, setNewProvider] = useState('');
  const [newRegion, setNewRegion] = useState('');
  const [newRuleName, setNewRuleName] = useState('');
  const [newRuleMode, setNewRuleMode] = useState('balanced');

  const handleAddProvider = async () => {
    if (!newProvider || !newRegion) return;
    await addProvider({ provider_name: newProvider, region: newRegion });
    setNewProvider('');
    setNewRegion('');
  };

  const handleCreateRule = async () => {
    if (!newRuleName.trim()) return;
    await createRoutingRule({ name: newRuleName, mode: newRuleMode });
    setNewRuleName('');
  };

  if (isLoading) return <LoadingState message="Loading cloud configuration..." />;

  const bestProvider = getBestProvider();

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Multi-Cloud Optimization</h1>
          <p className="text-muted-foreground">Intelligent routing across AWS, GCP, and Azure</p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Active Providers</CardTitle></CardHeader>
          <CardContent><p className="text-2xl font-bold">{providers.filter(p => p.is_active).length}</p></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Best Provider</CardTitle></CardHeader>
          <CardContent><p className="text-2xl font-bold">{bestProvider?.provider_name.toUpperCase() || 'N/A'}</p></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Failovers (24h)</CardTitle></CardHeader>
          <CardContent><p className="text-2xl font-bold">{failoverLogs.length}</p></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Active Rules</CardTitle></CardHeader>
          <CardContent><p className="text-2xl font-bold">{routingRules.filter(r => r.is_active).length}</p></CardContent>
        </Card>
      </div>

      <Tabs defaultValue="providers">
        <TabsList>
          <TabsTrigger value="providers">Cloud Providers</TabsTrigger>
          <TabsTrigger value="routing">Routing Rules</TabsTrigger>
          <TabsTrigger value="failover">Failover Log</TabsTrigger>
        </TabsList>

        <TabsContent value="providers" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Add Provider</CardTitle>
            </CardHeader>
            <CardContent className="flex gap-4">
              <Select value={newProvider} onValueChange={setNewProvider}>
                <SelectTrigger className="w-48"><SelectValue placeholder="Provider" /></SelectTrigger>
                <SelectContent>{CLOUD_PROVIDERS_LIST.map((p) => <SelectItem key={p.value} value={p.value}>{p.icon} {p.label}</SelectItem>)}</SelectContent>
              </Select>
              <Select value={newRegion} onValueChange={setNewRegion}>
                <SelectTrigger className="w-48"><SelectValue placeholder="Region" /></SelectTrigger>
                <SelectContent>{(REGIONS[newProvider as keyof typeof REGIONS] || []).map((r) => <SelectItem key={r} value={r}>{r}</SelectItem>)}</SelectContent>
              </Select>
              <Button onClick={handleAddProvider}><Plus className="mr-2 h-4 w-4" />Add</Button>
            </CardContent>
          </Card>

          {providers.length === 0 ? (
            <EmptyState title="No providers" description="Add cloud providers to enable multi-cloud routing" icon={Cloud} />
          ) : (
            <div className="grid gap-4 md:grid-cols-3">
              {providers.map((provider) => {
                const stats = getProviderStats(provider.id);
                const providerInfo = CLOUD_PROVIDERS_LIST.find(p => p.value === provider.provider_name);
                return (
                  <Card key={provider.id}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="flex items-center gap-2">{providerInfo?.icon} {provider.provider_name.toUpperCase()}</CardTitle>
                        <Switch checked={provider.is_active || false} onCheckedChange={(checked) => updateProvider(provider.id, { is_active: checked })} />
                      </div>
                      <CardDescription>{provider.region}</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div><p className="text-muted-foreground">Avg Latency</p><p className="font-medium">{stats.avgLatency ? `${stats.avgLatency.toFixed(0)}ms` : 'N/A'}</p></div>
                        <div><p className="text-muted-foreground">Success Rate</p><p className="font-medium">{stats.successRate ? `${stats.successRate.toFixed(1)}%` : 'N/A'}</p></div>
                      </div>
                      <div className="flex gap-2">
                        <Badge variant={provider.credentials_configured ? 'default' : 'outline'}>{provider.credentials_configured ? 'Configured' : 'Not Configured'}</Badge>
                      </div>
                      <Button size="sm" variant="destructive" onClick={() => deleteProvider(provider.id)}><Trash2 className="h-4 w-4" /></Button>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </TabsContent>

        <TabsContent value="routing" className="space-y-4">
          <Card>
            <CardHeader><CardTitle>Create Routing Rule</CardTitle></CardHeader>
            <CardContent className="flex gap-4">
              <Input placeholder="Rule name" value={newRuleName} onChange={(e) => setNewRuleName(e.target.value)} />
              <Select value={newRuleMode} onValueChange={setNewRuleMode}>
                <SelectTrigger className="w-48"><SelectValue /></SelectTrigger>
                <SelectContent>{ROUTING_MODES.map((m) => <SelectItem key={m.value} value={m.value}>{m.label}</SelectItem>)}</SelectContent>
              </Select>
              <Button onClick={handleCreateRule}><Plus className="mr-2 h-4 w-4" />Create</Button>
            </CardContent>
          </Card>

          {routingRules.map((rule) => (
            <Card key={rule.id}>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle>{rule.name}</CardTitle>
                  <Switch checked={rule.is_active || false} onCheckedChange={(checked) => toggleRoutingRule(rule.id, checked)} />
                </div>
              </CardHeader>
              <CardContent>
                <Badge>{ROUTING_MODES.find(m => m.value === rule.mode)?.label || rule.mode}</Badge>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="failover">
          {failoverLogs.length === 0 ? (
            <EmptyState title="No failover events" description="System is running smoothly" />
          ) : (
            <div className="space-y-2">
              {failoverLogs.map((log) => (
                <Card key={log.id}>
                  <CardContent className="flex items-center justify-between py-3">
                    <div>
                      <p className="font-medium">{log.reason}</p>
                      <p className="text-sm text-muted-foreground">{new Date(log.created_at).toLocaleString()}</p>
                    </div>
                    <Badge variant={log.success ? 'default' : 'destructive'}>{log.success ? 'Success' : 'Failed'}</Badge>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default MultiCloudPage;
