import React from "react";
import { Link } from "react-router-dom";
import { AlertCircle } from "lucide-react";

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#040814] px-6 relative overflow-hidden">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-rose-500/5 rounded-full blur-[120px] pointer-events-none" />

      <div className="text-center space-y-6 max-w-md relative z-10">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-500 animate-bounce">
          <AlertCircle className="h-8 w-8" />
        </div>

        <h1 className="text-6xl font-black text-white leading-none">404</h1>

        <div className="space-y-2">
          <h2 className="text-xl font-bold text-slate-100 uppercase tracking-wide">
            Substrate Lost
          </h2>
          <p className="text-slate-400 text-xs leading-relaxed">
            The target neural path or page substrate you are trying to lookup does not exist or has
            been garbage collected.
          </p>
        </div>

        <div className="pt-4">
          <Link
            to="/"
            className="inline-flex items-center gap-2 bg-[#76B900] hover:bg-[#8CD000] text-black font-extrabold text-xs px-6 py-3.5 rounded uppercase tracking-wider transition-all transform active:scale-95 shadow-[0_0_15px_rgba(118,185,0,0.3)]"
          >
            Back to Cockpit
          </Link>
        </div>
      </div>
    </div>
  );
}
