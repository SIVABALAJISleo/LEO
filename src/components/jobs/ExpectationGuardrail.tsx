// ExpectationGuardrail - Shows notices before heavy/fresh/private requests
// Prevents over-expectation without discouraging users

import { useState } from 'react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { Badge } from '@/components/ui/badge';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Clock, Zap, Sparkles, Server } from 'lucide-react';
import { cn } from '@/lib/utils';

export type RequestCharacteristic = 'fresh' | 'private' | 'heavy' | 'cached';

export interface QualityOption {
  id: string;
  label: string;
  description: string;
  estimatedTime: string;
  confidence: string;
  icon: React.ReactNode;
}

export interface ExpectationGuardrailProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  characteristics: RequestCharacteristic[];
  jobType: string;
  estimatedTime?: string;
  options?: QualityOption[];
  onProceed: (selectedOption?: string) => void;
  onCancel: () => void;
}

const CHARACTERISTIC_LABELS: Record<RequestCharacteristic, { label: string; description: string }> = {
  fresh: {
    label: 'New Request',
    description: 'This request needs fresh computation',
  },
  private: {
    label: 'Private Data',
    description: 'Processing your unique input',
  },
  heavy: {
    label: 'Complex Task',
    description: 'This task requires more processing time',
  },
  cached: {
    label: 'Optimized',
    description: 'Similar requests help speed this up',
  },
};

const DEFAULT_OPTIONS: QualityOption[] = [
  {
    id: 'quick',
    label: 'Quick Preview',
    description: 'Get an instant approximate result',
    estimatedTime: 'Instant',
    confidence: '~70%',
    icon: <Zap className="h-4 w-4 text-amber-500" />,
  },
  {
    id: 'balanced',
    label: 'Balanced',
    description: 'Faster result with good accuracy',
    estimatedTime: '~30 seconds',
    confidence: '~85%',
    icon: <Sparkles className="h-4 w-4 text-blue-500" />,
  },
  {
    id: 'full',
    label: 'Full Quality',
    description: 'Complete processing for best results',
    estimatedTime: '2-5 minutes',
    confidence: '~95%',
    icon: <Server className="h-4 w-4 text-green-500" />,
  },
];

export function ExpectationGuardrail({
  open,
  onOpenChange,
  characteristics,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  jobType,
  estimatedTime,
  options = DEFAULT_OPTIONS,
  onProceed,
  onCancel,
}: ExpectationGuardrailProps) {
  const [selectedOption, setSelectedOption] = useState<string>('full');

  const showOptions = characteristics.includes('heavy') || characteristics.includes('fresh');
  const isCached = characteristics.includes('cached');

  const handleProceed = () => {
    onProceed(showOptions ? selectedOption : undefined);
    onOpenChange(false);
  };

  const handleCancel = () => {
    onCancel();
    onOpenChange(false);
  };

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent className="max-w-md">
        <AlertDialogHeader>
          <AlertDialogTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5 text-primary" />
            {isCached ? 'Ready to Process' : 'Processing Time Notice'}
          </AlertDialogTitle>
          <AlertDialogDescription asChild>
            <div className="space-y-4">
              {/* Characteristics badges */}
              <div className="flex flex-wrap gap-2">
                {characteristics.map((char) => (
                  <Badge
                    key={char}
                    variant="secondary"
                    className={cn(
                      'text-xs',
                      char === 'cached' && 'bg-green-500/10 text-green-600 border-green-500/30',
                      char === 'fresh' && 'bg-amber-500/10 text-amber-600 border-amber-500/30',
                      char === 'heavy' && 'bg-red-500/10 text-red-600 border-red-500/30',
                      char === 'private' && 'bg-purple-500/10 text-purple-600 border-purple-500/30'
                    )}
                  >
                    {CHARACTERISTIC_LABELS[char].label}
                  </Badge>
                ))}
              </div>

              {/* Description */}
              <p className="text-sm text-foreground">
                {isCached
                  ? 'Your request will be processed quickly using optimized resources.'
                  : 'This request needs fresh computation. Please choose how you\'d like to proceed:'}
              </p>

              {/* Time estimate */}
              {estimatedTime && !isCached && (
                <div className="flex items-center gap-2 text-sm bg-muted/50 rounded-lg px-3 py-2">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span>Estimated time: <strong>{estimatedTime}</strong></span>
                </div>
              )}

              {/* Quality options */}
              {showOptions && (
                <RadioGroup
                  value={selectedOption}
                  onValueChange={setSelectedOption}
                  className="space-y-3"
                >
                  {options.map((option) => (
                    <div
                      key={option.id}
                      className={cn(
                        'flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors',
                        selectedOption === option.id
                          ? 'border-primary bg-primary/5'
                          : 'border-border hover:bg-muted/50'
                      )}
                      onClick={() => setSelectedOption(option.id)}
                    >
                      <RadioGroupItem value={option.id} id={option.id} className="mt-1" />
                      <div className="flex-1">
                        <Label
                          htmlFor={option.id}
                          className="flex items-center gap-2 cursor-pointer font-medium"
                        >
                          {option.icon}
                          {option.label}
                        </Label>
                        <p className="text-xs text-muted-foreground mt-1">
                          {option.description}
                        </p>
                        <div className="flex gap-3 mt-2 text-xs text-muted-foreground">
                          <span>⏱ {option.estimatedTime}</span>
                          <span>📊 {option.confidence} accuracy</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </RadioGroup>
              )}
            </div>
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel onClick={handleCancel}>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={handleProceed}>
            {isCached ? 'Process' : 'Continue'}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
