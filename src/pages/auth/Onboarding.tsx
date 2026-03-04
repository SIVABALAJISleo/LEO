import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { firebaseClient as supabase } from '@/integrations/firebase/client';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { useToast } from '@/hooks/use-toast';
import { Cpu, User, Settings, Palette, ChevronRight, ChevronLeft, Loader2 } from 'lucide-react';

type Step = 'profile' | 'modules' | 'theme';

const MODULES = [
  { name: 'kernel_fusion', label: 'Kernel Fusion', description: 'Combine multiple GPU kernels for reduced overhead' },
  { name: 'memory_optimization', label: 'Memory Optimization', description: 'Intelligent memory management and caching' },
  { name: 'tensor_compression', label: 'Tensor Compression', description: 'Reduce model size while maintaining accuracy' },
  { name: 'batch_scheduling', label: 'Batch Scheduling', description: 'Optimize batch processing for throughput' },
  { name: 'precision_scaling', label: 'Precision Scaling', description: 'Dynamic precision for performance gains' },
];

const THEMES = [
  { id: 'dark', label: 'Dark Mode', description: 'Default dark theme with neon green accents' },
  { id: 'light', label: 'Light Mode', description: 'Clean light theme for bright environments' },
  { id: 'system', label: 'System', description: 'Automatically match your system preference' },
];

