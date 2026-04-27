import React from 'react';
import { Handle, Position } from 'reactflow';
import { Database, Filter, Sigma, LayoutTemplate } from 'lucide-react';

export const DatasetNode = ({ data }: any) => (
  <div className="bg-slate-900 border-2 border-blue-500 p-4 rounded-lg shadow-xl text-white min-w-[150px]">
    <div className="flex items-center gap-2 mb-2 border-b border-slate-700 pb-2">
      <Database size={16} className="text-blue-400" />
      <span className="font-bold text-xs uppercase tracking-wider">Dataset</span>
    </div>
    <div className="text-sm font-semibold">{data.value || 'Select...'}</div>
    <Handle type="source" position={Position.Bottom} className="w-3 h-3 bg-blue-500" />
  </div>
);

export const FilterNode = ({ data }: any) => (
  <div className="bg-slate-900 border-2 border-amber-500 p-4 rounded-lg shadow-xl text-white min-w-[150px]">
    <Handle type="target" position={Position.Top} className="w-3 h-3 bg-amber-500" />
    <div className="flex items-center gap-2 mb-2 border-b border-slate-700 pb-2">
      <Filter size={16} className="text-amber-400" />
      <span className="font-bold text-xs uppercase tracking-wider">Filter</span>
    </div>
    <div className="text-[10px] text-slate-400 font-mono">{data.config?.condition || 'No condition'}</div>
    <Handle type="source" position={Position.Bottom} className="w-3 h-3 bg-amber-500" />
  </div>
);

export const AggregateNode = ({ data }: any) => (
  <div className="bg-slate-900 border-2 border-purple-500 p-4 rounded-lg shadow-xl text-white min-w-[150px]">
    <Handle type="target" position={Position.Top} className="w-3 h-3 bg-purple-500" />
    <div className="flex items-center gap-2 mb-2 border-b border-slate-700 pb-2">
      <Sigma size={16} className="text-purple-400" />
      <span className="font-bold text-xs uppercase tracking-wider">Aggregate</span>
    </div>
    <div className="text-[10px] text-slate-400">By: {data.config?.groupBy.join(', ')}</div>
    <Handle type="source" position={Position.Bottom} className="w-3 h-3 bg-purple-500" />
  </div>
);

export const OutputNode = ({ data }: any) => (
  <div className="bg-slate-900 border-2 border-green-500 p-4 rounded-lg shadow-xl text-white min-w-[150px]">
    <Handle type="target" position={Position.Top} className="w-3 h-3 bg-green-500" />
    <div className="flex items-center gap-2 mb-2 border-b border-slate-700 pb-2">
      <LayoutTemplate size={16} className="text-green-400" />
      <span className="font-bold text-xs uppercase tracking-wider">Output</span>
    </div>
    <div className="text-[10px] text-slate-400">Final Result Set</div>
  </div>
);
