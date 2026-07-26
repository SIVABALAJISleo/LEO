import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Store, Puzzle, Link2, Download, Star, Search, Plus } from "lucide-react";
import { useMarketplaceData } from "@/hooks/useMarketplaceData";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";

const MarketplacePage = () => {
  const { plugins, integrations, transactions, isLoading, installPlugin } = useMarketplaceData();
  const [searchQuery, setSearchQuery] = useState("");
  const [isCreateIntegrationOpen, setIsCreateIntegrationOpen] = useState(false);
  const [newIntegration, setNewIntegration] = useState({ name: "", integration_type: "webhook" });

  const filteredPlugins = plugins.filter(
    (p) =>
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.category?.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  const handleInstall = async (pluginId: string) => {
    await installPlugin(pluginId);
    toast.success("Plugin installed successfully");
  };

  const handleCreateIntegration = async () => {
    if (!newIntegration.name) {
      toast.error("Integration name is required");
      return;
    }
    toast.info("Integration creation coming soon");
    setNewIntegration({ name: "", integration_type: "webhook" });
    setIsCreateIntegrationOpen(false);
  };

  if (isLoading) return <LoadingState message="Loading marketplace..." />;

  return (
    <div className="space-y-6 p-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold">Marketplace</h1>
          <p className="text-muted-foreground">Plugins, integrations, and extensions</p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Available Plugins</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{plugins.filter((p) => p.is_published).length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Active Integrations</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{integrations.filter((i) => i.is_active).length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Installed</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{integrations.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Total Downloads</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">
              {plugins.reduce((sum, p) => sum + (p.download_count || 0), 0)}
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="plugins">
        <TabsList>
          <TabsTrigger value="plugins">Plugins</TabsTrigger>
          <TabsTrigger value="integrations">Integrations</TabsTrigger>
          <TabsTrigger value="transactions">Transactions</TabsTrigger>
        </TabsList>

        <TabsContent value="plugins" className="space-y-4">
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search plugins..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
          {filteredPlugins.length === 0 ? (
            <EmptyState
              title="No plugins found"
              description="Try adjusting your search"
              icon={Puzzle}
            />
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {filteredPlugins.map((p) => (
                <Card key={p.id} className="hover:border-primary/50 transition-colors">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded bg-primary/20 flex items-center justify-center">
                          <Puzzle className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <CardTitle className="text-lg">{p.name}</CardTitle>
                          <p className="text-sm text-muted-foreground">{p.category}</p>
                        </div>
                      </div>
                      {p.rating && (
                        <div className="flex items-center gap-1 text-yellow-500">
                          <Star className="h-4 w-4 fill-current" />
                          <span className="text-sm">{p.rating.toFixed(1)}</span>
                        </div>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-sm text-muted-foreground line-clamp-2">{p.description}</p>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Download className="h-4 w-4" />
                        <span>{p.download_count || 0}</span>
                        <Badge variant="outline">v{p.version}</Badge>
                      </div>
                      <Button size="sm" onClick={() => handleInstall(p.id)}>
                        {p.price && p.price > 0 ? `$${p.price}` : "Install"}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="integrations" className="space-y-4">
          <div className="flex justify-end">
            <Dialog open={isCreateIntegrationOpen} onOpenChange={setIsCreateIntegrationOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" /> New Integration
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create Integration</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label>Name</Label>
                    <Input
                      value={newIntegration.name}
                      onChange={(e) =>
                        setNewIntegration({ ...newIntegration, name: e.target.value })
                      }
                      placeholder="Integration name"
                    />
                  </div>
                  <div>
                    <Label>Type</Label>
                    <Select
                      value={newIntegration.integration_type}
                      onValueChange={(v) =>
                        setNewIntegration({ ...newIntegration, integration_type: v })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="webhook">Webhook</SelectItem>
                        <SelectItem value="oauth">OAuth</SelectItem>
                        <SelectItem value="api">API</SelectItem>
                        <SelectItem value="database">Database</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Button onClick={handleCreateIntegration} className="w-full">
                    Create
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
          {integrations.length === 0 ? (
            <EmptyState
              title="No integrations"
              description="Connect external services to your platform"
              icon={Link2}
            />
          ) : (
            <div className="space-y-2">
              {integrations.map((i) => (
                <Card key={i.id}>
                  <CardContent className="flex justify-between items-center py-4">
                    <div className="flex items-center gap-4">
                      <Link2 className="h-8 w-8 text-primary" />
                      <div>
                        <p className="font-medium">{i.name}</p>
                        <p className="text-sm text-muted-foreground">{i.integration_type}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={i.is_active ? "default" : "secondary"}>
                        {i.is_active ? "Active" : "Inactive"}
                      </Badge>
                      {i.last_sync_at && (
                        <span className="text-sm text-muted-foreground">
                          Synced: {new Date(i.last_sync_at).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="transactions" className="space-y-4">
          {transactions.length === 0 ? (
            <EmptyState
              title="No transactions"
              description="Your marketplace transactions will appear here"
              icon={Store}
            />
          ) : (
            <div className="space-y-2">
              {transactions.map((t) => (
                <Card key={t.id}>
                  <CardContent className="flex justify-between items-center py-4">
                    <div className="flex items-center gap-4">
                      <Store className="h-6 w-6 text-muted-foreground" />
                      <div>
                        <p className="font-medium">{t.transaction_type}</p>
                        <p className="text-sm text-muted-foreground">
                          {new Date(t.created_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold">
                        ${t.amount.toFixed(2)} {t.currency}
                      </span>
                      <Badge
                        variant={
                          t.status === "completed"
                            ? "default"
                            : t.status === "pending"
                              ? "secondary"
                              : "destructive"
                        }
                      >
                        {t.status}
                      </Badge>
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

export default MarketplacePage;
