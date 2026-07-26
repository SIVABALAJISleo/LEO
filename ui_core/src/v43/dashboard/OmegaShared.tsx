import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Alert, AlertTitle, AlertDescription } from "../../../components/ui/alert";

export const MetricCard = ({ label, value, comparison, status }: any) => (
  <div className="p-4 rounded-lg bg-slate-900 border border-slate-800 flex flex-col justify-between">
    <div>
      <h3 className="text-sm font-semibold text-slate-400">{label}</h3>
      <p className="text-2xl font-bold text-white mt-1">{value}</p>
    </div>
    <div className="mt-4 flex items-center justify-between">
      <span className="text-xs text-slate-500 truncate mr-2" title={comparison}>
        {comparison}
      </span>
      <span className="text-xs font-bold px-2 py-1 rounded bg-slate-800 text-green-400">
        {status}
      </span>
    </div>
  </div>
);

export const StatCard = ({ label, value }: any) => (
  <div className="p-4 rounded-lg bg-slate-900 border border-slate-800">
    <h3 className="text-sm font-semibold text-slate-400">{label}</h3>
    <p className="text-xl font-bold text-white mt-1">{value}</p>
  </div>
);
