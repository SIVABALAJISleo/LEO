import { z } from "zod";

// Polyfill prefault method on ZodType prototype if using Zod v3 with TanStack Start v1.171+
if (typeof (z.ZodType.prototype as any).prefault !== "function") {
  (z.ZodType.prototype as any).prefault = function (defaultValue: any) {
    return this.default(defaultValue);
  };
}

import { defineConfig } from "@lovable.dev/vite-tanstack-config";

export default defineConfig({
  nitro: { preset: process.env.NITRO_PRESET || "vercel" },
  tanstackStart: {
    // Redirect TanStack Start's bundled server entry to src/server.ts (our SSR error wrapper).
    server: { entry: "server" },
  },
  vite: {
    resolve: {
      tsconfigPaths: true,
    },
    build: {
      chunkSizeWarningLimit: 1000,
      rollupOptions: {
        output: {
          manualChunks(id) {
            if (id.includes("node_modules")) {
              if (
                id.includes("react") ||
                id.includes("react-dom") ||
                id.includes("@tanstack/react-router")
              ) {
                return "vendor";
              }
              if (id.includes("recharts")) {
                return "charts";
              }
              if (id.includes("zod") || id.includes("react-hook-form")) {
                return "forms";
              }
              if (id.includes("framer-motion")) {
                return "motion";
              }
            }
          },
        },
      },
    },
  },
});
