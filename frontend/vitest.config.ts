import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: ["./vitest.setup.ts"],
  },
  resolve: {
    // Mirrors the "@/*" -> "./src/*" alias from tsconfig.json
    alias: { "@": path.resolve(__dirname, "./src") },
  },
});