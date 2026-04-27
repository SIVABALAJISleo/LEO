import { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Database, Shield, AlertTriangle, HardDrive, Globe, CheckCircle, XCircle, Clock } from 'lucide-react';
import { useDisasterRecoveryData } from '@/hooks/useDisasterRecoveryData';
import { LoadingState } from '@/components/ui/loading-state';
import { EmptyState } from '@/components/ui/empty-state';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';

const DisasterRecoveryPage = () => {
  const { backups, failovers, incidents, isLoading, createBackup, triggerFailover, resolveIncident } = useDisasterRecoveryData();
  const [isCreateBackupOpen, setIsCreateBackupOpen] = useState(false);
  const [isFailoverOpen, setIsFailoverOpen] = useState(false);
  const [newBackup, setNewBackup] = useState({ backup_type: 'full', region: 'us-east-1' });
  const [failoverData, setFailoverData] = useState({ from_region: 'us-east-1', to_region: 'eu-west-1', trigger_reason: 'manual' });

  const stats = useMemo(() => ({
    totalBackups: backups.length,
    totalBackupSize: backups.reduce((sum, b) => sum + (b.size_bytes || 0), 0),
    totalFailovers: failovers.length,
    successfulFailovers: failovers.filter(f => f.success).length,
    activeIncidents: incidents.filter(i => i.status !== 'resolved').length,
    avgFailoverTime: failovers.length > 0 ? Math.round(failovers.reduce((sum, f) => sum + (f.duration_ms || 0), 0) / failovers.length) : 0,
  }), [backups, failovers, incidents]);

  const handleCreateBackup = async () => {
    await createBackup(newBackup);
    setIsCreateBackupOpen(false);
    toast.success('Backup initiated');
  };

  const handleFailover = async () => {
    await triggerFailover(failoverData.from_region, failoverData.to_region, failoverData.trigger_reason);
    setIsFailoverOpen(false);
    toast.success('Failover initiated');
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (isLoading) return <LoadingState message="Loading disaster recovery..." />;

  return (
    <div className="space-y-6 p-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold">Disaster Recovery</h1>
          <p className="text-muted-foreground">Backups, failover, and incident management</p>
        </div>
        <div className="flex gap-2">
          <Dialog open={isCreateBackupOpen} onOpenChange={setIsCreateBackupOpen}>
            <DialogTrigger asChild>
              <Button variant="outline"><Database className="mr-2 h-4 w-4" /> Create Backup</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create Backup</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label className="mb-3 block text-sm font-medium">Backup Type</Label>
                  <Select value={newBackup.backup_type} onValueChange={(v) => setNewBackup({ ...newBackup, backup_type: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="full">Full Backup</SelectItem>
                      <SelectItem value="incremental">Incremental</SelectItem>
                      <SelectItem value="snapshot">Snapshot</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label className="mb-3 block text-sm font-medium">Region</Label>
                  <Select value={newBackup.region} onValueChange={(v) => setNewBackup({ ...newBackup, region: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="us-east-1">US East</SelectItem>
                      <SelectItem value="us-west-2">US West</SelectItem>
                      <SelectItem value="eu-west-1">EU West</SelectItem>
                      <SelectItem value="ap-southeast-1">Asia Pacific</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button onClick={handleCreateBackup} className="w-full">Start Backup</Button>
              </div>
            </DialogContent>
          </Dialog>
          <Dialog open={isFailoverOpen} onOpenChange={setIsFailoverOpen}>
            <DialogTrigger asChild>
              <Button variant="destructive"><Shield className="mr-2 h-4 w-4" /> Trigger Failover</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Trigger Failover</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label className="mb-3 block text-sm font-medium">From Region</Label>
                  <Select value={failoverData.from_region} onValueChange={(v) => setFailoverData({ ...failoverData, from_region: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="us-east-1">US East</SelectItem>
                      <SelectItem value="us-west-2">US West</SelectItem>
                      <SelectItem value="eu-west-1">EU West</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label className="mb-3 block text-sm font-medium">To Region</Label>
                  <Select value={failoverData.to_region} onValueChange={(v) => setFailoverData({ ...failoverData, to_region: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="us-east-1">US East</SelectItem>
                      <SelectItem value="us-west-2">US West</SelectItem>
                      <SelectItem value="eu-west-1">EU West</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label className="mb-3 block text-sm font-medium">Reason</Label>
                  <Input value={failoverData.trigger_reason} onChange={(e) => setFailoverData({ ...failoverData, trigger_reason: e.target.value })} placeholder="Failover reason" />
                </div>
                <Button onClick={handleFailover} variant="destructive" className="w-full">Initiate Failover</Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Total Backups</CardTitle></CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stats.totalBackups}</p>
            <p className="text-sm text-muted-foreground">{formatBytes(stats.totalBackupSize)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Failover Events</CardTitle></CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stats.totalFailovers}</p>
            <p className="text-sm text-primary">{stats.successfulFailovers} successful</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Active Incidents</CardTitle></CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-destructive">{stats.activeIncidents}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Avg Failover Time</CardTitle></CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stats.avgFailoverTime}ms</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="backups">
        <TabsList>
          <TabsTrigger value="backups">Backups</TabsTrigger>
          <TabsTrigger value="failovers">Failovers</TabsTrigger>
          <TabsTrigger value="incidents">Incidents</TabsTrigger>
        </TabsList>

        <TabsContent value="backups" className="space-y-4">
          {backups.length === 0 ? (
            <EmptyState title="No backups" description="Create your first backup" icon={Database} />
          ) : (
            <div className="space-y-2">
              {backups.map((b) => (
                <Card key={b.id}>
                  <CardContent className="flex justify-between items-center py-4">
                    <div className="flex items-center gap-4">
                      <HardDrive className="h-8 w-8 text-primary" />
                      <div>
                        <p className="font-medium">{b.backup_type}</p>
                        <p className="text-sm text-muted-foreground">{b.region} • {formatBytes(b.size_bytes || 0)}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <Badge variant={b.status === 'completed' ? 'default' : b.status === 'pending' ? 'secondary' : 'destructive'}>{b.status}</Badge>
                        <p className="text-sm text-muted-foreground mt-1">{new Date(b.created_at).toLocaleString()}</p>
                      </div>
                      {b.encrypted && <Shield className="h-4 w-4 text-primary" />}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="failovers" className="space-y-4">
          {failovers.length === 0 ? (
            <EmptyState title="No failover events" description="Failover history will appear here" icon={Globe} />
          ) : (
            <div className="space-y-2">
              {failovers.map((f) => (
                <Card key={f.id}>
                  <CardContent className="flex justify-between items-center py-4">
                    <div className="flex items-center gap-4">
                      {f.success ? <CheckCircle className="h-8 w-8 text-primary" /> : <XCircle className="h-8 w-8 text-destructive" />}
                      <div>
                        <p className="font-medium">{f.from_region} → {f.to_region}</p>
                        <p className="text-sm text-muted-foreground">{f.trigger_reason}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="font-medium">{f.duration_ms}ms</p>
                        <p className="text-sm text-muted-foreground">{new Date(f.created_at).toLocaleString()}</p>
                      </div>
                      {f.data_loss_bytes && f.data_loss_bytes > 0 && (
                        <Badge variant="destructive">Data Loss: {formatBytes(f.data_loss_bytes)}</Badge>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="incidents" className="space-y-4">
          {incidents.length === 0 ? (
            <EmptyState title="No incidents" description="Incident reports will appear here" icon={AlertTriangle} />
          ) : (
            <div className="space-y-2">
              {incidents.map((i) => (
                <Card key={i.id} className={i.status === 'active' ? 'border-destructive' : ''}>
                  <CardContent className="py-4">
                    <div className="flex justify-between items-start">
                      <div className="flex items-center gap-4">
                        <AlertTriangle className={`h-8 w-8 ${i.severity === 'critical' ? 'text-destructive' : i.severity === 'high' ? 'text-orange-500' : 'text-yellow-500'}`} />
                        <div>
                          <p className="font-medium">{i.title}</p>
                          {i.description && <p className="text-sm text-muted-foreground">{i.description}</p>}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={i.severity === 'critical' ? 'destructive' : i.severity === 'high' ? 'default' : 'secondary'}>{i.severity}</Badge>
                        <Badge variant={i.status === 'resolved' ? 'outline' : 'destructive'}>{i.status}</Badge>
                      </div>
                    </div>
                    <div className="mt-4 flex justify-between items-center">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Clock className="h-4 w-4" />
                        <span>Started: {new Date(i.started_at).toLocaleString()}</span>
                        {i.resolved_at && <span>• Resolved: {new Date(i.resolved_at).toLocaleString()}</span>}
                      </div>
                      {i.status !== 'resolved' && (
                        <Button size="sm" onClick={() => resolveIncident(i.id, 'Manual resolution')}>Resolve</Button>
                      )}
                    </div>
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

export default DisasterRecoveryPage;