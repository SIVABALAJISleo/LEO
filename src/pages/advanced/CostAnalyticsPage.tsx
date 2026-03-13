import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { DollarSign, Plus, TrendingUp } from 'lucide-react';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { useCostAnalyticsData, RESOURCE_TYPES } from '@/hooks/useCostAnalyticsData';
import { LoadingState } from '@/components/ui/loading-state';
import { EmptyState } from '@/components/ui/empty-state';

const CostAnalyticsPage = () => {
  const { transactions, predictions, budgets, isLoading, createBudget, getTotalSpent, getTotalBudget, getSpentByCategory } = useCostAnalyticsData();
  const [budgetName, setBudgetName] = useState('');
  const [budgetAmount, setBudgetAmount] = useState('');
  const totalSpent = getTotalSpent();
  const totalBudget = getTotalBudget();
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const byCategory = getSpentByCategory();

  if (isLoading) return <LoadingState message="Loading cost data..." />;

  return (
    <div className="space-y-6 p-6">
      <div><h1 className="text-3xl font-bold">Cost Analytics</h1><p className="text-muted-foreground">Real-time cost tracking, forecasts, and budget controls</p></div>
      
      <div className="grid gap-4 md:grid-cols-4">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Total Spent</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">${totalSpent.toFixed(2)}</p></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Total Budget</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">${totalBudget.toFixed(2)}</p></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Budget Used</CardTitle></CardHeader><CardContent><p className={`text-2xl font-bold ${totalBudget > 0 && (totalSpent / totalBudget) > 0.8 ? 'text-destructive' : ''}`}>{totalBudget > 0 ? ((totalSpent / totalBudget) * 100).toFixed(1) : 0}%</p></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Transactions</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{transactions.length}</p></CardContent></Card>
      </div>

      <Tabs defaultValue="budgets">
        <TabsList><TabsTrigger value="budgets">Budgets</TabsTrigger><TabsTrigger value="transactions">Transactions</TabsTrigger><TabsTrigger value="predictions">Predictions</TabsTrigger></TabsList>
        
        <TabsContent value="budgets" className="space-y-4">
          <Card><CardHeader><CardTitle>Create Budget</CardTitle></CardHeader>
            <CardContent className="flex gap-4">
              <Input placeholder="Budget name" value={budgetName} onChange={(e) => setBudgetName(e.target.value)} />
              <Input type="number" placeholder="Amount" value={budgetAmount} onChange={(e) => setBudgetAmount(e.target.value)} className="w-32" />
              <Button onClick={() => { createBudget({ name: budgetName, total_budget: parseFloat(budgetAmount), period_start: new Date().toISOString().split('T')[0], period_end: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] }); setBudgetName(''); setBudgetAmount(''); }}><Plus className="mr-2 h-4 w-4" />Create</Button>
            </CardContent>
          </Card>
          {budgets.length === 0 ? <EmptyState title="No budgets" description="Create a budget to track spending" icon={DollarSign} /> : budgets.map(b => (
            <Card key={b.id}><CardContent className="flex justify-between items-center py-3"><div><p className="font-medium">{b.name}</p><p className="text-sm text-muted-foreground">${b.spent_amount?.toFixed(2) || 0} / ${b.total_budget}</p></div>
              <div className="flex items-center gap-2"><div className="w-32 bg-muted rounded-full h-2"><div className="bg-primary h-2 rounded-full" style={{ width: `${Math.min((b.spent_amount || 0) / b.total_budget * 100, 100)}%` }} /></div><Badge variant={b.is_active ? 'default' : 'outline'}>{b.is_active ? 'Active' : 'Inactive'}</Badge></div>
            </CardContent></Card>
          ))}
        </TabsContent>
        
        <TabsContent value="transactions">{transactions.length === 0 ? <EmptyState title="No transactions" description="No cost transactions recorded" /> : transactions.slice(0, 20).map(t => (
          <Card key={t.id} className="mb-2"><CardContent className="flex justify-between py-3"><div><p className="font-medium">{t.resource_type}</p><p className="text-sm text-muted-foreground">{t.category || 'Uncategorized'} • {new Date(t.transaction_at).toLocaleDateString()}</p></div><span className="font-bold">${t.amount.toFixed(2)}</span></CardContent></Card>
        ))}</TabsContent>
        
        <TabsContent value="predictions">{predictions.length === 0 ? <EmptyState title="No predictions" description="Cost predictions will appear here" icon={TrendingUp} /> : predictions.map(p => (
          <Card key={p.id} className="mb-2"><CardContent className="grid grid-cols-4 gap-4 py-3"><div><span className="text-muted-foreground">Resource:</span> {p.resource_type}</div><div><span className="text-muted-foreground">Predicted:</span> ${p.predicted_amount.toFixed(2)}</div><div><span className="text-muted-foreground">Period:</span> {p.prediction_period}</div><div><span className="text-muted-foreground">Date:</span> {p.prediction_date}</div></CardContent></Card>
        ))}</TabsContent>
      </Tabs>
    </div>
  );
};

export default CostAnalyticsPage;
