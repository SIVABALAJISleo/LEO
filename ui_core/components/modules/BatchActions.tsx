import { Power, PowerOff, Copy, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";

interface BatchActionsProps {
  selectedCount: number;
  onEnableAll: () => void;
  onDisableAll: () => void;
  onApplyTemplate: () => void;
  onClearSelection: () => void;
}

export function BatchActions({
  selectedCount,
  onEnableAll,
  onDisableAll,
  onApplyTemplate,
  onClearSelection,
}: BatchActionsProps) {
  if (selectedCount === 0) return null;

  return (
    <div className="flex items-center gap-3 p-4 bg-primary/10 border border-primary/30 rounded-lg animate-in slide-in-from-top-2">
      <Badge variant="secondary" className="text-sm">
        {selectedCount} selected
      </Badge>

      <div className="flex items-center gap-2 flex-1">
        <Button
          variant="outline"
          size="sm"
          onClick={onEnableAll}
          className="text-green-400 border-green-500/30 hover:bg-green-500/20"
        >
          <Power className="h-4 w-4 mr-1.5" />
          Enable All
        </Button>

        <Button
          variant="outline"
          size="sm"
          onClick={onDisableAll}
          className="text-red-400 border-red-500/30 hover:bg-red-500/20"
        >
          <PowerOff className="h-4 w-4 mr-1.5" />
          Disable All
        </Button>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm">
              <Copy className="h-4 w-4 mr-1.5" />
              Apply Template
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            <DropdownMenuItem onClick={onApplyTemplate}>High Performance Template</DropdownMenuItem>
            <DropdownMenuItem onClick={onApplyTemplate}>Memory Optimized Template</DropdownMenuItem>
            <DropdownMenuItem onClick={onApplyTemplate}>Balanced Template</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <Button variant="ghost" size="icon" onClick={onClearSelection} className="shrink-0">
        <X className="h-4 w-4" />
      </Button>
    </div>
  );
}
