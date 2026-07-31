import { z } from "zod";

// Polyfill prefault method on ZodType prototype if using Zod v3 with TanStack Start v1.171+
/* eslint-disable @typescript-eslint/no-explicit-any */
if (typeof (z.ZodType.prototype as any).prefault !== "function") {
  (z.ZodType.prototype as any).prefault = function (defaultValue: any) {
    return this.default(defaultValue);
  };
}
/* eslint-enable @typescript-eslint/no-explicit-any */

import { defineConfig } from "@lovable.dev/vite-tanstack-config";

export default defineConfig({
  nitro: false,
  tanstackStart: {
    // Redirect TanStack Start's bundled server entry to src/server.ts (our SSR error wrapper).
    server: { entry: "server" },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ["react", "react-dom", "@tanstack/react-router"],
          charts: ["recharts"],
          forms: ["zod", "react-hook-form"],
          motion: ["framer-motion"],
        },
      },
    },
  },
});
