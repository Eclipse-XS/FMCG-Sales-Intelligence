# Dashboard V1.1

Sales pages share one filter state for inclusive `date_from`/`date_to`, region, channel, store, category, brand, SKU and promotion status. The backend provides bounded values at `/api/v1/analytics/filters`; typed query parsing, cardinality limits and parameterized DuckDB queries protect the boundary. State persists across page navigation and in URL query parameters. Clear All restores the unfiltered state.

Home, Sales Overview, Brand/Product and Store/Outlet support the filters. Frozen model metadata and versioned offline artifacts do not share the sales mart grain; the UI explicitly marks global sales filters not applicable rather than silently ignoring them. Brand and store pages provide supported contribution drilldowns. All results remain descriptive historical analytics.

V1.1 uses a lazy dashboard entry, modular ECharts imports and explicit React/ECharts/zrender chunks. Build change: the V1 entry was 1,341.16 kB (447.57 kB gzip); V1.1 emits a 2.33 kB entry, 9.26 kB dashboard chunk, 185.29 kB React chunk, 360.59 kB ECharts chunk and 175.93 kB zrender chunk, with no chunk above 500 kB.

Visible caveats remain: forecast and stockout targets are `(t,t+7d]`; segments are exploratory; anomaly candidates are unreviewed; basket rules are associations; promotion comparisons are descriptive and non-causal. Freshness and model version metadata are exposed without fabricated live data.
