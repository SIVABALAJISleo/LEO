import { useState, useEffect } from "react";
import { useSettingsData } from "@/hooks/useSettingsData";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/hooks/use-toast";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
  DialogDescription,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import {
  User,
  Key,
  Bell,
  Settings2,
  Webhook,
  Database,
  Trash2,
  Copy,
  Eye,
  EyeOff,
  Plus,
  Check,
  X,
  RefreshCw,
  Download,
  AlertTriangle,
  Shield,
} from "lucide-react";
import { format } from "date-fns";
import { ComputeSafetySettings } from "@/components/settings/ComputeSafetySettings";

const SettingsPage = () => {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const {
    loading,
    profile,
    apiKeys,
    subscription,
    updateProfile,
    generateApiKey,
    revokeApiKey,
    deleteApiKey,
    refreshAll,
  } = useSettingsData();
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { user, signOut } = useAuth();
  const { toast } = useToast();

  const [fullName, setFullName] = useState(profile?.full_name || "");
  const [company, setCompany] = useState(profile?.company || "");
  const [isSaving, setIsSaving] = useState(false);
  const [newKeyName, setNewKeyName] = useState("");
  const [showNewKeyDialog, setShowNewKeyDialog] = useState(false);
  const [newlyGeneratedKey, setNewlyGeneratedKey] = useState<string | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [visibleKeys, setVisibleKeys] = useState<Record<string, boolean>>({});
  const [webhookUrl, setWebhookUrl] = useState("");
  const [webhookTesting, setWebhookTesting] = useState(false);
  const [notifications, setNotifications] = useState({
    email: true,
    jobComplete: true,
    alerts: true,
    weekly: false,
  });

  // Update state when profile loads
  useEffect(() => {
    if (profile) {
      setFullName(profile.full_name || "");
      setCompany(profile.company || "");
    }
  }, [profile]);

  const handleSaveProfile = async () => {
    setIsSaving(true);
    await updateProfile({ full_name: fullName, company });
    setIsSaving(false);
  };

  const handleGenerateKey = async () => {
    if (!newKeyName.trim()) {
      toast({ title: "Error", description: "Please enter a key name", variant: "destructive" });
      return;
    }
    const key = await generateApiKey(newKeyName);
    if (key) {
      setNewlyGeneratedKey(key);
      setNewKeyName("");
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({ title: "Copied", description: "API key copied to clipboard" });
  };

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const toggleKeyVisibility = (keyId: string) => {
    setVisibleKeys((prev) => ({ ...prev, [keyId]: !prev[keyId] }));
  };

  const testWebhook = async () => {
    if (!webhookUrl) {
      toast({ title: "Error", description: "Please enter a webhook URL", variant: "destructive" });
      return;
    }

    setWebhookTesting(true);
    try {
      // PROD SaaS Engine: Local webhook simulation
      await new Promise((r) => setTimeout(r, 1000));

      const isSuccess = Math.random() > 0.2;
      if (isSuccess) {
        toast({ title: "Success", description: "Webhook test successful (Simulated)!" });
      } else {
        toast({
          title: "Failed",
          description: "Webhook returned 500 (Simulated)",
          variant: "destructive",
        });
      }
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      toast({ title: "Error", description: err.message, variant: "destructive" });
    } finally {
      setWebhookTesting(false);
    }
  };

  const exportUserData = async () => {
    if (!user) return;

    // PROD SaaS Engine: Local data export simulation
    const exportData = {
      profile,
      subscription,
      jobs: [],
      metrics: [],
      alerts: [],
      exportedAt: new Date().toISOString(),
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `hyper-data-${new Date().toISOString().split("T")[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);

    toast({ title: "Data Exported", description: "Your data has been downloaded" });
  };

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <Skeleton className="h-16" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Skeleton className="h-64" />
          <Skeleton className="h-64" />
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-muted-foreground">Manage your account and preferences</p>
      </div>

      <Tabs defaultValue="profile" className="w-full">
        <TabsList className="mb-6 flex-wrap">
          <TabsTrigger value="profile" className="flex items-center gap-2">
            <User className="h-4 w-4" />
            Profile
          </TabsTrigger>
          <TabsTrigger value="api-keys" className="flex items-center gap-2">
            <Key className="h-4 w-4" />
            API Keys
          </TabsTrigger>
          <TabsTrigger value="notifications" className="flex items-center gap-2">
            <Bell className="h-4 w-4" />
            Notifications
          </TabsTrigger>
          <TabsTrigger value="compute-safety" className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Compute Safety
          </TabsTrigger>
          <TabsTrigger value="advanced" className="flex items-center gap-2">
            <Settings2 className="h-4 w-4" />
            Advanced
          </TabsTrigger>
        </TabsList>

        {/* Profile Tab */}
        <TabsContent value="profile">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>Profile Information</CardTitle>
                <CardDescription>Update your account details</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-4">
                  <div className="space-y-3">
                    <Label htmlFor="email" className="text-sm font-semibold">
                      Email
                    </Label>
                    <Input
                      id="email"
                      value={user?.email || ""}
                      disabled
                      className="bg-muted opacity-80"
                    />
                  </div>
                  <div className="space-y-3">
                    <Label htmlFor="fullName" className="text-sm font-semibold">
                      Full Name
                    </Label>
                    <Input
                      id="fullName"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="Enter your full name"
                    />
                  </div>
                  <div className="space-y-3">
                    <Label htmlFor="company" className="text-sm font-semibold">
                      Company
                    </Label>
                    <Input
                      id="company"
                      value={company}
                      onChange={(e) => setCompany(e.target.value)}
                      placeholder="Enter your company name"
                    />
                  </div>
                </div>
                <Button onClick={handleSaveProfile} disabled={isSaving}>
                  {isSaving ? "Saving..." : "Save Changes"}
                </Button>
              </CardContent>
            </Card>

            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>Subscription</CardTitle>
                <CardDescription>Your current plan details</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {subscription ? (
                  <>
                    <div className="flex items-center justify-between">
                      <span className="text-muted-foreground">Plan</span>
                      <Badge variant="default" className="text-lg px-3 py-1">
                        {subscription.tier.toUpperCase()}
                      </Badge>
                    </div>
                    <Separator />
                    <div className="flex items-center justify-between">
                      <span className="text-muted-foreground">Status</span>
                      <Badge variant={subscription.status === "active" ? "default" : "secondary"}>
                        {subscription.status}
                      </Badge>
                    </div>
                    <Separator />
                    <div className="flex items-center justify-between">
                      <span className="text-muted-foreground">API Calls Used</span>
                      <span className="font-medium">
                        {subscription.api_calls_used} / {subscription.api_calls_limit}
                      </span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div
                        className="bg-primary h-2 rounded-full transition-all"
                        style={{
                          width: `${(subscription.api_calls_used / subscription.api_calls_limit) * 100}%`,
                        }}
                      />
                    </div>
                    <Separator />
                    <div className="flex items-center justify-between">
                      <span className="text-muted-foreground">Resets At</span>
                      <span className="text-sm">
                        {format(new Date(subscription.reset_at), "PPP")}
                      </span>
                    </div>
                  </>
                ) : (
                  <p className="text-muted-foreground">No subscription found</p>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* API Keys Tab */}
        <TabsContent value="api-keys">
          <Card className="bg-card border-border">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>API Keys</CardTitle>
                <CardDescription>Manage your API keys for programmatic access</CardDescription>
              </div>
              <Dialog open={showNewKeyDialog} onOpenChange={setShowNewKeyDialog}>
                <DialogTrigger asChild>
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Generate New Key
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Generate API Key</DialogTitle>
                    <DialogDescription>
                      Create a new API key for accessing HYPER services
                    </DialogDescription>
                  </DialogHeader>
                  {newlyGeneratedKey ? (
                    <div className="space-y-4">
                      <div className="p-4 bg-primary/10 rounded-lg border border-primary/20">
                        <p className="text-sm text-muted-foreground mb-2">
                          Your new API key (copy it now, it won't be shown again):
                        </p>
                        <div className="flex items-center gap-2">
                          <code className="flex-1 font-mono text-sm bg-muted p-2 rounded break-all">
                            {newlyGeneratedKey}
                          </code>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => copyToClipboard(newlyGeneratedKey)}
                          >
                            <Copy className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                      <Button
                        className="w-full"
                        onClick={() => {
                          setNewlyGeneratedKey(null);
                          setShowNewKeyDialog(false);
                        }}
                      >
                        Done
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="keyName">Key Name</Label>
                        <Input
                          id="keyName"
                          value={newKeyName}
                          onChange={(e) => setNewKeyName(e.target.value)}
                          placeholder="e.g., Production, Development"
                        />
                      </div>
                      <DialogFooter>
                        <Button variant="outline" onClick={() => setShowNewKeyDialog(false)}>
                          Cancel
                        </Button>
                        <Button onClick={handleGenerateKey}>Generate</Button>
                      </DialogFooter>
                    </div>
                  )}
                </DialogContent>
              </Dialog>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow className="border-border">
                    <TableHead>Name</TableHead>
                    <TableHead>Key</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Last Used</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {apiKeys.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                        No API keys. Generate one to get started.
                      </TableCell>
                    </TableRow>
                  ) : (
                    apiKeys.map((key) => (
                      <TableRow key={key.id} className="border-border">
                        <TableCell className="font-medium">{key.key_name}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <code className="font-mono text-sm text-muted-foreground">
                              {key.key_prefix || "••••••••...••••"}
                            </code>
                            <span className="text-xs text-muted-foreground">
                              (hidden for security)
                            </span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant={key.is_active ? "default" : "secondary"}>
                            {key.is_active ? "Active" : "Revoked"}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-muted-foreground text-sm">
                          {format(new Date(key.created_at), "MMM d, yyyy")}
                        </TableCell>
                        <TableCell className="text-muted-foreground text-sm">
                          {key.last_used_at
                            ? format(new Date(key.last_used_at), "MMM d, yyyy")
                            : "Never"}
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-1">
                            {key.is_active && (
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => revokeApiKey(key.id)}
                              >
                                <X className="h-4 w-4" />
                              </Button>
                            )}
                            <AlertDialog>
                              <AlertDialogTrigger asChild>
                                <Button size="sm" variant="ghost">
                                  <Trash2 className="h-4 w-4 text-destructive" />
                                </Button>
                              </AlertDialogTrigger>
                              <AlertDialogContent>
                                <AlertDialogHeader>
                                  <AlertDialogTitle>Delete API Key?</AlertDialogTitle>
                                  <AlertDialogDescription>
                                    This action cannot be undone. Any applications using this key
                                    will lose access.
                                  </AlertDialogDescription>
                                </AlertDialogHeader>
                                <AlertDialogFooter>
                                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                                  <AlertDialogAction onClick={() => deleteApiKey(key.id)}>
                                    Delete
                                  </AlertDialogAction>
                                </AlertDialogFooter>
                              </AlertDialogContent>
                            </AlertDialog>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle>Notification Preferences</CardTitle>
              <CardDescription>Configure how you receive updates</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Email Notifications</p>
                  <p className="text-sm text-muted-foreground">Receive notifications via email</p>
                </div>
                <Switch
                  checked={notifications.email}
                  onCheckedChange={(v) => setNotifications((prev) => ({ ...prev, email: v }))}
                />
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Job Completion Alerts</p>
                  <p className="text-sm text-muted-foreground">
                    Get notified when inference jobs complete
                  </p>
                </div>
                <Switch
                  checked={notifications.jobComplete}
                  onCheckedChange={(v) => setNotifications((prev) => ({ ...prev, jobComplete: v }))}
                />
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">System Alerts</p>
                  <p className="text-sm text-muted-foreground">
                    Critical alerts about system status
                  </p>
                </div>
                <Switch
                  checked={notifications.alerts}
                  onCheckedChange={(v) => setNotifications((prev) => ({ ...prev, alerts: v }))}
                />
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Weekly Summary</p>
                  <p className="text-sm text-muted-foreground">
                    Receive a weekly performance summary
                  </p>
                </div>
                <Switch
                  checked={notifications.weekly}
                  onCheckedChange={(v) => setNotifications((prev) => ({ ...prev, weekly: v }))}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Compute Safety Tab */}
        <TabsContent value="compute-safety">
          <ComputeSafetySettings />
        </TabsContent>

        {/* Advanced Tab */}
        <TabsContent value="advanced">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Webhook className="h-5 w-5" />
                  Webhook Configuration
                </CardTitle>
                <CardDescription>Test webhook endpoints</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="webhook">Webhook URL</Label>
                  <Input
                    id="webhook"
                    type="url"
                    value={webhookUrl}
                    onChange={(e) => setWebhookUrl(e.target.value)}
                    placeholder="https://your-server.com/webhook"
                  />
                </div>
                <Button onClick={testWebhook} disabled={webhookTesting}>
                  {webhookTesting ? (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      Testing...
                    </>
                  ) : (
                    "Test Webhook"
                  )}
                </Button>
              </CardContent>
            </Card>

            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5" />
                  Data Management
                </CardTitle>
                <CardDescription>Export or delete your data</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button variant="outline" className="w-full" onClick={exportUserData}>
                  <Download className="h-4 w-4 mr-2" />
                  Export All Data
                </Button>

                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button variant="destructive" className="w-full">
                      <Trash2 className="h-4 w-4 mr-2" />
                      Delete Account
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle className="flex items-center gap-2">
                        <AlertTriangle className="h-5 w-5 text-destructive" />
                        Delete Account?
                      </AlertDialogTitle>
                      <AlertDialogDescription>
                        This will permanently delete your account and all associated data. This
                        action cannot be undone.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction className="bg-destructive text-destructive-foreground">
                        Delete Account
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default SettingsPage;
