import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Atom, Play, Trash2, Plus, Zap } from "lucide-react";
import { useQuantumData, QUANTUM_ALGORITHMS } from "@/hooks/useQuantumData";
import { LoadingState } from "@/components/ui/loading-state";
import { EmptyState } from "@/components/ui/empty-state";

const QuantumPage = () => {
  const {
    circuits,
    jobs,
    benchmarks,
    isLoading,
    createCircuit,
    runJob,
    runBenchmark,
    deleteCircuit,
  } = useQuantumData();
  const [name, setName] = useState("");
  const [algorithm, setAlgorithm] = useState("custom");
  const [qubits, setQubits] = useState("4");

  const handleCreate = async () => {
    if (!name.trim()) return;
    await createCircuit({ name, algorithm_type: algorithm, qubit_count: parseInt(qubits) });
    setName("");
  };

  if (isLoading) return <LoadingState message="Loading quantum workspace..." />;

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Quantum Hybrid Execution</h1>
        <p className="text-muted-foreground">
          Build and run quantum circuits with classical benchmarking
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Circuits</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{circuits.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Jobs Run</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{jobs.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Avg Speedup</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">
              {benchmarks.length
                ? (
                    benchmarks.reduce((s, b) => s + (b.speedup_factor || 0), 0) / benchmarks.length
                  ).toFixed(1)
                : 0}
              x
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Total Qubits</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{circuits.reduce((s, c) => s + c.qubit_count, 0)}</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="circuits">
        <TabsList>
          <TabsTrigger value="circuits">Circuits</TabsTrigger>
          <TabsTrigger value="jobs">Jobs</TabsTrigger>
          <TabsTrigger value="benchmarks">Benchmarks</TabsTrigger>
        </TabsList>

        <TabsContent value="circuits" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Create Circuit</CardTitle>
            </CardHeader>
            <CardContent className="flex gap-4 flex-wrap">
              <Input
                placeholder="Circuit name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-48"
              />
              <Select value={algorithm} onValueChange={setAlgorithm}>
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {QUANTUM_ALGORITHMS.map((a) => (
                    <SelectItem key={a.value} value={a.value}>
                      {a.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Input
                type="number"
                placeholder="Qubits"
                value={qubits}
                onChange={(e) => setQubits(e.target.value)}
                className="w-24"
              />
              <Button onClick={handleCreate}>
                <Plus className="mr-2 h-4 w-4" />
                Create
              </Button>
            </CardContent>
          </Card>
          {circuits.length === 0 ? (
            <EmptyState
              title="No circuits"
              description="Create your first quantum circuit"
              icon={Atom}
            />
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {circuits.map((c) => (
                <Card key={c.id}>
                  <CardHeader>
                    <div className="flex justify-between">
                      <CardTitle>{c.name}</CardTitle>
                      <Badge>{c.algorithm_type}</Badge>
                    </div>
                    <CardDescription>{c.qubit_count} qubits</CardDescription>
                  </CardHeader>
                  <CardContent className="flex gap-2">
                    <Button size="sm" onClick={() => runJob(c.id)}>
                      <Play className="mr-1 h-4 w-4" />
                      Run
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => runBenchmark(c.id)}>
                      <Zap className="mr-1 h-4 w-4" />
                      Benchmark
                    </Button>
                    <Button size="sm" variant="destructive" onClick={() => deleteCircuit(c.id)}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="jobs">
          {jobs.length === 0 ? (
            <EmptyState title="No jobs" description="Run a circuit to create jobs" />
          ) : (
            jobs.map((j) => (
              <Card key={j.id} className="mb-2">
                <CardContent className="flex justify-between items-center py-3">
                  <div>
                    <p className="font-medium">{j.quantum_circuits?.name || "Circuit"}</p>
                    <p className="text-sm text-muted-foreground">{j.shots} shots</p>
                  </div>
                  <Badge>{j.status}</Badge>
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>

        <TabsContent value="benchmarks">
          {benchmarks.length === 0 ? (
            <EmptyState
              title="No benchmarks"
              description="Run a benchmark to compare quantum vs classical"
            />
          ) : (
            benchmarks.map((b) => (
              <Card key={b.id} className="mb-2">
                <CardContent className="grid grid-cols-4 gap-4 py-3 text-center">
                  <div>
                    <p className="text-muted-foreground text-xs">Quantum</p>
                    <p className="font-bold">{b.quantum_time_ms}ms</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground text-xs">Classical</p>
                    <p className="font-bold">{b.classical_time_ms}ms</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground text-xs">Speedup</p>
                    <p className="font-bold text-primary">{b.speedup_factor?.toFixed(1)}x</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground text-xs">Date</p>
                    <p className="text-sm">{new Date(b.created_at).toLocaleDateString()}</p>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default QuantumPage;
