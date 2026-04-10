import { useState, useEffect } from 'react';
import { Settings, RotateCcw, Save, TrendingUp } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import { ModuleData, ModuleStats, useModulesData } from '@/hooks/useModulesData';
import { Json } from '@/integrations/supabase/types';
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from '@/components/ui/chart';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer } from 'recharts';

interface ConfigureModalProps {
  module: ModuleData | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ConfigureModal({ module, open, onOpenChange }: ConfigureModalProps) {
  const { updateModuleSettings, resetModuleSettings, getDefaultSettings, fetchModuleStats } = useModulesData();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [settings, setSettings] = useState<Record<string, any>>({});
  const [saving, setSaving] = useState(false);
  const [stats, setStats] = useState<ModuleStats | null>(null);
  const [loadingStats, setLoadingStats] = useState(false);

  useEffect(() => {
    if (module && open) {
      const currentSettings = module.config?.settings;
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const defaults = getDefaultSettings(module.name) as Record<string, any>;
      const parsed = typeof currentSettings === 'object' && currentSettings !== null && !Array.isArray(currentSettings)
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        ? currentSettings as Record<string, any>
        : {};
      setSettings({ ...defaults, ...parsed });

      // Fetch performance history
      setLoadingStats(true);
      fetchModuleStats(module.name).then((data) => {
        setStats(data);
        setLoadingStats(false);
      });
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [module, open]);

  const handleSave = async () => {
    if (!module) return;
    setSaving(true);
    await updateModuleSettings(module.name, settings as Json);
    setSaving(false);
    onOpenChange(false);
  };

  const handleReset = async () => {
    if (!module) return;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const defaults = getDefaultSettings(module.name) as Record<string, any>;
    setSettings(defaults);
    await resetModuleSettings(module.name);
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const updateSetting = (key: string, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const renderSettingInput = (key: string, value: any) => {
    if (typeof value === 'boolean') {
      return (
        <div key={key} className="flex items-center justify-between py-2">
          <Label htmlFor={key} className="text-sm capitalize">
            {key.replace(/_/g, ' ')}
          </Label>
          <Switch
            id={key}
            checked={value}
            onCheckedChange={(checked) => updateSetting(key, checked)}
          />
        </div>
      );
    }

    if (typeof value === 'number') {
      return (
        <div key={key} className="space-y-2">
          <Label htmlFor={key} className="text-sm capitalize">
            {key.replace(/_/g, ' ')}
          </Label>
          <Input
            id={key}
            type="number"
            value={value}
            onChange={(e) => updateSetting(key, parseFloat(e.target.value) || 0)}
            className="bg-background"
          />
        </div>
      );
    }

    if (typeof value === 'string') {
      // Check if it's a select-like value
      const selectOptions: Record<string, string[]> = {
        precision: ['INT8', 'FP16', 'FP32', 'BF16'],
        compression_algo: ['lz4', 'zstd', 'snappy', 'gzip'],
        eviction_policy: ['lru', 'lfu', 'fifo', 'arc'],
        stream_priority: ['low', 'normal', 'high'],
        sync_mode: ['sync', 'async'],
        communication_backend: ['nccl', 'gloo', 'mpi'],
        target_device: ['cuda', 'cpu', 'tensorrt'],
        min_precision: ['FP16', 'FP32', 'BF16'],
        max_precision: ['FP16', 'FP32', 'BF16'],
        pruning_method: ['magnitude', 'structured', 'unstructured', 'lottery']
      };

      if (selectOptions[key]) {
        return (
          <div key={key} className="space-y-2">
            <Label htmlFor={key} className="text-sm capitalize">
              {key.replace(/_/g, ' ')}
            </Label>
            <Select value={value} onValueChange={(v) => updateSetting(key, v)}>
              <SelectTrigger className="bg-background">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {selectOptions[key].map((opt) => (
                  <SelectItem key={opt} value={opt}>{opt}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        );
      }

      return (
        <div key={key} className="space-y-2">
          <Label htmlFor={key} className="text-sm capitalize">
            {key.replace(/_/g, ' ')}
          </Label>
          <Input
            id={key}
            type="text"
            value={value}
            onChange={(e) => updateSetting(key, e.target.value)}
            className="bg-background"
          />
        </div>
      );
    }

    return null;
  };

  if (!module) return null;

  const chartData = stats?.performanceHistory.slice(0, 20).reverse().map((item, idx) => ({
    index: idx,
    speedup: item.speedup,
    date: new Date(item.recorded_at).toLocaleDateString()
  })) || [];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Configure {module.name}
          </DialogTitle>
          <DialogDescription>
            {module.description}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Settings Form */}
          <div className="space-y-4">
            <h4 className="text-sm font-semibold text-foreground">Settings</h4>
            <div className="grid gap-4 sm:grid-cols-2">
              {Object.entries(settings).map(([key, value]) => renderSettingInput(key, value))}
            </div>
          </div>

          <Separator />

          {/* Performance History Chart */}
          <div className="space-y-4">
            <h4 className="text-sm font-semibold text-foreground flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Performance History
            </h4>
            {loadingStats ? (
              <div className="h-32 flex items-center justify-center text-muted-foreground">
                Loading performance data...
              </div>
            ) : chartData.length > 0 ? (
              <ChartContainer
                config={{
                  speedup: {
                    label: 'Speedup',
                    color: 'hsl(var(--primary))'
                  }
                }}
                className="h-32"
              >
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
                    <XAxis dataKey="date" hide />
                    <YAxis hide domain={['auto', 'auto']} />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <Line
                      type="monotone"
                      dataKey="speedup"
                      stroke="hsl(var(--primary))"
                      strokeWidth={2}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </ChartContainer>
            ) : (
              <div className="h-32 flex items-center justify-center text-muted-foreground bg-muted/50 rounded-lg">
                No performance data yet
              </div>
            )}
          </div>
        </div>

        <DialogFooter className="flex gap-2 sm:gap-0">
          <Button
            variant="outline"
            onClick={handleReset}
            className="flex-1 sm:flex-none"
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            Reset to Defaults
          </Button>
          <Button
            onClick={handleSave}
            disabled={saving}
            className="flex-1 sm:flex-none"
          >
            <Save className="h-4 w-4 mr-2" />
            {saving ? 'Saving...' : 'Save Settings'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
