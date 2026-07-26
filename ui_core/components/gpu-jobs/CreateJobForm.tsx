import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2, Plus, AlertTriangle, CheckCircle2 } from "lucide-react";
import { useGpuJobs } from "@/hooks/useGpuJobs";
import { JOB_TYPE_OPTIONS, GPU_MEMORY_LIMIT_MB } from "@/lib/gpuJobTypes";

export function CreateJobForm() {
  const { createJob, getMemoryReport } = useGpuJobs();
  const [loading, setLoading] = useState(false);
  const [jobType, setJobType] = useState("");
  const [jobName, setJobName] = useState("");
  const [priority, setPriority] = useState([5]);
  const [payload, setPayload] = useState("{}");
  const [memoryRequired, setMemoryRequired] = useState(4096);

  const memoryReport = getMemoryReport();
  const selectedJobType = JOB_TYPE_OPTIONS.find((o) => o.value === jobType);
  const estimatedMemory = selectedJobType?.memoryEstimate || memoryRequired;
  const canSubmit = jobType && estimatedMemory <= memoryReport.max_job_size_mb;

  const handleJobTypeChange = (value: string) => {
    setJobType(value);
    const option = JOB_TYPE_OPTIONS.find((o) => o.value === value);
    if (option) {
      setMemoryRequired(option.memoryEstimate);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;

    setLoading(true);
    try {
      let parsedPayload = {};
      try {
        parsedPayload = JSON.parse(payload);
      } catch {
        parsedPayload = { raw: payload };
      }

      await createJob({
        job_type: jobType,
        job_name: jobName || undefined,
        payload: parsedPayload,
        priority: priority[0],
        memory_required_mb: memoryRequired,
      });

      // Reset form
      setJobType("");
      setJobName("");
      setPriority([5]);
      setPayload("{}");
      setMemoryRequired(4096);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Plus className="h-5 w-5 text-primary" />
          Create New Job
        </CardTitle>
        <CardDescription>Submit a new GPU compute job to the HYPER queue</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Memory Status Alert */}
          {memoryReport.can_accept_job ? (
            <Alert className="border-primary/30 bg-primary/10">
              <CheckCircle2 className="h-4 w-4 text-primary" />
              <AlertDescription>
                GPU ready: {memoryReport.available_mb.toLocaleString()}MB available (max job:{" "}
                {memoryReport.max_job_size_mb.toLocaleString()}MB)
              </AlertDescription>
            </Alert>
          ) : (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                GPU memory low. Please wait for current jobs to complete.
              </AlertDescription>
            </Alert>
          )}

          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="jobType">Job Type</Label>
              <Select value={jobType} onValueChange={handleJobTypeChange}>
                <SelectTrigger>
                  <SelectValue placeholder="Select job type" />
                </SelectTrigger>
                <SelectContent>
                  {JOB_TYPE_OPTIONS.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label} (~{(option.memoryEstimate / 1024).toFixed(1)}GB)
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="jobName">Job Name (Optional)</Label>
              <Input
                id="jobName"
                placeholder="My Training Job"
                value={jobName}
                onChange={(e) => setJobName(e.target.value)}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label>Priority: {priority[0]} (1 = Low, 10 = High)</Label>
            <Slider
              value={priority}
              onValueChange={setPriority}
              min={1}
              max={10}
              step={1}
              className="w-full"
            />
          </div>

          <div className="space-y-2">
            <Label>Memory Required: {(memoryRequired / 1024).toFixed(1)}GB</Label>
            <Slider
              value={[memoryRequired]}
              onValueChange={([val]) => setMemoryRequired(val)}
              min={512}
              max={GPU_MEMORY_LIMIT_MB}
              step={512}
              className="w-full"
            />
            {memoryRequired > memoryReport.max_job_size_mb && (
              <p className="text-sm text-destructive">
                Exceeds maximum allowed ({(memoryReport.max_job_size_mb / 1024).toFixed(1)}GB)
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="payload">Job Payload (JSON)</Label>
            <Textarea
              id="payload"
              placeholder='{"model": "gpt-4", "input": "..."}'
              value={payload}
              onChange={(e) => setPayload(e.target.value)}
              rows={4}
              className="font-mono text-sm"
            />
          </div>

          <Button type="submit" disabled={loading || !canSubmit} className="w-full">
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Creating Job...
              </>
            ) : (
              <>
                <Plus className="mr-2 h-4 w-4" />
                Submit Job to Queue
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
