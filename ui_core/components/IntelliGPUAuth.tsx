import React, { useState } from "react";
import { Cpu } from "lucide-react";
import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";

interface IntelliGPUAuthProps {
  onNavigate: (
    view: "home" | "docs" | "playground" | "pricing" | "swarms" | "auth" | "onboarding",
  ) => void;
  onSuccess: () => void;
}

export const IntelliGPUAuth: React.FC<IntelliGPUAuthProps> = ({ onNavigate, onSuccess }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSuccess();
  };

  return (
    <div className="bg-[#020813] text-slate-100 min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-[#76B900]/5 rounded-full blur-[100px] pointer-events-none" />

      <Card className="w-full max-w-md bg-[#0b1329]/80 border border-slate-800/80 backdrop-blur-md shadow-2xl relative z-10">
        <CardContent className="p-8 flex flex-col items-center">
          {/* Logo */}
          <div className="flex items-center gap-2 mb-6">
            <Cpu className="h-6 w-6 text-[#76B900]" />
            <span className="text-lg font-black tracking-tight text-white font-display">
              IntelliGPU
            </span>
          </div>

          <h2 className="text-2xl font-black text-white mb-1 tracking-tight text-center">
            Welcome Back
          </h2>
          <p className="text-slate-400 text-xs text-center mb-8">
            Sign in to access your GPU optimization dashboard
          </p>

          <form onSubmit={handleSubmit} className="w-full space-y-5">
            <div>
              <label
                htmlFor="email"
                className="block text-slate-300 font-bold text-xs uppercase mb-2"
              >
                Email
              </label>
              <input
                id="email"
                type="email"
                required
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 bg-[#020813] border border-slate-800 rounded focus:outline-none focus:ring-1 focus:ring-[#76B900] text-xs font-medium placeholder-slate-600 text-slate-100"
              />
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-slate-300 font-bold text-xs uppercase mb-2"
              >
                Password
              </label>
              <input
                id="password"
                type="password"
                required
                placeholder="........"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 bg-[#020813] border border-slate-800 rounded focus:outline-none focus:ring-1 focus:ring-[#76B900] text-xs font-medium placeholder-slate-600 text-slate-100"
              />
            </div>

            <div className="flex items-center justify-between text-xs">
              <label className="flex items-center text-slate-400 cursor-pointer">
                <input
                  type="checkbox"
                  className="mr-2 rounded border-slate-800 bg-[#020813] text-[#76B900] focus:ring-0 focus:ring-offset-0"
                />
                Remember me
              </label>
              <a href="#forgot" className="text-[#76B900] hover:underline font-semibold">
                Forgot password?
              </a>
            </div>

            <Button
              type="submit"
              className="w-full py-6 bg-[#76B900] hover:bg-[#659e00] text-black font-extrabold text-xs rounded transition-all shadow-[0_0_15px_rgba(118,185,0,0.2)]"
            >
              Sign In
            </Button>
          </form>

          <div className="text-xs text-slate-400 mt-6 text-center">
            Don't have an account?{" "}
            <button
              onClick={() => onNavigate("onboarding")}
              className="text-[#76B900] hover:underline font-bold"
            >
              Sign up
            </button>
          </div>

          <button
            onClick={() => onNavigate("home")}
            className="text-xs text-slate-500 hover:text-slate-300 mt-8 transition-colors"
          >
            ← Back to home
          </button>
        </CardContent>
      </Card>
    </div>
  );
};
