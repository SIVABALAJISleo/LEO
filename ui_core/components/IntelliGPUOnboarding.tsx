import React, { useState } from "react";
import { Cpu, User, Settings, CheckCircle2, Palette } from "lucide-react";
import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";

interface IntelliGPUOnboardingProps {
  onNavigate: (
    view: "home" | "docs" | "playground" | "pricing" | "swarms" | "auth" | "onboarding",
  ) => void;
  onComplete: () => void;
}

export const IntelliGPUOnboarding: React.FC<IntelliGPUOnboardingProps> = ({
  onNavigate,
  onComplete,
}) => {
  const [step, setStep] = useState(1);
  const [fullName, setFullName] = useState("SIVA");
  const [company, setCompany] = useState("Acme Corp");
  const [selectedTheme, setSelectedTheme] = useState("dark");
  const [enabledModules, setEnabledModules] = useState<Record<string, boolean>>({
    fusion: false,
    memory: false,
    tensor: false,
    batch: false,
    precision: false,
  });

  const toggleModule = (mod: string) => {
    setEnabledModules((prev) => ({
      ...prev,
      [mod]: !prev[mod],
    }));
  };

  const handleNext = () => {
    if (step < 3) {
      setStep(step + 1);
    } else {
      onComplete();
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    } else {
      onNavigate("auth");
    }
  };

  const progressPct = step === 1 ? 33 : step === 2 ? 67 : 100;

  return (
    <div className="bg-[#020813] text-slate-100 min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-[#76B900]/5 rounded-full blur-[100px] pointer-events-none" />

      <Card className="w-full max-w-md bg-[#0b1329]/80 border border-slate-800/80 backdrop-blur-md shadow-2xl relative z-10">
        <CardContent className="p-8">
          {/* Header Branding */}
          <div className="flex items-center justify-center gap-2 mb-6">
            <Cpu className="h-6 w-6 text-[#76B900]" />
            <span className="text-lg font-black tracking-tight text-white font-display">
              IntelliGPU
            </span>
          </div>

          {/* Progress Section */}
          <div className="mb-8">
            <div className="flex justify-between text-[11px] font-bold text-slate-400 uppercase mb-2">
              <span>Step {step} of 3</span>
              <span className="text-[#76B900]">{progressPct}% complete</span>
            </div>
            <div className="w-full bg-[#131d35] h-1.5 rounded-full overflow-hidden">
              <div
                className="bg-[#76B900] h-full transition-all duration-300 rounded-full"
                style={{ width: `${progressPct}%` }}
              />
            </div>
          </div>

          {/* Step 1: Complete Profile */}
          {step === 1 && (
            <div className="space-y-6">
              <div className="flex flex-col items-center">
                <div className="bg-[#76B900]/10 border border-[#76B900]/30 p-4 rounded-full mb-4 shadow-[0_0_15px_rgba(118,185,0,0.1)]">
                  <User className="h-8 w-8 text-[#76B900]" />
                </div>
                <h2 className="text-xl font-black text-white tracking-tight">
                  Complete Your Profile
                </h2>
                <p className="text-slate-400 text-xs mt-1 text-center">
                  Tell us a bit about yourself
                </p>
              </div>

              <div className="space-y-4">
                <div>
                  <label
                    htmlFor="fullName"
                    className="block text-slate-300 font-bold text-xs uppercase mb-2"
                  >
                    Full Name
                  </label>
                  <input
                    id="fullName"
                    type="text"
                    required
                    placeholder="John Doe"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full px-4 py-3 bg-[#020813] border border-slate-800 rounded focus:outline-none focus:ring-1 focus:ring-[#76B900] text-xs font-medium placeholder-slate-600 text-slate-100"
                  />
                </div>

                <div>
                  <label
                    htmlFor="company"
                    className="block text-slate-300 font-bold text-xs uppercase mb-2"
                  >
                    Company (Optional)
                  </label>
                  <input
                    id="company"
                    type="text"
                    placeholder="Acme Corp"
                    value={company}
                    onChange={(e) => setCompany(e.target.value)}
                    className="w-full px-4 py-3 bg-[#020813] border border-slate-800 rounded focus:outline-none focus:ring-1 focus:ring-[#76B900] text-xs font-medium placeholder-slate-600 text-slate-100"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Step 2: Enable Modules */}
          {step === 2 && (
            <div className="space-y-6">
              <div className="flex flex-col items-center">
                <div className="bg-[#76B900]/10 border border-[#76B900]/30 p-4 rounded-full mb-4 shadow-[0_0_15px_rgba(118,185,0,0.1)]">
                  <Settings className="h-8 w-8 text-[#76B900]" />
                </div>
                <h2 className="text-xl font-black text-white tracking-tight">
                  Enable Optimization Modules
                </h2>
                <p className="text-slate-400 text-xs mt-1 text-center">
                  Choose which modules to enable by default
                </p>
              </div>

              <div className="space-y-3">
                {[
                  {
                    id: "fusion",
                    label: "Kernel Fusion",
                    desc: "Combine multiple GPU kernels for reduced overhead",
                  },
                  {
                    id: "memory",
                    label: "Memory Optimization",
                    desc: "Intelligent memory management and caching",
                  },
                  {
                    id: "tensor",
                    label: "Tensor Compression",
                    desc: "Reduce model size while maintaining accuracy",
                  },
                  {
                    id: "batch",
                    label: "Batch Scheduling",
                    desc: "Optimize batch processing for throughput",
                  },
                  {
                    id: "precision",
                    label: "Precision Scaling",
                    desc: "Dynamic precision for performance gains",
                  },
                ].map((mod) => (
                  <button
                    key={mod.id}
                    onClick={() => toggleModule(mod.id)}
                    className={`w-full p-4 rounded border text-left flex items-start transition-all ${
                      enabledModules[mod.id]
                        ? "bg-[#76B900]/5 border-[#76B900]"
                        : "bg-[#020813] border-slate-800/80 hover:border-slate-700"
                    }`}
                  >
                    <div className="mr-3 mt-0.5">
                      <div
                        className={`h-4.5 w-4.5 rounded-full border flex items-center justify-center transition-all ${
                          enabledModules[mod.id]
                            ? "border-[#76B900] bg-[#76B900]"
                            : "border-slate-700 bg-transparent"
                        }`}
                      >
                        {enabledModules[mod.id] && (
                          <CheckCircle2 className="h-3 w-3 text-black stroke-[3px]" />
                        )}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs font-bold text-slate-100">{mod.label}</div>
                      <div className="text-[10px] text-slate-400 mt-0.5">{mod.desc}</div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Step 3: Choose Your Theme */}
          {step === 3 && (
            <div className="space-y-6">
              <div className="flex flex-col items-center">
                <div className="bg-[#76B900]/10 border border-[#76B900]/30 p-4 rounded-full mb-4 shadow-[0_0_15px_rgba(118,185,0,0.1)]">
                  <Palette className="h-8 w-8 text-[#76B900]" />
                </div>
                <h2 className="text-xl font-black text-white tracking-tight">Choose Your Theme</h2>
                <p className="text-slate-400 text-xs mt-1 text-center font-medium">
                  Select your preferred appearance
                </p>
              </div>

              <div className="space-y-3">
                {[
                  {
                    id: "dark",
                    label: "Dark Mode",
                    desc: "Default dark theme with NVIDIA green accents",
                  },
                  {
                    id: "light",
                    label: "Light Mode",
                    desc: "Clean light theme for bright environments",
                  },
                  {
                    id: "system",
                    label: "System",
                    desc: "Automatically match your system preference",
                  },
                ].map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setSelectedTheme(t.id)}
                    className={`w-full p-4 rounded border text-left flex items-start transition-all ${
                      selectedTheme === t.id
                        ? "bg-[#76B900]/5 border-[#76B900]"
                        : "bg-[#020813] border-slate-800/80 hover:border-slate-700"
                    }`}
                  >
                    <div className="mr-3 mt-0.5">
                      <div
                        className={`h-4.5 w-4.5 rounded-full border flex items-center justify-center transition-all ${
                          selectedTheme === t.id ? "border-[#76B900]" : "border-slate-700"
                        }`}
                      >
                        {selectedTheme === t.id && (
                          <div className="h-2 w-2 rounded-full bg-[#76B900]" />
                        )}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs font-bold text-slate-100">{t.label}</div>
                      <div className="text-[10px] text-slate-400 mt-0.5">{t.desc}</div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-4 mt-8">
            <Button
              onClick={handleBack}
              className="flex-1 py-6 text-xs font-bold bg-[#131d35] hover:bg-[#1a2644] text-slate-200 border border-slate-700/60 rounded"
            >
              Back
            </Button>
            <Button
              onClick={handleNext}
              className="flex-1 py-6 text-xs font-extrabold bg-[#76B900] hover:bg-[#659e00] text-black rounded transition-all shadow-[0_0_15px_rgba(118,185,0,0.2)]"
            >
              {step === 3 ? "Complete Setup >" : "Next"}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
