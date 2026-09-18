# Dashboard V1

The React/TypeScript/Vite application uses ECharts as its only charting library. It reads company labels and all analytical values through FastAPI. Its eleven pages cover Home, Sales Overview, Brand/Product, Store/Outlet, Forecast, Stockout Risk, Segments, Anomaly Review, Basket Insights, Promotions and Model Catalog. Sales pages use DuckDB-backed API queries; offline analytical pages use bounded API pagination over canonical outputs; model pages expose frozen metadata without fabricating future results. Empty/loading/error states and scientific caveats are explicit. No profit, causal ROI, fake AI assistant, or direct database/Parquet access is presented.

The information architecture was conceptually inspired by [Chad Lines' Coca-Cola visualization explanation](https://github.com/Chad-Lines/Data-Projects/blob/main/Coca-Cola%20Sales%20Data%20Visualiation/Project%20Explanation.md). No code, screenshots, layout, logo or proprietary assets were copied.

Development: `cd apps/dashboard`, `npm ci`, `npm run dev`. Production check: `npm test`, `npm run build`, `npm audit --audit-level=high`. Docker: `docker compose --profile core up -d --build`.

Limitations: global cross-page dimension filters are not implemented, and the current single ECharts bundle exceeds Vite's preferred 500 kB chunk threshold. These are product-UX/performance gaps, not scientific blockers.