const Onboarding = () => {
  const [step, setStep] = useState<Step>('profile');
  const [loading, setLoading] = useState(false);
  
  // Profile data
  const [fullName, setFullName] = useState('');
  const [company, setCompany] = useState('');
  
  // Module preferences
  const [enabledModules, setEnabledModules] = useState<string[]>(['kernel_fusion', 'memory_optimization']);
  
  // Theme preference
  const [selectedTheme, setSelectedTheme] = useState('dark');
  
  const navigate = useNavigate();
  const { user } = useAuth();
  const { toast } = useToast();

  const steps: Step[] = ['profile', 'modules', 'theme'];
  const currentStepIndex = steps.indexOf(step);
  const progress = ((currentStepIndex + 1) / steps.length) * 100;

  const toggleModule = (moduleName: string) => {
    setEnabledModules(prev => 
      prev.includes(moduleName)
        ? prev.filter(m => m !== moduleName)
        : [...prev, moduleName]
    );
  };

  const handleNext = () => {
    const nextIndex = currentStepIndex + 1;
    if (nextIndex < steps.length) {
      setStep(steps[nextIndex]);
    }
  };

  const handleBack = () => {
    const prevIndex = currentStepIndex - 1;
    if (prevIndex >= 0) {
      setStep(steps[prevIndex]);
    }
  };

  const handleComplete = async () => {
    if (!user) {
      toast({
        title: 'Error',
        description: 'Please sign in to complete onboarding.',
        variant: 'destructive',
      });
      navigate('/auth/login');
      return;
    }

    setLoading(true);

    try {
      // Update profile
      const { error: profileError } = await supabase
        .from('profiles')
        .update({
          full_name: fullName,
          company: company,
        })
        .eq('user_id', user.id);

      if (profileError) throw profileError;

      // Create module configs
      const moduleConfigs = MODULES.map(module => ({
        user_id: user.id,
        module_name: module.name,
        module_type: 'optimization',
        enabled: enabledModules.includes(module.name),
        config: {},
        settings: {},
      }));

      const { error: modulesError } = await supabase
        .from('module_configs')
        .upsert(moduleConfigs, { 
          onConflict: 'user_id,module_name',
          ignoreDuplicates: false 
        });

      if (modulesError) throw modulesError;

      // Save theme preference (could be stored in localStorage or user metadata)
      localStorage.setItem('theme-preference', selectedTheme);

      toast({
        title: 'Setup Complete!',
        description: 'Your preferences have been saved. Welcome to HYPER!',
      });

      navigate('/dashboard/home');
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error: unknown) {
      toast({
        title: 'Error',
        description: 'Failed to save preferences. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const renderStepContent = () => {
    switch (step) {
      case 'profile':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-center w-16 h-16 rounded-full bg-primary/20 mx-auto mb-4">
              <User className="h-8 w-8 text-primary" />
            </div>
            <div className="text-center mb-6">
              <h3 className="text-xl font-semibold">Complete Your Profile</h3>
              <p className="text-muted-foreground text-sm mt-1">
                Tell us a bit about yourself
              </p>
            </div>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="fullName">Full Name</Label>
                <Input
                  id="fullName"
                  placeholder="John Doe"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="company">Company (Optional)</Label>
                <Input
                  id="company"
                  placeholder="Acme Corp"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                />
              </div>
            </div>
          </div>
        );

      case 'modules':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-center w-16 h-16 rounded-full bg-primary/20 mx-auto mb-4">
              <Settings className="h-8 w-8 text-primary" />
            </div>
            <div className="text-center mb-6">
              <h3 className="text-xl font-semibold">Enable Optimization Modules</h3>
              <p className="text-muted-foreground text-sm mt-1">
                Choose which modules to enable by default
              </p>
            </div>
            <div className="space-y-3">
              {MODULES.map((module) => (
                <div
                  key={module.name}
                  className={`p-4 rounded-lg border cursor-pointer transition-all ${
                    enabledModules.includes(module.name)
                      ? 'border-primary bg-primary/10'
                      : 'border-border hover:border-primary/50'
                  }`}
                  onClick={() => toggleModule(module.name)}
                >
                  <div className="flex items-start gap-3">
                    <Checkbox
                      checked={enabledModules.includes(module.name)}
                      onCheckedChange={() => toggleModule(module.name)}
                      className="mt-1"
                    />
                    <div>
                      <p className="font-medium">{module.label}</p>
                      <p className="text-sm text-muted-foreground">{module.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );

      case 'theme':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-center w-16 h-16 rounded-full bg-primary/20 mx-auto mb-4">
              <Palette className="h-8 w-8 text-primary" />
            </div>
            <div className="text-center mb-6">
              <h3 className="text-xl font-semibold">Choose Your Theme</h3>
              <p className="text-muted-foreground text-sm mt-1">
                Select your preferred appearance
              </p>
            </div>
            <div className="space-y-3">
              {THEMES.map((theme) => (
                <div
                  key={theme.id}
                  className={`p-4 rounded-lg border cursor-pointer transition-all ${
                    selectedTheme === theme.id
                      ? 'border-primary bg-primary/10'
                      : 'border-border hover:border-primary/50'
                  }`}
                  onClick={() => setSelectedTheme(theme.id)}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-4 h-4 rounded-full border-2 ${
                      selectedTheme === theme.id
                        ? 'border-primary bg-primary'
                        : 'border-muted-foreground'
                    }`} />
                    <div>
                      <p className="font-medium">{theme.label}</p>
                      <p className="text-sm text-muted-foreground">{theme.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-gradient-glow" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,hsl(88_72%_50%/0.1),transparent_50%)]" />

      <Card className="relative w-full max-w-lg p-8 bg-card border-border shadow-card">
        {/* Logo */}
        <div className="flex items-center justify-center space-x-2 mb-6">
          <Cpu className="h-8 w-8 text-primary" />
          <span className="text-2xl font-display font-bold">
            HYPER
          </span>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-muted-foreground mb-2">
            <span>Step {currentStepIndex + 1} of {steps.length}</span>
            <span>{Math.round(progress)}% complete</span>
          </div>
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-primary transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Step Content */}
        {renderStepContent()}

        {/* Navigation Buttons */}
        <div className="flex justify-between mt-8 pt-6 border-t border-border">
          <Button
            variant="outline"
            onClick={handleBack}
            disabled={currentStepIndex === 0}
            className="gap-2"
          >
            <ChevronLeft className="h-4 w-4" />
            Back
          </Button>
          
          {currentStepIndex < steps.length - 1 ? (
            <Button
              onClick={handleNext}
              className="bg-gradient-primary shadow-glow gap-2"
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </Button>
          ) : (
            <Button
              onClick={handleComplete}
              disabled={loading}
              className="bg-gradient-primary shadow-glow gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  Complete Setup
                  <ChevronRight className="h-4 w-4" />
                </>
              )}
            </Button>
          )}
        </div>
      </Card>
    </div>
  );
};

export default Onboarding;
