import { useState, useEffect } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';

export const COMPLIANCE_FRAMEWORKS = [
  { value: 'soc2', label: 'SOC 2' },
  { value: 'gdpr', label: 'GDPR' },
  { value: 'hipaa', label: 'HIPAA' },
  { value: 'pci_dss', label: 'PCI DSS' },
  { value: 'iso27001', label: 'ISO 27001' },
];

export function useSecurityData() {
  const { user } = useAuth();
  const [securityEvents, setSecurityEvents] = useState<any[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [complianceChecks, setComplianceChecks] = useState<any[]>([]);
  const [threats, setThreats] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (user) fetchAll();
  }, [user]);

  const fetchAll = async () => {
    setIsLoading(true);
    const [eventsRes, logsRes, checksRes, threatsRes] = await Promise.all([
      supabase.from('security_events').select('*').order('created_at', { ascending: false }).limit(100),
      supabase.from('immutable_audit_logs').select('*').order('created_at', { ascending: false }).limit(100),
      supabase.from('compliance_checks').select('*').order('created_at', { ascending: false }),
      supabase.from('threats_detected').select('*').order('detected_at', { ascending: false }),
    ]);
    if (eventsRes.data) setSecurityEvents(eventsRes.data);
    if (logsRes.data) setAuditLogs(logsRes.data);
    if (checksRes.data) setComplianceChecks(checksRes.data);
    if (threatsRes.data) setThreats(threatsRes.data);
    setIsLoading(false);
  };

  const createComplianceCheck = async (data: { check_name: string; framework: string }) => {
    if (!user) return;
    const { error } = await supabase.from('compliance_checks').insert({ ...data, user_id: user.id, status: 'pending' });
    if (error) toast.error('Failed to create check');
    else { toast.success('Compliance check created'); fetchAll(); }
  };

  const runComplianceCheck = async (id: string) => {
    // HONEST: Score is null/pending until real compliance check runs
    const { error } = await supabase.from('compliance_checks').update({ 
      status: 'pending_verification', 
      score: null, // Will be set by actual compliance verification
      last_run_at: new Date().toISOString() 
    }).eq('id', id);
    if (error) toast.error('Failed to run check');
    else { toast.success('Compliance check queued for verification'); fetchAll(); }
  };

  const mitigateThreat = async (id: string) => {
    const { error } = await supabase.from('threats_detected').update({ mitigation_status: 'mitigated', mitigated_at: new Date().toISOString() }).eq('id', id);
    if (error) toast.error('Failed to mitigate');
    else { toast.success('Threat mitigated'); fetchAll(); }
  };

  const getSecurityScore = () => {
    if (complianceChecks.length === 0) return 0;
    const scores = complianceChecks.filter(c => c.score).map(c => c.score);
    return scores.length ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0;
  };

  return { securityEvents, auditLogs, complianceChecks, threats, isLoading, createComplianceCheck, runComplianceCheck, mitigateThreat, getSecurityScore };
}
