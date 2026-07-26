import { useState, useMemo } from "react";
import { Cpu, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ModuleFilters } from "@/components/modules/ModuleFilters";
import { ModuleCard } from "@/components/modules/ModuleCard";
import { ConfigureModal } from "@/components/modules/ConfigureModal";
import { StatsDrawer } from "@/components/modules/StatsDrawer";
import { BatchActions } from "@/components/modules/BatchActions";
import { useModulesData, ModuleData } from "@/hooks/useModulesData";
import { useToast } from "@/hooks/use-toast";

export default function ModulesPage() {
  const { toast } = useToast();
  const {
    modules,
    loading,
    error,
    refetch,
    toggleModuleEnabled,
    batchToggleModules,
    applySettingsTemplate,
  } = useModulesData();

  // Filter & Sort state
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sortBy, setSortBy] = useState("name");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  // Selection state
  const [selectedModules, setSelectedModules] = useState<Set<string>>(new Set());

  // Modal/Drawer state
  const [configureModule, setConfigureModule] = useState<ModuleData | null>(null);
  const [statsModule, setStatsModule] = useState<ModuleData | null>(null);

  // Filter and sort modules
  const filteredModules = useMemo(() => {
    let result = [...modules];

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        (m) => m.name.toLowerCase().includes(query) || m.description.toLowerCase().includes(query),
      );
    }

    // Status filter
    if (statusFilter !== "all") {
      result = result.filter((m) => {
        const status = m.status?.status?.toLowerCase() || "idle";
        return status === statusFilter.toLowerCase();
      });
    }

    // Sort
    result.sort((a, b) => {
      let comparison = 0;
      switch (sortBy) {
        case "name":
          comparison = a.name.localeCompare(b.name);
          break;
        case "health":
          comparison = (a.status?.health_score ?? 100) - (b.status?.health_score ?? 100);
          break;
        case "speedup":
          comparison = (a.config?.speedup_achieved ?? 0) - (b.config?.speedup_achieved ?? 0);
          break;
        case "compression":
          comparison =
            (a.config?.compression_ratio_achieved ?? 0) -
            (b.config?.compression_ratio_achieved ?? 0);
          break;
      }
      return sortOrder === "asc" ? comparison : -comparison;
    });

    return result;
  }, [modules, searchQuery, statusFilter, sortBy, sortOrder]);

  const handleSelectModule = (moduleName: string, selected: boolean) => {
    setSelectedModules((prev) => {
      const newSet = new Set(prev);
      if (selected) {
        newSet.add(moduleName);
      } else {
        newSet.delete(moduleName);
      }
      return newSet;
    });
  };

  const handleClearSelection = () => {
    setSelectedModules(new Set());
  };

  const handleBatchEnable = async () => {
    await batchToggleModules(Array.from(selectedModules), true);
    handleClearSelection();
  };

  const handleBatchDisable = async () => {
    await batchToggleModules(Array.from(selectedModules), false);
    handleClearSelection();
  };

  const handleApplyTemplate = async () => {
    // Example template - balanced settings
    const template = {
      auto_tune: true,
      optimization_level: 2,
      cache_enabled: true,
    };
    await applySettingsTemplate(Array.from(selectedModules), template);
    handleClearSelection();
    toast({
      title: "Template Applied",
      description: "Balanced settings applied to selected modules.",
    });
  };

  if (error) {
    return (
      <div className="p-6 text-center">
        <p className="text-destructive mb-4">{error}</p>
        <Button onClick={refetch}>Retry</Button>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded-lg">
            <Cpu className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-foreground">GPU Modules</h1>
            <p className="text-sm text-muted-foreground">
              Manage and configure optimization modules
            </p>
          </div>
        </div>
        <Button variant="outline" onClick={refetch} disabled={loading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {/* Filters */}
      <ModuleFilters
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        statusFilter={statusFilter}
        onStatusFilterChange={setStatusFilter}
        sortBy={sortBy}
        onSortByChange={setSortBy}
        sortOrder={sortOrder}
        onSortOrderToggle={() => setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"))}
      />

      {/* Batch Actions */}
      <BatchActions
        selectedCount={selectedModules.size}
        onEnableAll={handleBatchEnable}
        onDisableAll={handleBatchDisable}
        onApplyTemplate={handleApplyTemplate}
        onClearSelection={handleClearSelection}
      />

      {/* Module Grid */}
      {loading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-80 rounded-lg" />
          ))}
        </div>
      ) : filteredModules.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          <Cpu className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>No modules found matching your criteria.</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredModules.map((module) => (
            <ModuleCard
              key={module.name}
              module={module}
              isSelected={selectedModules.has(module.name)}
              onSelect={(selected) => handleSelectModule(module.name, selected)}
              onToggleEnabled={(enabled) => toggleModuleEnabled(module.name, enabled)}
              onConfigure={() => setConfigureModule(module)}
              onViewStats={() => setStatsModule(module)}
            />
          ))}
        </div>
      )}

      {/* Configure Modal */}
      <ConfigureModal
        module={configureModule}
        open={!!configureModule}
        onOpenChange={(open) => !open && setConfigureModule(null)}
      />

      {/* Stats Drawer */}
      <StatsDrawer
        module={statsModule}
        open={!!statsModule}
        onOpenChange={(open) => !open && setStatsModule(null)}
      />
    </div>
  );
}
