import { useState } from 'react';
import { z } from 'zod';
import { Plus, Loader2 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Slider } from '@/components/ui/slider';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Model, CreateJobInput } from '@/hooks/useJobsData';
import { MODULE_NAMES } from '@/hooks/useModulesData';
import { useToast } from '@/hooks/use-toast';

const jobSchema = z.object({
  model_id: z.string().min(1, 'Please select a model'),
  priority: z.number().min(1).max(10),
  input_text: z.string().max(10000, 'Input text must be less than 10000 characters'),
  batch_size: z.number().min(1).max(128),
  max_tokens: z.number().min(1).max(4096),
});

interface JobCreateFormProps {
  models: Model[];
  onSubmit: (input: CreateJobInput) => Promise<string | null>;
}

export function JobCreateForm({ models, onSubmit }: JobCreateFormProps) {
  const { toast } = useToast();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  
  const [modelId, setModelId] = useState('');
  const [priority, setPriority] = useState(5);
  const [inputText, setInputText] = useState('');
  const [batchSize, setBatchSize] = useState(1);
  const [maxTokens, setMaxTokens] = useState(256);
  const [selectedModules, setSelectedModules] = useState<string[]>([]);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const resetForm = () => {
    setModelId('');
    setPriority(5);
    setInputText('');
    setBatchSize(1);
    setMaxTokens(256);
    setSelectedModules([]);
    setErrors({});
  };

  const toggleModule = (module: string) => {
    setSelectedModules(prev =>
      prev.includes(module)
        ? prev.filter(m => m !== module)
        : [...prev, module]
    );
  };

  const handleSubmit = async () => {
    // Validate
    const result = jobSchema.safeParse({
      model_id: modelId,
      priority,
      input_text: inputText,
      batch_size: batchSize,
      max_tokens: maxTokens
    });

    if (!result.success) {
      const fieldErrors: Record<string, string> = {};
      result.error.errors.forEach(err => {
        if (err.path[0]) {
          fieldErrors[err.path[0].toString()] = err.message;
        }
      });
      setErrors(fieldErrors);
      return;
    }

    setErrors({});
    setLoading(true);

    const jobInput: CreateJobInput = {
      model_id: modelId,
      priority,
      input_data: {
        text: inputText.trim(),
        batch_size: batchSize,
        max_tokens: maxTokens
      },
      enabled_modules: selectedModules,
      optimization_options: {
        use_cache: true,
        precision: 'FP16'
      }
    };

    const jobId = await onSubmit(jobInput);
    setLoading(false);

    if (jobId) {
      resetForm();
      setOpen(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          New Job
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[90vh]">
        <DialogHeader>
          <DialogTitle>Create Inference Job</DialogTitle>
          <DialogDescription>
            Configure and submit a new GPU inference job.
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="max-h-[60vh] pr-4">
          <div className="space-y-6 py-4">
            {/* Model Selection */}
            <div className="space-y-2">
              <Label htmlFor="model">Model *</Label>
              <Select value={modelId} onValueChange={setModelId}>
                <SelectTrigger className={errors.model_id ? 'border-red-500' : ''}>
                  <SelectValue placeholder="Select a model" />
                </SelectTrigger>
                <SelectContent>
                  {models.length === 0 ? (
                    <SelectItem value="none" disabled>No models available</SelectItem>
                  ) : (
                    models.map(model => (
                      <SelectItem key={model.id} value={model.id}>
                        {model.name} ({model.model_type})
                      </SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
              {errors.model_id && (
                <p className="text-xs text-red-500">{errors.model_id}</p>
              )}
            </div>

            {/* Priority */}
            <div className="space-y-3">
              <div className="flex justify-between">
                <Label>Priority</Label>
                <span className="text-sm text-muted-foreground">
                  {priority <= 3 ? 'High' : priority <= 6 ? 'Normal' : 'Low'} ({priority})
                </span>
              </div>
              <Slider
                value={[priority]}
                onValueChange={([v]) => setPriority(v)}
                min={1}
                max={10}
                step={1}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>High Priority</span>
                <span>Low Priority</span>
              </div>
            </div>

            {/* Input Text */}
            <div className="space-y-2">
              <Label htmlFor="input">Input Text</Label>
              <Textarea
                id="input"
                placeholder="Enter input text for inference..."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                className={`min-h-[100px] ${errors.input_text ? 'border-red-500' : ''}`}
              />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>{inputText.length} / 10,000 characters</span>
                {errors.input_text && (
                  <span className="text-red-500">{errors.input_text}</span>
                )}
              </div>
            </div>

            {/* Batch Size & Max Tokens */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="batch_size">Batch Size</Label>
                <Input
                  id="batch_size"
                  type="number"
                  min={1}
                  max={128}
                  value={batchSize}
                  onChange={(e) => setBatchSize(parseInt(e.target.value) || 1)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="max_tokens">Max Tokens</Label>
                <Input
                  id="max_tokens"
                  type="number"
                  min={1}
                  max={4096}
                  value={maxTokens}
                  onChange={(e) => setMaxTokens(parseInt(e.target.value) || 256)}
                />
              </div>
            </div>

            {/* Optimization Modules */}
            <div className="space-y-3">
              <Label>Optimization Modules</Label>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                {MODULE_NAMES.map(module => (
                  <div
                    key={module}
                    className="flex items-center space-x-2 p-2 rounded border border-border hover:bg-muted/50 cursor-pointer"
                    onClick={() => toggleModule(module)}
                  >
                    <Checkbox
                      id={module}
                      checked={selectedModules.includes(module)}
                      onCheckedChange={() => toggleModule(module)}
                    />
                    <label
                      htmlFor={module}
                      className="text-xs cursor-pointer flex-1 truncate"
                    >
                      {module}
                    </label>
                  </div>
                ))}
              </div>
              <p className="text-xs text-muted-foreground">
                {selectedModules.length} modules selected
              </p>
            </div>
          </div>
        </ScrollArea>

        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Creating...
              </>
            ) : (
              'Create Job'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
