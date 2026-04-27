import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Users, Shield, GitBranch, Plus, UserPlus, Settings } from 'lucide-react';
import { useGovernanceData } from '@/hooks/useGovernanceData';
import { LoadingState } from '@/components/ui/loading-state';
import { EmptyState } from '@/components/ui/empty-state';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';

const GovernancePage = () => {
  const { teams, teamMembers, customRoles, workflows, isLoading, createTeam, createRole, createWorkflow } = useGovernanceData();
  const [isCreateTeamOpen, setIsCreateTeamOpen] = useState(false);
  const [isCreateRoleOpen, setIsCreateRoleOpen] = useState(false);
  const [isCreateWorkflowOpen, setIsCreateWorkflowOpen] = useState(false);
  const [selectedTeamId, setSelectedTeamId] = useState<string>('');
  const [newTeam, setNewTeam] = useState({ name: '', description: '' });
  const [newRole, setNewRole] = useState({ name: '', description: '' });
  const [newWorkflow, setNewWorkflow] = useState({ name: '', description: '', workflow_type: 'approval' });

  const handleCreateTeam = async () => {
    if (!newTeam.name) {
      toast.error('Team name is required');
      return;
    }
    await createTeam(newTeam);
    setNewTeam({ name: '', description: '' });
    setIsCreateTeamOpen(false);
  };

  const handleCreateRole = async () => {
    if (!newRole.name) {
      toast.error('Role name is required');
      return;
    }
    if (!selectedTeamId) {
      toast.error('Please select a team first');
      return;
    }
    await createRole(selectedTeamId, newRole);
    setNewRole({ name: '', description: '' });
    setIsCreateRoleOpen(false);
  };

  const handleCreateWorkflow = async () => {
    if (!newWorkflow.name) {
      toast.error('Workflow name is required');
      return;
    }
    if (!selectedTeamId) {
      toast.error('Please select a team first');
      return;
    }
    await createWorkflow(selectedTeamId, newWorkflow);
    setNewWorkflow({ name: '', description: '', workflow_type: 'approval' });
    setIsCreateWorkflowOpen(false);
  };

  if (isLoading) return <LoadingState message="Loading governance..." />;

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Governance</h1>
        <p className="text-muted-foreground">Team management, roles, and approval workflows</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Teams</CardTitle></CardHeader>
          <CardContent><p className="text-2xl font-bold">{teams.length}</p></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Members</CardTitle></CardHeader>
          <CardContent><p className="text-2xl font-bold">{teamMembers.length}</p></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Custom Roles</CardTitle></CardHeader>
          <CardContent><p className="text-2xl font-bold">{customRoles.length}</p></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Active Workflows</CardTitle></CardHeader>
          <CardContent><p className="text-2xl font-bold">{workflows.filter(w => w.is_active).length}</p></CardContent>
        </Card>
      </div>

      <Tabs defaultValue="teams">
        <TabsList>
          <TabsTrigger value="teams">Teams</TabsTrigger>
          <TabsTrigger value="roles">Roles</TabsTrigger>
          <TabsTrigger value="workflows">Workflows</TabsTrigger>
        </TabsList>

        <TabsContent value="teams" className="space-y-4">
          <div className="flex justify-end">
            <Dialog open={isCreateTeamOpen} onOpenChange={setIsCreateTeamOpen}>
              <DialogTrigger asChild>
                <Button><Plus className="mr-2 h-4 w-4" /> New Team</Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create Team</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label>Name</Label>
                    <Input value={newTeam.name} onChange={(e) => setNewTeam({ ...newTeam, name: e.target.value })} placeholder="Team name" />
                  </div>
                  <div>
                    <Label>Description</Label>
                    <Textarea value={newTeam.description} onChange={(e) => setNewTeam({ ...newTeam, description: e.target.value })} placeholder="Team description" />
                  </div>
                  <Button onClick={handleCreateTeam} className="w-full">Create Team</Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
          {teams.length === 0 ? (
            <EmptyState title="No teams" description="Create your first team to organize members" icon={Users} />
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {teams.map((t) => (
                <Card key={t.id} className="hover:border-primary/50 transition-colors">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded bg-primary/20 flex items-center justify-center">
                          <Users className="h-5 w-5 text-primary" />
                        </div>
                        <CardTitle className="text-lg">{t.name}</CardTitle>
                      </div>
                    </div>
                    {t.description && <p className="text-sm text-muted-foreground mt-2">{t.description}</p>}
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">{teamMembers.filter(m => m.team_id === t.id).length} members</span>
                      <Button size="sm" variant="outline"><UserPlus className="h-4 w-4 mr-1" /> Invite</Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="roles" className="space-y-4">
          <div className="flex justify-between items-center">
            {teams.length > 0 && (
              <Select value={selectedTeamId} onValueChange={setSelectedTeamId}>
                <SelectTrigger className="w-[200px]">
                  <SelectValue placeholder="Select team" />
                </SelectTrigger>
                <SelectContent>
                  {teams.map(t => (
                    <SelectItem key={t.id} value={t.id}>{t.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
            <Dialog open={isCreateRoleOpen} onOpenChange={setIsCreateRoleOpen}>
              <DialogTrigger asChild>
                <Button><Plus className="mr-2 h-4 w-4" /> New Role</Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create Custom Role</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label>Name</Label>
                    <Input value={newRole.name} onChange={(e) => setNewRole({ ...newRole, name: e.target.value })} placeholder="Role name" />
                  </div>
                  <div>
                    <Label>Description</Label>
                    <Textarea value={newRole.description} onChange={(e) => setNewRole({ ...newRole, description: e.target.value })} placeholder="Role description" />
                  </div>
                  <Button onClick={handleCreateRole} className="w-full">Create Role</Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
          {customRoles.length === 0 ? (
            <EmptyState title="No custom roles" description="Create roles to define permissions" icon={Shield} />
          ) : (
            <div className="space-y-2">
              {customRoles.map((r) => (
                <Card key={r.id}>
                  <CardContent className="flex justify-between items-center py-4">
                    <div className="flex items-center gap-4">
                      <Shield className="h-8 w-8 text-primary" />
                      <div>
                        <p className="font-medium">{r.name}</p>
                        {r.description && <p className="text-sm text-muted-foreground">{r.description}</p>}
                      </div>
                    </div>
                    <Button size="sm" variant="outline"><Settings className="h-4 w-4 mr-1" /> Configure</Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="workflows" className="space-y-4">
          <div className="flex justify-between items-center">
            {teams.length > 0 && (
              <Select value={selectedTeamId} onValueChange={setSelectedTeamId}>
                <SelectTrigger className="w-[200px]">
                  <SelectValue placeholder="Select team" />
                </SelectTrigger>
                <SelectContent>
                  {teams.map(t => (
                    <SelectItem key={t.id} value={t.id}>{t.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
            <Dialog open={isCreateWorkflowOpen} onOpenChange={setIsCreateWorkflowOpen}>
              <DialogTrigger asChild>
                <Button><Plus className="mr-2 h-4 w-4" /> New Workflow</Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create Workflow</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label>Name</Label>
                    <Input value={newWorkflow.name} onChange={(e) => setNewWorkflow({ ...newWorkflow, name: e.target.value })} placeholder="Workflow name" />
                  </div>
                  <div>
                    <Label>Description</Label>
                    <Textarea value={newWorkflow.description} onChange={(e) => setNewWorkflow({ ...newWorkflow, description: e.target.value })} placeholder="Workflow description" />
                  </div>
                  <div>
                    <Label>Type</Label>
                    <Select value={newWorkflow.workflow_type} onValueChange={(v) => setNewWorkflow({ ...newWorkflow, workflow_type: v })}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="approval">Approval</SelectItem>
                        <SelectItem value="review">Review</SelectItem>
                        <SelectItem value="deployment">Deployment</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Button onClick={handleCreateWorkflow} className="w-full">Create Workflow</Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
          {workflows.length === 0 ? (
            <EmptyState title="No workflows" description="Create approval workflows for governance" icon={GitBranch} />
          ) : (
            <div className="space-y-2">
              {workflows.map((w) => (
                <Card key={w.id}>
                  <CardContent className="flex justify-between items-center py-4">
                    <div className="flex items-center gap-4">
                      <GitBranch className="h-8 w-8 text-primary" />
                      <div>
                        <p className="font-medium">{w.name}</p>
                        <p className="text-sm text-muted-foreground">{w.workflow_type}</p>
                      </div>
                    </div>
                    <Badge variant={w.is_active ? 'default' : 'secondary'}>{w.is_active ? 'Active' : 'Inactive'}</Badge>
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

export default GovernancePage;