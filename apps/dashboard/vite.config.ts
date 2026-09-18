import {defineConfig} from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes("node_modules/zrender")) return "zrender";
          if (id.includes("node_modules/echarts")) return "charts";
          if (id.includes("node_modules/react")) return "react";
        },
      },
    },
  },
});
