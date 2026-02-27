import { useState, useEffect } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';

export const RESOURCE_TYPES = [
  { value: 'compute', label: 'Compute' },
  { value: 'storage', label: 'Storage' },
  { value: 'network', label: 'Network' },
  { value: 'inference', label: 'Inference' },
  { value: 'training', label: 'Training' },
];

export function useCostAnalyticsData() {
  const { user } = useAuth();
  const [transactions, setTransactions] = useState<any[]>([]);
  const [predictions, setPredictions] = useState<any[]>([]);
  const [budgets, setBudgets] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (user) fetchAll();
  }, [user]);

  const fetchAll = async () => {
    setIsLoading(true);
    const [txRes, predRes, budgetRes] = await Promise.all([
      supabase.from('cost_transactions').select('*').order('transaction_at', { ascending: false }).limit(100),
      supabase.from('cost_predictions').select('*').order('prediction_date', { ascending: false }),
      supabase.from('budget_allocations').select('*').order('created_at', { ascending: false }),
    ]);
    if (txRes.data) setTransactions(txRes.data);
    if (predRes.data) setPredictions(predRes.data);
    if (budgetRes.data) setBudgets(budgetRes.data);
    setIsLoading(false);
  };

  const createBudget = async (data: { name: string; total_budget: number; period_start: string; period_end: string; category?: string }) => {
    if (!user) return;
    const { error } = await supabase.from('budget_allocations').insert({ ...data, user_id: user.id });
    if (error) toast.error('Failed to create budget');
    else { toast.success('Budget created'); fetchAll(); }
  };

  const recordTransaction = async (data: { resource_type: string; amount: number; category?: string }) => {
    if (!user) return;
    const { error } = await supabase.from('cost_transactions').insert({ ...data, user_id: user.id });
    if (error) toast.error('Failed to record');
    else fetchAll();
  };

  const getTotalSpent = () => transactions.reduce((sum, t) => sum + (t.amount || 0), 0);
  
  const getTotalBudget = () => budgets.filter(b => b.is_active).reduce((sum, b) => sum + (b.total_budget || 0), 0);

  const getSpentByCategory = () => {
    const byCategory: Record<string, number> = {};
    transactions.forEach(t => {
      const cat = t.category || 'Other';
      byCategory[cat] = (byCategory[cat] || 0) + (t.amount || 0);
    });
    return byCategory;
  };

  return { transactions, predictions, budgets, isLoading, createBudget, recordTransaction, getTotalSpent, getTotalBudget, getSpentByCategory };
}
