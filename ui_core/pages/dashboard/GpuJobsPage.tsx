import { CreateJobForm } from "@/components/gpu-jobs/CreateJobForm";
import { JobQueueList } from "@/components/gpu-jobs/JobQueueList";
import { SystemStatusPanel } from "@/components/gpu-jobs/SystemStatusPanel";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { useGpuJobs } from "@/hooks/useGpuJobs";
import { Cpu, ListOrdered, Activity, Shield, Wifi, Thermometer, HardDrive } from "lucide-react";

export default function GpuJobsPage() {
  const { getJobStats, getThermalStatus, getMemoryReport } = useGpuJobs();
  const stats = getJobStats();
  const thermal = getThermalStatus();
  const memory = getMemoryReport();

  return (
    <>
      <div className="flex-1 space-y-6 p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-primary">Smart GPU Job Queue</h1>
          <p className="text-muted-foreground">
            Submit, monitor, and manage your GPU compute jobs with full safety protection
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card className="bg-card border-border">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Active Jobs</CardTitle>
              <Activity className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.running}</div>
              <p className="text-xs text-muted-foreground">{stats.pending} queued</p>
            </CardContent>
          </Card>

          <Card className="bg-card border-border">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">GPU Memory</CardTitle>
              <HardDrive className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {((memory.total_mb - memory.available_mb) / 1024).toFixed(1)}GB
              </div>
              <p className="text-xs text-muted-foreground">
                of {(memory.total_mb / 1024).toFixed(0)}GB used
              </p>
            </CardContent>
          </Card>

          <Card className="bg-card border-border">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">GPU Temp</CardTitle>
              <Thermometer
                className={`h-4 w-4 ${thermal.is_safe ? "text-primary" : "text-orange-500"}`}
              />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{thermal.gpu_temp}°C</div>
              <p className="text-xs text-muted-foreground">
                {thermal.is_safe ? "Normal" : "Elevated"}
              </p>
            </CardContent>
          </Card>

          <Card className="bg-card border-border">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Protection</CardTitle>
              <Shield className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <Badge variant="default" className="bg-primary">
                  Active
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground mt-1">All 6 safeguards enabled</p>
            </CardContent>
          </Card>
        </div>

        {/* Feature Badges */}
        <div className="flex flex-wrap gap-2">
          <Badge variant="outline" className="gap-1">
            <Shield className="h-3 w-3" /> Safe Queue
          </Badge>
          <Badge variant="outline" className="gap-1">
            <Wifi className="h-3 w-3" /> Offline-Proof
          </Badge>
          <Badge variant="outline" className="gap-1">
            <HardDrive className="h-3 w-3" /> Memory-Aware
          </Badge>
          <Badge variant="outline" className="gap-1">
            <Thermometer className="h-3 w-3" /> Thermal Protection
          </Badge>
          <Badge variant="outline" className="gap-1">
            <Cpu className="h-3 w-3" /> Local Execution
          </Badge>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="queue" className="space-y-4">
          <TabsList>
            <TabsTrigger value="queue" className="gap-2">
              <ListOrdered className="h-4 w-4" />
              Job Queue
            </TabsTrigger>
            <TabsTrigger value="create" className="gap-2">
              <Cpu className="h-4 w-4" />
              Create Job
            </TabsTrigger>
            <TabsTrigger value="status" className="gap-2">
              <Activity className="h-4 w-4" />
              System Status
            </TabsTrigger>
          </TabsList>

          <TabsContent value="queue" className="space-y-4">
            <JobQueueList />
          </TabsContent>

          <TabsContent value="create" className="space-y-4">
            <div className="grid gap-6 lg:grid-cols-2">
              <CreateJobForm />
              <SystemStatusPanel />
            </div>
          </TabsContent>

          <TabsContent value="status" className="space-y-4">
            <div className="grid gap-6 lg:grid-cols-2">
              <SystemStatusPanel />
              <Card className="bg-card border-border">
                <CardHeader>
                  <CardTitle>Safety Features</CardTitle>
                  <CardDescription>
                    HYPER's Smart GPU Job Management protects your hardware
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex items-start gap-3 p-3 bg-primary/5 rounded-lg">
                      <Shield className="h-5 w-5 text-primary mt-0.5" />
                      <div>
                        <h4 className="font-medium">Safe Job Queue</h4>
                        <p className="text-sm text-muted-foreground">
                          Users never touch GPU directly. Only HYPER worker processes jobs.
                        </p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3 p-3 bg-primary/5 rounded-lg">
                      <Wifi className="h-5 w-5 text-primary mt-0.5" />
                      <div>
                        <h4 className="font-medium">Offline-Proof Execution</h4>
                        <p className="text-sm text-muted-foreground">
                          Checkpoints every 2 minutes. Continues if Wi-Fi drops.
                        </p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3 p-3 bg-primary/5 rounded-lg">
                      <HardDrive className="h-5 w-5 text-primary mt-0.5" />
                      <div>
                        <h4 className="font-medium">Memory-Aware</h4>
                        <p className="text-sm text-muted-foreground">
                          Rejects jobs that would crash the GPU due to memory overflow.
                        </p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3 p-3 bg-primary/5 rounded-lg">
                      <Thermometer className="h-5 w-5 text-primary mt-0.5" />
                      <div>
                        <h4 className="font-medium">Thermal Protection</h4>
                        <p className="text-sm text-muted-foreground">
                          Auto-pauses jobs if GPU overheats. Resumes when safe.
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </>
  );
}
