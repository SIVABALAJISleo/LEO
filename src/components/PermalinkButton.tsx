// Copy a self-contained permalink encoding thresholds, health history,
// CORS result, SSE config, and sseLog so operators can reproduce the same
// debugging state on another machine.
import { toast } from "sonner";
import { buildPermalinkUrl } from "@/lib/permalink";

export function PermalinkButton() {
  async function copy() {
    try {
      const url = buildPermalinkUrl();
      await navigator.clipboard.writeText(url);
      const len = url.length;
      toast.success(`Permalink copied (${len.toLocaleString()} chars)`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Copy failed");
    }
  }
  return (
    <button
      type="button"
      onClick={copy}
      title="Copy a URL that restores current thresholds, health history, CORS result, SSE settings, and sseLog"
      className="border border-border px-3 py-1.5 text-xs font-semibold hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
    >
      Copy permalink
    </button>
  );
}
