import { useState, useEffect } from 'react';
import { firebaseClient as supabase } from '@/integrations/firebase/client';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';

export const QUANTUM_ALGORITHMS = [
  { value: 'qft', label: 'Quantum Fourier Transform' },
  { value: 'grover', label: "Grover's Search" },
  { value: 'vqe', label: 'Variational Quantum Eigensolver' },
  { value: 'qaoa', label: 'QAOA' },
  { value: 'custom', label: 'Custom Circuit' },
];

export const QUANTUM_GATES = ['H', 'X', 'Y', 'Z', 'CNOT', 'CZ', 'RX', 'RY', 'RZ', 'SWAP', 'T', 'S'];

export function useQuantumData() {
  const { user } = useAuth();
  const [circuits, setCircuits] = useState<any[]>([]);
  const [jobs, setJobs] = useState<any[]>([]);
  const [benchmarks, setBenchmarks] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (user) fetchAll();
  }, [user]);

  const fetchAll = async () => {
    setIsLoading(true);
    const [circuitsRes, jobsRes, benchmarksRes] = await Promise.all([
      supabase.from('quantum_circuits').select('*').order('created_at', { ascending: false }),
      supabase.from('quantum_jobs').select('*, quantum_circuits(name)').order('created_at', { ascending: false }),
      supabase.from('quantum_benchmarks').select('*').order('created_at', { ascending: false }),
    ]);
    if (circuitsRes.data) setCircuits(circuitsRes.data);
    if (jobsRes.data) setJobs(jobsRes.data);
    if (benchmarksRes.data) setBenchmarks(benchmarksRes.data);
    setIsLoading(false);
  };

  const createCircuit = async (data: { name: string; algorithm_type: string; qubit_count: number; circuit_data?: any }) => {
    if (!user) return;
    const { error } = await supabase.from('quantum_circuits').insert({ ...data, user_id: user.id });
    if (error) toast.error('Failed to create circuit');
    else { toast.success('Circuit created'); fetchAll(); }
  };

  const runJob = async (circuitId: string, shots: number = 1000) => {
    if (!user) return;
    const { error } = await supabase.from('quantum_jobs').insert({ user_id: user.id, circuit_id: circuitId, shots, status: 'queued' });
    if (error) toast.error('Failed to queue job');
    else { toast.success('Job queued'); fetchAll(); }
  };

  const runBenchmark = async (circuitId: string) => {
    if (!user) return;
    // PRODUCTION HONESTY: Benchmarks require real quantum/classical execution
    // Queue benchmark job with pending status - no fake timing data
    const { error } = await supabase.from('quantum_benchmarks').insert({
      user_id: user.id, 
      circuit_id: circuitId,
      quantum_time_ms: null, // Awaiting real quantum execution
      classical_time_ms: null, // Awaiting real classical execution
      speedup_factor: null, // Will be calculated from real results
      resource_usage: { qubits: 4, gates: 12, depth: 8, status: 'pending_execution' }
    });
    if (error) toast.error('Failed to queue benchmark');
    else { toast.success('Benchmark queued - awaiting execution'); fetchAll(); }
  };

  const deleteCircuit = async (id: string) => {
    const { error } = await supabase.from('quantum_circuits').delete().eq('id', id);
    if (error) toast.error('Failed to delete');
    else { toast.success('Deleted'); fetchAll(); }
  };

  return { circuits, jobs, benchmarks, isLoading, createCircuit, runJob, runBenchmark, deleteCircuit };
}
