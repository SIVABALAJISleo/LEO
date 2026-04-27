import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Shield, Plus, Play, AlertTriangle } from 'lucide-react';
import { useSecurityData, COMPLIANCE_FRAMEWORKS } from '@/hooks/useSecurityData';
import { LoadingState } from '@/components/ui/loading-state';
import { EmptyState } from '@/components/ui/empty-state';

const SecurityPage = () => {
  const { securityEvents, auditLogs, complianceChecks, threats, isLoading, createComplianceCheck, runComplianceCheck, mitigateThreat, getSecurityScore } = useSecurityData();
  const [checkName, setCheckName] = useState('');
  const [framework, setFramework] = useState('soc2');
  const score = getSecurityScore();

  if (isLoading) return <LoadingState message="Loading security data..." />;

  return (
    <div className="space-y-6 p-6">
      <div><h1 className="text-3xl font-bold">Zero Trust & Compliance</h1><p className="text-muted-foreground">RBAC, threat detection, and compliance scoring</p></div>
      
      <div className="grid gap-4 md:grid-cols-4">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Security Score</CardTitle></CardHeader><CardContent><p className={`text-2xl font-bold ${score >= 80 ? 'text-primary' : score >= 60 ? 'text-yellow-500' : 'text-destructive'}`}>{score}%</p></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Events (24h)</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{securityEvents.length}</p></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Active Threats</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold text-destructive">{threats.filter(t => t.mitigation_status !== 'mitigated').length}</p></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Compliance Checks</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{complianceChecks.length}</p></CardContent></Card>
      </div>

      <Tabs defaultValue="compliance">
        <TabsList><TabsTrigger value="compliance">Compliance</TabsTrigger><TabsTrigger value="threats">Threats</TabsTrigger><TabsTrigger value="audit">Audit Log</TabsTrigger></TabsList>
        
        <TabsContent value="compliance" className="space-y-4">
          <Card><CardHeader><CardTitle>Create Compliance Check</CardTitle></CardHeader>
            <CardContent className="flex gap-4">
              <Input placeholder="Check name" value={checkName} onChange={(e) => setCheckName(e.target.value)} className="w-48" />
              <Select value={framework} onValueChange={setFramework}><SelectTrigger className="w-40"><SelectValue /></SelectTrigger><SelectContent>{COMPLIANCE_FRAMEWORKS.map(f => <SelectItem key={f.value} value={f.value}>{f.label}</SelectItem>)}</SelectContent></Select>
              <Button onClick={() => { createComplianceCheck({ check_name: checkName, framework }); setCheckName(''); }}><Plus className="mr-2 h-4 w-4" />Create</Button>
            </CardContent>
          </Card>
          {complianceChecks.length === 0 ? <EmptyState title="No checks" description="Create compliance checks" icon={Shield} /> : complianceChecks.map(c => (
            <Card key={c.id}><CardContent className="flex justify-between items-center py-3"><div><p className="font-medium">{c.check_name}</p><p className="text-sm text-muted-foreground">{COMPLIANCE_FRAMEWORKS.find(f => f.value === c.framework)?.label}</p></div>
              <div className="flex items-center gap-2">{c.score && <span className="font-bold">{c.score}%</span>}<Badge>{c.status}</Badge><Button size="sm" onClick={() => runComplianceCheck(c.id)}><Play className="h-4 w-4" /></Button></div>
            </CardContent></Card>
          ))}
        </TabsContent>
        
        <TabsContent value="threats">{threats.length === 0 ? <EmptyState title="No threats" description="No threats detected" /> : threats.map(t => (
          <Card key={t.id} className="mb-2"><CardContent className="flex justify-between items-center py-3"><div className="flex items-center gap-3"><AlertTriangle className={t.severity === 'critical' ? 'text-destructive' : 'text-yellow-500'} /><div><p className="font-medium">{t.threat_type}</p><p className="text-sm text-muted-foreground">{t.description}</p></div></div>
            <div className="flex items-center gap-2"><Badge variant={t.severity === 'critical' ? 'destructive' : 'default'}>{t.severity}</Badge>{t.mitigation_status !== 'mitigated' && <Button size="sm" onClick={() => mitigateThreat(t.id)}>Mitigate</Button>}</div>
          </CardContent></Card>
        ))}</TabsContent>
        
        <TabsContent value="audit">{auditLogs.slice(0, 20).map(l => <Card key={l.id} className="mb-2"><CardContent className="flex justify-between py-3"><div><p className="font-medium">{l.action}</p><p className="text-sm text-muted-foreground">{l.resource_type} • {new Date(l.created_at).toLocaleString()}</p></div></CardContent></Card>)}</TabsContent>
      </Tabs>
    </div>
  );
};

export default SecurityPage;
