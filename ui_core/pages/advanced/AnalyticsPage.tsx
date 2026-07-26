import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  BarChart3,
  PieChart,
  TrendingUp,
  FileText,
  Plus,
  Play,
  Download,
  Share2,
} from "lucide-react";
import { useAdvancedAnalyticsData } from "@/hooks/useAdvancedAnalyticsData";
import { LoadingState } from "@/components/ui/loading-state";
import { EmptyState } from "@/components/ui/empty-state";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";

const AnalyticsPage = () => {
  const { dashboards, reports, visualizations, isLoading, createDashboard, createReport } =
    useAdvancedAnalyticsData();
  const [isCreateDashboardOpen, setIsCreateDashboardOpen] = useState(false);
  const [isCreateReportOpen, setIsCreateReportOpen] = useState(false);
  const [newDashboard, setNewDashboard] = useState({ name: "", description: "" });
  const [newReport, setNewReport] = useState({
    name: "",
    description: "",
    report_type: "performance",
  });

  const handleCreateDashboard = async () => {
    if (!newDashboard.name) {
      toast.error("Dashboard name is required");
      return;
    }
    await createDashboard(newDashboard);
    setNewDashboard({ name: "", description: "" });
    setIsCreateDashboardOpen(false);
  };

  const handleCreateReport = async () => {
    if (!newReport.name) {
      toast.error("Report name is required");
      return;
    }
    await createReport(newReport);
    setNewReport({ name: "", description: "", report_type: "performance" });
    setIsCreateReportOpen(false);
  };

  if (isLoading) return <LoadingState message="Loading analytics..." />;

  return (
    <div className="space-y-6 p-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold">Advanced Analytics</h1>
          <p className="text-muted-foreground">Dashboards, reports, and predictive analytics</p>
        </div>
        <div className="flex gap-2">
          <Dialog open={isCreateDashboardOpen} onOpenChange={setIsCreateDashboardOpen}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <Plus className="mr-2 h-4 w-4" /> New Dashboard
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create Dashboard</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label>Name</Label>
                  <Input
                    value={newDashboard.name}
                    onChange={(e) => setNewDashboard({ ...newDashboard, name: e.target.value })}
                    placeholder="Dashboard name"
                  />
                </div>
                <div>
                  <Label>Description</Label>
                  <Textarea
                    value={newDashboard.description}
                    onChange={(e) =>
                      setNewDashboard({ ...newDashboard, description: e.target.value })
                    }
                    placeholder="Dashboard description"
                  />
                </div>
                <Button onClick={handleCreateDashboard} className="w-full">
                  Create Dashboard
                </Button>
              </div>
            </DialogContent>
          </Dialog>
          <Dialog open={isCreateReportOpen} onOpenChange={setIsCreateReportOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" /> New Report
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create Report</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label>Name</Label>
                  <Input
                    value={newReport.name}
                    onChange={(e) => setNewReport({ ...newReport, name: e.target.value })}
                    placeholder="Report name"
                  />
                </div>
                <div>
                  <Label>Description</Label>
                  <Textarea
                    value={newReport.description}
                    onChange={(e) => setNewReport({ ...newReport, description: e.target.value })}
                    placeholder="Report description"
                  />
                </div>
                <div>
                  <Label>Report Type</Label>
                  <Select
                    value={newReport.report_type}
                    onValueChange={(v) => setNewReport({ ...newReport, report_type: v })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="performance">Performance</SelectItem>
                      <SelectItem value="cost">Cost Analysis</SelectItem>
                      <SelectItem value="usage">Usage Statistics</SelectItem>
                      <SelectItem value="predictive">Predictive</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button onClick={handleCreateReport} className="w-full">
                  Create Report
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Dashboards</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{dashboards.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Reports</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{reports.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Visualizations</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{visualizations.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Scheduled</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{reports.filter((r) => r.schedule).length}</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="dashboards">
        <TabsList>
          <TabsTrigger value="dashboards">Dashboards</TabsTrigger>
          <TabsTrigger value="reports">Reports</TabsTrigger>
          <TabsTrigger value="visualizations">Visualizations</TabsTrigger>
        </TabsList>

        <TabsContent value="dashboards" className="space-y-4">
          {dashboards.length === 0 ? (
            <EmptyState
              title="No dashboards"
              description="Create your first analytics dashboard"
              icon={BarChart3}
            />
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {dashboards.map((d) => (
                <Card key={d.id} className="hover:border-primary/50 transition-colors">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <CardTitle className="text-lg">{d.name}</CardTitle>
                      <div className="flex gap-1">
                        {d.is_default && <Badge variant="secondary">Default</Badge>}
                        {d.is_shared && <Badge variant="outline">Shared</Badge>}
                      </div>
                    </div>
                    {d.description && (
                      <p className="text-sm text-muted-foreground">{d.description}</p>
                    )}
                  </CardHeader>
                  <CardContent>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline">
                        <BarChart3 className="h-4 w-4 mr-1" /> View
                      </Button>
                      <Button size="sm" variant="outline">
                        <Share2 className="h-4 w-4 mr-1" /> Share
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="reports" className="space-y-4">
          {reports.length === 0 ? (
            <EmptyState
              title="No reports"
              description="Create your first analytics report"
              icon={FileText}
            />
          ) : (
            <div className="space-y-2">
              {reports.map((r) => (
                <Card key={r.id}>
                  <CardContent className="flex justify-between items-center py-4">
                    <div className="flex items-center gap-4">
                      <FileText className="h-8 w-8 text-primary" />
                      <div>
                        <p className="font-medium">{r.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {r.report_type} • {r.schedule || "Manual"}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {r.last_generated_at && (
                        <span className="text-sm text-muted-foreground">
                          Last run: {new Date(r.last_generated_at).toLocaleDateString()}
                        </span>
                      )}
                      <Button size="sm" variant="outline">
                        <Play className="h-4 w-4 mr-1" /> Run
                      </Button>
                      <Button size="sm" variant="outline">
                        <Download className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="visualizations" className="space-y-4">
          {visualizations.length === 0 ? (
            <EmptyState
              title="No visualizations"
              description="Create custom visualizations for your dashboards"
              icon={PieChart}
            />
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {visualizations.map((v) => (
                <Card key={v.id}>
                  <CardHeader>
                    <CardTitle className="text-lg">{v.name}</CardTitle>
                    <Badge variant="outline">{v.visualization_type}</Badge>
                  </CardHeader>
                  <CardContent>
                    <div className="h-32 bg-muted/50 rounded flex items-center justify-center">
                      <TrendingUp className="h-12 w-12 text-muted-foreground" />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AnalyticsPage;
