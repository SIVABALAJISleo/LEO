import { useState, useEffect } from 'react';
import { firebaseClient as supabase } from '@/integrations/firebase/client';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';

export const DEFAULT_PERMISSIONS = [
  { resource: 'jobs', actions: ['create', 'read', 'update', 'delete'] },
  { resource: 'models', actions: ['create', 'read', 'update', 'delete'] },
  { resource: 'modules', actions: ['read', 'configure'] },
  { resource: 'settings', actions: ['read', 'update'] },
  { resource: 'team', actions: ['read', 'invite', 'remove'] },
];

export function useGovernanceData() {
  const { user } = useAuth();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [teams, setTeams] = useState<any[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [teamMembers, setTeamMembers] = useState<any[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [customRoles, setCustomRoles] = useState<any[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [workflows, setWorkflows] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (user) fetchAll();
  }, [user]);

  const fetchAll = async () => {
    setIsLoading(true);
    const [teamsRes, membersRes, rolesRes, workflowsRes] = await Promise.all([
      supabase.from('teams').select('*').order('created_at', { ascending: false }),
      supabase.from('team_members').select('*'),
      supabase.from('custom_roles').select('*'),
      supabase.from('approval_workflows').select('*'),
    ]);
    if (teamsRes.data) setTeams(teamsRes.data);
    if (membersRes.data) setTeamMembers(membersRes.data);
    if (rolesRes.data) setCustomRoles(rolesRes.data);
    if (workflowsRes.data) setWorkflows(workflowsRes.data);
    setIsLoading(false);
  };

  const createTeam = async (data: { name: string; description?: string }) => {
    if (!user) return;
    const { error } = await supabase.from('teams').insert({ ...data, owner_id: user.id });
    if (error) toast.error('Failed to create team');
    else { toast.success('Team created'); fetchAll(); }
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const createRole = async (teamId: string, data: { name: string; description?: string; permissions?: any[] }) => {
    const { error } = await supabase.from('custom_roles').insert({ ...data, team_id: teamId });
    if (error) toast.error('Failed to create role');
    else { toast.success('Role created'); fetchAll(); }
  };

  const createWorkflow = async (teamId: string, data: { name: string; workflow_type: string; description?: string }) => {
    const { error } = await supabase.from('approval_workflows').insert({ ...data, team_id: teamId });
    if (error) toast.error('Failed to create workflow');
    else { toast.success('Workflow created'); fetchAll(); }
  };

  const deleteTeam = async (id: string) => {
    const { error } = await supabase.from('teams').delete().eq('id', id);
    if (error) toast.error('Failed to delete');
    else { toast.success('Team deleted'); fetchAll(); }
  };

  return { teams, teamMembers, customRoles, workflows, isLoading, createTeam, createRole, createWorkflow, deleteTeam };
}
