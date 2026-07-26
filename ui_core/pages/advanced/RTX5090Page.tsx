import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Cpu, Plus, Play, Save, Zap, Package, Video, HardDrive } from "lucide-react";
import { useRTX5090Data } from "@/hooks/useRTX5090Data";
import { LoadingState } from "@/components/ui/loading-state";
import { EmptyState } from "@/components/ui/empty-state";
import { Switch } from "@/components/ui/switch";

const RTX5090Page = () => {
  const {
    trainingJobs,
    offlinePackages,
    graphicsBenchmarks,
    videoBenchmarks,
    persistentJobs,
    isLoading,
    createTrainingJob,
    createOfflinePackage,
    runGraphicsBenchmark,
    runVideoBenchmark,
    createPersistentJob,
    checkpointJob,
  } = useRTX5090Data();
  const [name, setName] = useState("");
  const [mixedPrecision, setMixedPrecision] = useState(true);
  const [gradientComp, setGradientComp] = useState(true);

  if (isLoading) return <LoadingState message="Loading HYPER Engine data..." />;

  const avgSpeedup = trainingJobs.length
    ? trainingJobs.reduce((s, j) => s + (j.speedup_vs_rtx5090 || 0), 0) / trainingJobs.length
    : 0;
  const avgComparison = graphicsBenchmarks.length
    ? graphicsBenchmarks.reduce((s, b) => s + (b.comparison_percent || 0), 0) /
      graphicsBenchmarks.length
    : 0;

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">HYPER Compute Engine</h1>
        <p className="text-muted-foreground">
          Software-only GPU acceleration matching high-end GPU performance
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-5">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Training Jobs</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{trainingJobs.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Avg vs Legacy GPU</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-primary">{(avgSpeedup * 100).toFixed(0)}%</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Graphics Perf</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{avgComparison.toFixed(0)}%</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Offline Packages</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{offlinePackages.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Persistent Jobs</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">
              {persistentJobs.filter((j) => j.status === "running").length}
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="training">
        <TabsList className="flex-wrap">
          <TabsTrigger value="training">
            <Zap className="h-4 w-4 mr-1" />
            Training
          </TabsTrigger>
          <TabsTrigger value="offline">
            <Package className="h-4 w-4 mr-1" />
            Offline
          </TabsTrigger>
          <TabsTrigger value="graphics">
            <Cpu className="h-4 w-4 mr-1" />
            Graphics
          </TabsTrigger>
          <TabsTrigger value="video">
            <Video className="h-4 w-4 mr-1" />
            Video
          </TabsTrigger>
          <TabsTrigger value="persistent">
            <HardDrive className="h-4 w-4 mr-1" />
            Persistent
          </TabsTrigger>
        </TabsList>

        <TabsContent value="training" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Create Distributed Training Job</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input
                placeholder="Job name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
              <div className="flex gap-6">
                <label className="flex items-center gap-2">
                  <Switch checked={mixedPrecision} onCheckedChange={setMixedPrecision} />
                  Mixed Precision
                </label>
                <label className="flex items-center gap-2">
                  <Switch checked={gradientComp} onCheckedChange={setGradientComp} />
                  Gradient Compression
                </label>
              </div>
              <Button
                onClick={() => {
                  createTrainingJob({
                    name,
                    mixed_precision: mixedPrecision,
                    gradient_compression: gradientComp,
                  });
                  setName("");
                }}
              >
                <Plus className="mr-2 h-4 w-4" />
                Create Job
              </Button>
            </CardContent>
          </Card>
          {trainingJobs.length === 0 ? (
            <EmptyState
              title="No training jobs"
              description="Create a distributed training job"
              icon={Zap}
            />
          ) : (
            trainingJobs.map((j) => (
              <Card key={j.id}>
                <CardContent className="flex justify-between items-center py-3">
                  <div>
                    <p className="font-medium">{j.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {j.node_count} nodes • {j.mixed_precision ? "FP16" : "FP32"}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-primary">
                      {((j.speedup_vs_rtx5090 || 0) * 100).toFixed(0)}% vs Legacy GPU
                    </span>
                    <Badge>{j.status}</Badge>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>

        <TabsContent value="offline" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Create Offline Package</CardTitle>
            </CardHeader>
            <CardContent className="flex gap-4">
              <Input
                placeholder="Package name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
              <Button
                onClick={() => {
                  createOfflinePackage({ name });
                  setName("");
                }}
              >
                <Plus className="mr-2 h-4 w-4" />
                Build
              </Button>
            </CardContent>
          </Card>
          {offlinePackages.map((p) => (
            <Card key={p.id}>
              <CardContent className="flex justify-between py-3">
                <div>
                  <p className="font-medium">{p.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {p.total_size_mb?.toFixed(0)} MB • {p.estimated_latency_ms}ms latency
                  </p>
                </div>
                <Badge>{p.status}</Badge>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="graphics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Run Graphics Benchmark</CardTitle>
            </CardHeader>
            <CardContent className="flex gap-4">
              <Input
                placeholder="Benchmark name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
              <Button
                onClick={() => {
                  runGraphicsBenchmark({ name });
                  setName("");
                }}
              >
                <Play className="mr-2 h-4 w-4" />
                Run
              </Button>
            </CardContent>
          </Card>
          {graphicsBenchmarks.map((b) => (
            <Card key={b.id}>
              <CardContent className="grid grid-cols-4 gap-4 py-3 text-center">
                <div>
                  <p className="text-muted-foreground text-xs">HYPER Engine</p>
                  <p className="font-bold">{b.your_engine_fps?.toFixed(0)} FPS</p>
                </div>
                <div>
                  <p className="text-muted-foreground text-xs">Legacy GPU</p>
                  <p className="font-bold">{b.rtx5090_fps?.toFixed(0)} FPS</p>
                </div>
                <div>
                  <p className="text-muted-foreground text-xs">Comparison</p>
                  <p
                    className={`font-bold ${(b.comparison_percent || 0) >= 95 ? "text-primary" : ""}`}
                  >
                    {b.comparison_percent?.toFixed(1)}%
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground text-xs">Scene</p>
                  <p>{b.scene_complexity}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="video" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Run Video Benchmark</CardTitle>
            </CardHeader>
            <CardContent className="flex gap-4">
              <Input
                placeholder="Benchmark name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
              <Button
                onClick={() => {
                  runVideoBenchmark({ name });
                  setName("");
                }}
              >
                <Play className="mr-2 h-4 w-4" />
                Run
              </Button>
            </CardContent>
          </Card>
          {videoBenchmarks.map((b) => (
            <Card key={b.id}>
              <CardContent className="grid grid-cols-4 gap-4 py-3 text-center">
                <div>
                  <p className="text-muted-foreground text-xs">Resolution</p>
                  <p className="font-bold">{b.resolution}</p>
                </div>
                <div>
                  <p className="text-muted-foreground text-xs">Framerate</p>
                  <p className="font-bold">{b.framerate} fps</p>
                </div>
                <div>
                  <p className="text-muted-foreground text-xs">Quality</p>
                  <p className="font-bold">{b.quality_score?.toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-muted-foreground text-xs">Latency</p>
                  <p className="font-bold">{b.latency_ms}ms</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="persistent" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Create Persistent Compute Job</CardTitle>
            </CardHeader>
            <CardContent className="flex gap-4">
              <Input
                placeholder="Job name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
              <Button
                onClick={() => {
                  createPersistentJob({ name, job_type: "long_running" });
                  setName("");
                }}
              >
                <Plus className="mr-2 h-4 w-4" />
                Start
              </Button>
            </CardContent>
          </Card>
          {persistentJobs.map((j) => (
            <Card key={j.id}>
              <CardContent className="flex justify-between items-center py-3">
                <div>
                  <p className="font-medium">{j.name}</p>
                  <p className="text-sm text-muted-foreground">
                    Max {j.max_duration_hours}h • {j.recovery_count} recoveries
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Button size="sm" variant="outline" onClick={() => checkpointJob(j.id)}>
                    <Save className="h-4 w-4 mr-1" />
                    Checkpoint
                  </Button>
                  <Badge>{j.status}</Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default RTX5090Page;
