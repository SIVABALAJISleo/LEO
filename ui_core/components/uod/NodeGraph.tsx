import React, { useState, useCallback, useMemo } from 'react';
import ReactFlow, { 
  addEdge, 
  Background, 
  Controls, 
  Connection, 
  Edge, 
  Node, 
  useNodesState, 
  useEdgesState,
  Panel
} from 'reactflow';
import 'reactflow/dist/style.css';
import { DatasetNode, FilterNode, AggregateNode, OutputNode } from './UOD_Nodes';
import { SQLCompiler } from './SQLCompiler';
import { globalDuckDB } from './DuckDBEngine';
import './UOD.css';

const nodeTypes = {
  dataset: DatasetNode,
  filter: FilterNode,
  aggregate: AggregateNode,
  output: OutputNode,
};

const initialNodes: Node[] = [
  { 
    id: '1', 
    type: 'dataset', 
    position: { x: 250, y: 50 }, 
    data: { type: 'dataset', value: 'sales_data' } 
  },
  { 
    id: '2', 
    type: 'filter', 
    position: { x: 250, y: 200 }, 
    data: { type: 'filter', config: { condition: 'revenue > 1000' } } 
  },
  { 
    id: '3', 
    type: 'output', 
    position: { x: 250, y: 350 }, 
    data: { type: 'output' } 
  },
];

const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2', animated: true },
  { id: 'e2-3', source: '2', target: '3', animated: true },
];

export const NodeGraph = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [sql, setSql] = useState('');
  const [results, setResults] = useState<any[]>([]);

  const onConnect = useCallback((params: Connection) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

  const compileAndRun = async () => {
    const compiledSql = SQLCompiler.compile(nodes, edges);
    setSql(compiledSql);
    try {
      // Mock registration for demo
      // In a real app, this would be a Parquet URL from the ingestion engine
      await globalDuckDB.runQuery('CREATE TABLE IF NOT EXISTS sales_data AS SELECT * FROM (SELECT 100.5 AS revenue, "A" AS user_id UNION ALL SELECT 2000.0, "B")');
      const res = await globalDuckDB.runQuery(compiledSql);
      setResults(res);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="w-full h-full relative bg-slate-950">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background color="#1e293b" gap={20} />
        <Controls />
        
        <Panel position="top-right" className="bg-slate-900/90 p-4 rounded-xl border border-slate-700 w-80 text-white shadow-2xl backdrop-blur-md">
          <h3 className="text-blue-400 font-bold mb-2 flex items-center gap-2 uppercase text-xs tracking-widest">
            <span className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
            Live SQL Pipeline
          </h3>
          <div className="bg-black/50 p-3 rounded font-mono text-[10px] text-amber-300 break-words mb-4 border border-amber-900/30">
            {sql || '-- Build graph to see SQL'}
          </div>
          <button 
            onClick={compileAndRun}
            className="w-full bg-blue-600 hover:bg-blue-500 text-white py-2 rounded-lg font-bold text-sm transition-all active:scale-95 shadow-lg shadow-blue-900/20"
          >
            EXECUTE DATAFLOW
          </button>
        </Panel>

        <Panel position="bottom-left" className="bg-slate-900/90 p-4 rounded-xl border border-slate-700 max-w-lg min-h-[100px] text-white shadow-2xl backdrop-blur-md overflow-auto max-h-[300px]">
          <h3 className="text-green-400 font-bold mb-2 uppercase text-xs tracking-widest">Result Preview</h3>
          {results.length > 0 ? (
            <table className="w-full text-xs text-slate-300">
              <thead>
                <tr className="border-b border-slate-700">
                  {Object.keys(results[0]).map(k => <th key={k} className="text-left p-1">{k}</th>)}
                </tr>
              </thead>
              <tbody>
                {results.map((r, i) => (
                  <tr key={i} className="hover:bg-slate-800/50">
                    {Object.values(r).map((v: any, j) => <td key={j} className="p-1">{String(v)}</td>)}
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="text-slate-500 text-sm italic">No data executed yet.</div>
          )}
        </Panel>
      </ReactFlow>
    </div>
  );
};
