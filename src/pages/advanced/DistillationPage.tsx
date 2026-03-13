import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Brain, Play, RotateCcw, Trash2, Sparkles, Plus } from 'lucide-react';
import { useDistillationData, DISTILLATION_TYPES, SPECIALIZATIONS, DISTILLATION_STAGES } from '@/hooks/useDistillationData';
import { LoadingState } from '@/components/ui/loading-state';
import { EmptyState } from '@/components/ui/empty-state';

const DistillationPage = () => {
  const { models, jobs, teacherModels, isLoading, createDistilledModel, startDistillation, rollbackToStage, deleteModel, findSweetSpot } = useDistillationData();
  const [newModelName, setNewModelName] = useState('');
  const [selectedTeacher, setSelectedTeacher] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [selectedSpec, setSelectedSpec] = useState('');

  const handleCreate = async () => {
    if (!newModelName.trim()) return;
    await createDistilledModel({ name: newModelName, teacher_model_id: selectedTeacher || undefined, specialization: selectedSpec || undefined });
    setNewModelName('');
  };

  if (isLoading) return <LoadingState message="Loading distillation data..." />;

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Model Distillation Pipeline</h1>
          <p className="text-muted-foreground">Create optimized student models from teacher models</p>
        </div>
      </div>

      <Tabs defaultValue="models">
        <TabsList>
          <TabsTrigger value="models">Distilled Models</TabsTrigger>
          <TabsTrigger value="jobs">Jobs Queue</TabsTrigger>
          <TabsTrigger value="create">Create New</TabsTrigger>
        </TabsList>

        <TabsContent value="models" className="space-y-4">
          {models.length === 0 ? (
            <EmptyState title="No distilled models" description="Create your first distilled model to get started" icon={Brain} />
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {models.map((model) => {
                const sweetSpot = findSweetSpot(model.id);
                return (
                  <Card key={model.id}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle>{model.name}</CardTitle>
                        <Badge>{model.status}</Badge>
                      </div>
                      <CardDescription>{model.specialization || 'General'} • Stage {model.current_stage}/5</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-3 gap-2 text-center text-sm">
                        <div><p className="text-muted-foreground">Accuracy</p><p className="font-bold">{model.accuracy ? `${model.accuracy}%` : '-'}</p></div>
                        <div><p className="text-muted-foreground">Latency</p><p className="font-bold">{model.latency_ms ? `${model.latency_ms}ms` : '-'}</p></div>
                        <div><p className="text-muted-foreground">Compression</p><p className="font-bold">{model.compression_ratio ? `${model.compression_ratio}x` : '-'}</p></div>
                      </div>
                      <div className="space-y-1">
                        <p className="text-xs text-muted-foreground">Stages</p>
                        <div className="flex gap-1">
                          {DISTILLATION_STAGES.map((s) => (
                            <div key={s.stage} className={`flex-1 h-2 rounded ${model.current_stage >= s.stage ? 'bg-primary' : 'bg-muted'}`} title={s.name} />
                          ))}
                        </div>
                      </div>
                      {sweetSpot && (
                        <div className="p-2 bg-primary/10 rounded text-sm">
                          <Sparkles className="h-4 w-4 inline mr-1" />Sweet Spot: Stage {sweetSpot.stage} - {sweetSpot.reason}
                        </div>
                      )}
                      <div className="flex gap-2">
                        <Button size="sm" onClick={() => startDistillation(model.id, 'attention_transfer', model.current_stage + 1)}><Play className="h-4 w-4 mr-1" />Next Stage</Button>
                        <Button size="sm" variant="outline" onClick={() => rollbackToStage(model.id, Math.max(1, model.current_stage - 1))}><RotateCcw className="h-4 w-4" /></Button>
                        <Button size="sm" variant="destructive" onClick={() => deleteModel(model.id)}><Trash2 className="h-4 w-4" /></Button>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </TabsContent>

        <TabsContent value="jobs" className="space-y-4">
          {jobs.length === 0 ? (
            <EmptyState title="No jobs" description="Start a distillation job from a model" />
          ) : (
            jobs.map((job) => (
              <Card key={job.id}>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{job.distillation_type}</CardTitle>
                    <Badge variant={job.status === 'running' ? 'default' : job.status === 'completed' ? 'secondary' : 'outline'}>{job.status}</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <Progress value={job.progress || 0} className="h-2" />
                  <p className="text-sm text-muted-foreground mt-2">Stage {job.stage} • Priority {job.priority}</p>
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>

        <TabsContent value="create">
          <Card>
            <CardHeader>
              <CardTitle>Create Distilled Model</CardTitle>
              <CardDescription>Define a new student model for knowledge distillation</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input placeholder="Model name" value={newModelName} onChange={(e) => setNewModelName(e.target.value)} />
              <Select value={selectedTeacher} onValueChange={setSelectedTeacher}>
                <SelectTrigger><SelectValue placeholder="Select teacher model" /></SelectTrigger>
                <SelectContent>{teacherModels.map((m) => <SelectItem key={m.id} value={m.id}>{m.name}</SelectItem>)}</SelectContent>
              </Select>
              <Select value={selectedType} onValueChange={setSelectedType}>
                <SelectTrigger><SelectValue placeholder="Distillation type" /></SelectTrigger>
                <SelectContent>{DISTILLATION_TYPES.map((t) => <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>)}</SelectContent>
              </Select>
              <Select value={selectedSpec} onValueChange={setSelectedSpec}>
                <SelectTrigger><SelectValue placeholder="Specialization (optional)" /></SelectTrigger>
                <SelectContent>{SPECIALIZATIONS.map((s) => <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>)}</SelectContent>
              </Select>
              <Button onClick={handleCreate}><Plus className="mr-2 h-4 w-4" />Create Model</Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default DistillationPage;
