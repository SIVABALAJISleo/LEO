import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Layers, Plus, Trash2 } from 'lucide-react';
import { useFusionData, FUSION_STRATEGIES, CONFLICT_RESOLUTIONS } from '@/hooks/useFusionData';
import { LoadingState } from '@/components/ui/loading-state';
import { EmptyState } from '@/components/ui/empty-state';

const FusionPage = () => {
  const { fusedModels, strategies, isLoading, createFusedModel, createStrategy, deleteFusedModel } = useFusionData();
  const [modelName, setModelName] = useState('');
  const [fusionStrategy, setFusionStrategy] = useState('late');
  const [strategyName, setStrategyName] = useState('');
  const [strategyType, setStrategyType] = useState('late');
  const [conflictRes, setConflictRes] = useState('weighted_average');

  if (isLoading) return <LoadingState message="Loading fusion data..." />;

  return (
    <div className="space-y-6 p-6">
      <div><h1 className="text-3xl font-bold">Neural Model Fusion</h1><p className="text-muted-foreground">Combine multiple models with intelligent fusion strategies</p></div>
      
      <div className="grid gap-4 md:grid-cols-3">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Fused Models</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{fusedModels.length}</p></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Active Strategies</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{strategies.filter(s => s.is_active).length}</p></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Avg Accuracy</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{fusedModels.length ? (fusedModels.filter(m => m.accuracy).reduce((s, m) => s + m.accuracy, 0) / fusedModels.filter(m => m.accuracy).length || 0).toFixed(1) : 0}%</p></CardContent></Card>
      </div>

      <Tabs defaultValue="models">
        <TabsList><TabsTrigger value="models">Fused Models</TabsTrigger><TabsTrigger value="strategies">Strategies</TabsTrigger></TabsList>
        
        <TabsContent value="models" className="space-y-4">
          <Card><CardHeader><CardTitle>Create Fused Model</CardTitle></CardHeader>
            <CardContent className="flex gap-4 flex-wrap">
              <Input placeholder="Model name" value={modelName} onChange={(e) => setModelName(e.target.value)} className="w-48" />
              <Select value={fusionStrategy} onValueChange={setFusionStrategy}><SelectTrigger className="w-48"><SelectValue /></SelectTrigger><SelectContent>{FUSION_STRATEGIES.map(s => <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>)}</SelectContent></Select>
              <Button onClick={() => { createFusedModel({ name: modelName, fusion_strategy: fusionStrategy }); setModelName(''); }}><Plus className="mr-2 h-4 w-4" />Create</Button>
            </CardContent>
          </Card>
          {fusedModels.length === 0 ? <EmptyState title="No fused models" description="Create your first fused model" icon={Layers} /> : (
            <div className="grid gap-4 md:grid-cols-2">{fusedModels.map(m => (
              <Card key={m.id}><CardHeader><div className="flex justify-between"><CardTitle>{m.name}</CardTitle><Badge>{m.status}</Badge></div><CardDescription>{FUSION_STRATEGIES.find(s => s.value === m.fusion_strategy)?.label}</CardDescription></CardHeader>
                <CardContent><div className="grid grid-cols-2 gap-2 text-sm mb-3"><div><span className="text-muted-foreground">Accuracy:</span> {m.accuracy ? `${m.accuracy}%` : 'N/A'}</div><div><span className="text-muted-foreground">Latency:</span> {m.latency_ms ? `${m.latency_ms}ms` : 'N/A'}</div></div>
                  <Button size="sm" variant="destructive" onClick={() => deleteFusedModel(m.id)}><Trash2 className="h-4 w-4" /></Button>
                </CardContent>
              </Card>
            ))}</div>
          )}
        </TabsContent>
        
        <TabsContent value="strategies" className="space-y-4">
          <Card><CardHeader><CardTitle>Create Strategy</CardTitle></CardHeader>
            <CardContent className="flex gap-4 flex-wrap">
              <Input placeholder="Strategy name" value={strategyName} onChange={(e) => setStrategyName(e.target.value)} className="w-48" />
              <Select value={strategyType} onValueChange={setStrategyType}><SelectTrigger className="w-40"><SelectValue /></SelectTrigger><SelectContent>{FUSION_STRATEGIES.map(s => <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>)}</SelectContent></Select>
              <Select value={conflictRes} onValueChange={setConflictRes}><SelectTrigger className="w-48"><SelectValue /></SelectTrigger><SelectContent>{CONFLICT_RESOLUTIONS.map(c => <SelectItem key={c.value} value={c.value}>{c.label}</SelectItem>)}</SelectContent></Select>
              <Button onClick={() => { createStrategy({ name: strategyName, strategy_type: strategyType, conflict_resolution: conflictRes }); setStrategyName(''); }}><Plus className="mr-2 h-4 w-4" />Create</Button>
            </CardContent>
          </Card>
          {strategies.map(s => <Card key={s.id}><CardContent className="flex justify-between items-center py-3"><div><p className="font-medium">{s.name}</p><p className="text-sm text-muted-foreground">{s.strategy_type} • {s.conflict_resolution}</p></div><Badge variant={s.is_active ? 'default' : 'outline'}>{s.is_active ? 'Active' : 'Inactive'}</Badge></CardContent></Card>)}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default FusionPage;
