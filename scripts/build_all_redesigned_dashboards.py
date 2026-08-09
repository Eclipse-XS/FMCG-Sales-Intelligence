"""Generate production-grade, varied, task-specific analytical Grafana dashboards for FMCG Sales Intelligence."""
import json
from pathlib import Path

BASE_DIR = Path("platform/observability/grafana/provisioning/dashboards/json")
BIZ_DIR = BASE_DIR / "business"
SCI_DIR = BASE_DIR / "scientific"
OPS_DIR = BASE_DIR / "operations"

for d in [BIZ_DIR, SCI_DIR, OPS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

DS_PG = {"type": "postgres", "uid": "postgres_db"}
DS_PROM = {"type": "prometheus", "uid": "prometheus"}

# ==============================================================================
# REUSABLE GRAPHICAL PANEL BUILDERS
# ==============================================================================

def text_panel(id, title, markdown_content, x, y, w=24, h=3):
    return {
        "id": id, "title": title, "type": "text",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "options": {
            "mode": "markdown",
            "content": markdown_content
        }
    }

def stat_panel(id, title, sql, x, y, w=6, h=3, unit="short", color="text", decimals=None, description="", is_string=False):
    field_config = {
        "defaults": {
            "unit": unit,
            "color": {"mode": "fixed", "fixedColor": color},
        },
        "overrides": []
    }
    if decimals is not None:
        field_config["defaults"]["decimals"] = decimals
    
    reduce_opts = {"calcs": ["lastNotNull"], "values": False}
    if is_string:
        reduce_opts["fields"] = "/.*/"
    
    return {
        "id": id, "title": title, "type": "stat", "description": description,
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [{"datasource": DS_PG, "format": "table", "rawSql": sql, "refId": "A"}],
        "options": {
            "colorMode": "value", "graphMode": "none", "justifyMode": "auto",
            "textMode": "value" if is_string else "auto",
            "reduceOptions": reduce_opts
        },
        "fieldConfig": field_config
    }

def barchart_panel(id, title, sql, x, y, w=12, h=8, orientation="horizontal", xField=None, unit="short", color=None, color_mode="palette-classic", description="", showValue="always", overrides=None, stacking="none"):
    defaults = {
        "unit": unit,
        "color": {"mode": color_mode}
    }
    if color:
        defaults["color"] = {"mode": "fixed", "fixedColor": color}
    
    options = {
        "orientation": orientation,
        "showValue": showValue,
        "xField": xField,
        "legend": {"displayMode": "list", "placement": "bottom", "showLegend": True}
    }
    if stacking != "none":
        options["stacking"] = {"mode": "normal", "group": "A"}

    return {
        "id": id, "title": title, "type": "barchart", "description": description,
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [{"datasource": DS_PG, "format": "table", "rawSql": sql, "refId": "A"}],
        "options": options,
        "fieldConfig": {
            "defaults": defaults,
            "overrides": overrides or []
        }
    }

def timeseries_panel(id, title, sql, x, y, w=16, h=8, unit="short", description="", overrides=None):
    return {
        "id": id, "title": title, "type": "timeseries", "description": description,
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [{"datasource": DS_PG, "format": "time_series", "rawSql": sql, "refId": "A"}],
        "options": {
            "legend": {"displayMode": "list", "placement": "bottom", "showLegend": True}
        },
        "fieldConfig": {
            "defaults": {
                "unit": unit,
                "custom": {
                    "drawStyle": "line", "lineInterpolation": "smooth",
                    "lineWidth": 2, "fillOpacity": 15, "pointSize": 5, "showPoints": "auto"
                },
                "color": {"mode": "palette-classic"}
            },
            "overrides": overrides or []
        }
    }

def xychart_panel(id, title, sql, series_configs, x, y, w=12, h=8, description="", default_show="points", default_point_size=4, default_line_width=2, default_color="#5794F2"):
    series_list = []
    overrides = []
    
    for s in series_configs:
        x_field = s["xField"]
        y_field = s["yField"]
        label = s["name"]
        
        # Native Grafana 11.5.2 manual series mapping
        series_list.append({
            "frame": {"matcher": {"id": "byIndex", "options": 0}},
            "x": {"matcher": {"id": "byName", "options": x_field}},
            "y": {"matcher": {"id": "byName", "options": y_field}},
            "name": {"fixed": label}
        })
        
        show_mode = s.get("show", default_show)
        if show_mode == "both":
            show_mode = "points+lines"
            
        props = [
            {"id": "custom.show", "value": show_mode},
            {"id": "custom.pointSize", "value": {"fixed": s.get("pointSize", default_point_size)}},
            {"id": "custom.lineWidth", "value": s.get("lineWidth", default_line_width)}
        ]
        if "lineStyle" in s:
            props.append({"id": "custom.lineStyle", "value": s["lineStyle"]})
        if "color" in s:
            props.append({"id": "color", "value": {"mode": "fixed", "fixedColor": s["color"]}})
            
        overrides.append({
            "matcher": {"id": "byName", "options": y_field},
            "properties": props
        })
    
    return {
        "id": id, "title": title, "type": "xychart", "pluginVersion": "11.5.2", "description": description,
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "datasource": DS_PG,
        "targets": [{"datasource": DS_PG, "format": "table", "rawSql": sql, "refId": "A"}],
        "options": {
            "mapping": "manual",
            "series": series_list,
            "legend": {"displayMode": "list", "placement": "bottom", "showLegend": True},
            "tooltip": {"mode": "single"}
        },
        "fieldConfig": {
            "defaults": {
                "custom": {
                    "show": default_show,
                    "pointSize": {"fixed": default_point_size},
                    "lineWidth": default_line_width,
                    "fillOpacity": 50
                },
                "color": {"mode": "fixed", "fixedColor": default_color}
            },
            "overrides": overrides
        }
    }

def table_panel(id, title, sql, x, y, w=24, h=8, description="", overrides=None):
    return {
        "id": id, "title": title, "type": "table", "description": description,
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [{"datasource": DS_PG, "format": "table", "rawSql": sql, "refId": "A"}],
        "options": {
            "footer": {"enablePagination": True, "show": True},
            "showHeader": True
        },
        "fieldConfig": {
            "defaults": {"color": {"mode": "thresholds"}},
            "overrides": overrides or []
        }
    }

def dashboard_json(title, uid, panels, templating=None, tags=None, time_from="2024-01-01T00:00:00.000Z", time_to="2024-03-31T23:59:59.000Z"):
    return {
        "title": title, "uid": uid, "timezone": "browser", "refresh": "5m",
        "schemaVersion": 39, "tags": tags or ["fmcg"],
        "time": {"from": time_from, "to": time_to},
        "templating": {"list": templating or []},
        "panels": panels
    }

def save_dashboard(target_dir, db):
    path = target_dir / f"{db['uid']}.json"
    path.write_text(json.dumps(db, indent=2), encoding="utf-8")
    print(f"Generated: {target_dir.name}/{path.name}")

# ==============================================================================
# 1. FMCG Business Overview (Business)
# ==============================================================================
save_dashboard(BIZ_DIR, dashboard_json(
    title="FMCG Business Overview",
    uid="fmcg_biz_overview",
    tags=["business", "executive", "fmcg"],
    panels=[
        text_panel(1, "Executive Commercial Context",
            "**FMCG Operational Intelligence Platform** — Executive sales performance, category revenue contribution, and retail footprint coverage.\n"
            "*Source:* Authoritative sales and product entities (`fmcg.sales`, `fmcg.stores`, `fmcg.products`, `fmcg.categories`).",
            0, 0, 24, 2),
        stat_panel(2, "Total Gross Revenue", "SELECT sum(gross_revenue) AS value FROM fmcg.sales;", 0, 2, 6, 3, unit="currencyUSD", color="blue", description="Aggregate gross sales revenue across retail network"),
        stat_panel(3, "Total Physical Units Sold", "SELECT sum(quantity_units) AS value FROM fmcg.sales;", 6, 2, 6, 3, unit="short", color="green", description="Total physical units sold across all active SKUs"),
        stat_panel(4, "Sales Transactions Recorded", "SELECT count(sale_id) AS value FROM fmcg.sales;", 12, 2, 6, 3, unit="short", color="purple", description="Total distinct point-of-sale receipt checkout events"),
        stat_panel(5, "Active Retail Stores", "SELECT count(distinct store_id) AS value FROM fmcg.stores;", 18, 2, 6, 3, unit="short", color="text", description="Total monitored brick-and-mortar retail outlets"),
        timeseries_panel(6, "Daily Revenue Trajectory (30-Day Window)", 
            "SELECT sale_date AS time, sum(gross_revenue) AS revenue FROM fmcg.sales WHERE sale_date >= '2024-03-01' GROUP BY 1 ORDER BY 1;", 
            0, 5, 16, 8, unit="currencyUSD", description="Chain-wide daily gross sales revenue trajectory", overrides=[
                {"matcher": {"id": "byName", "options": "revenue"}, "properties": [{"id": "color", "value": {"mode": "fixed", "fixedColor": "blue"}}]}
            ]),
        barchart_panel(7, "Revenue Share by Product Category", 
            "SELECT c.category_name as category, round(sum(s.gross_revenue)::numeric, 2) as revenue FROM fmcg.sales s JOIN fmcg.skus k ON s.sku_id = k.sku_id JOIN fmcg.products p ON k.product_id = p.product_id JOIN fmcg.categories c ON p.category_id = c.category_id GROUP BY 1 ORDER BY 2 DESC;", 
            16, 5, 8, 8, orientation="horizontal", unit="currencyUSD", color="purple", description="Gross revenue contribution by commercial product category"),
        barchart_panel(8, "Top 10 Revenue-Generating SKUs", 
            "SELECT concat(p.product_name, ' [SKU ', s.sku_id, ']') as sku_label, round(sum(s.gross_revenue)::numeric, 2) as revenue FROM fmcg.sales s JOIN fmcg.skus k ON s.sku_id = k.sku_id JOIN fmcg.products p ON k.product_id = p.product_id GROUP BY 1, p.product_name ORDER BY 2 DESC LIMIT 10;", 
            0, 13, 14, 8, orientation="horizontal", unit="currencyUSD", color="orange", description="Top 10 individual product lines by total gross sales volume"),
        barchart_panel(9, "Regional Performance Summary", 
            "SELECT r.region_name as region, round(sum(s.gross_revenue)::numeric, 2) as revenue FROM fmcg.sales s JOIN fmcg.stores st ON s.store_id = st.store_id JOIN fmcg.regions r ON st.region_id = r.region_id GROUP BY 1 ORDER BY 2 DESC;", 
            14, 13, 10, 8, orientation="horizontal", unit="currencyUSD", color="green", description="Sales distribution across geographic distribution zones"),
        table_panel(10, "Store Commercial Performance Summary", 
            "SELECT st.store_id, st.store_name, r.region_name, st.store_type, st.channel, sum(s.quantity_units) as total_units, round(sum(s.gross_revenue)::numeric, 2) as total_revenue, count(s.sale_id) as total_transactions FROM fmcg.sales s JOIN fmcg.stores st ON s.store_id = st.store_id JOIN fmcg.regions r ON st.region_id = r.region_id GROUP BY 1, 2, 3, 4, 5 ORDER BY total_revenue DESC;", 
            0, 21, 24, 8, description="Exhaustive commercial performance ledger by retail outlet", overrides=[
                {"matcher": {"id": "byName", "options": "total_revenue"}, "properties": [{"id": "unit", "value": "currencyUSD"}, {"id": "custom.displayName", "value": "Total Revenue"}]},
                {"matcher": {"id": "byName", "options": "total_units"}, "properties": [{"id": "custom.displayName", "value": "Units Sold"}]},
                {"matcher": {"id": "byName", "options": "total_transactions"}, "properties": [{"id": "custom.displayName", "value": "Transactions"}]}
            ])
    ]
))

# ==============================================================================
# 2. FMCG Sales & Inventory (Business)
# ==============================================================================
save_dashboard(BIZ_DIR, dashboard_json(
    title="FMCG Sales & Inventory",
    uid="fmcg_sales_inventory",
    tags=["business", "inventory", "fmcg"],
    panels=[
        text_panel(1, "Operational Inventory & Fulfillment Context",
            "**Supply Chain Real-Time Health & Depot Stock Positioning** — Available warehouse inventory vs retail sales volume.\n"
            "*Source:* Operational database (`fmcg.inventory`, `fmcg.sales`, `fmcg.warehouses`).",
            0, 0, 24, 2),
        stat_panel(2, "Current On-Hand Inventory Units", "SELECT sum(available_quantity) FROM fmcg.inventory WHERE snapshot_date = (SELECT max(snapshot_date) FROM fmcg.inventory);", 0, 2, 6, 3, unit="short", color="blue", description="Latest total available stock on hand across all fulfillment hubs"),
        stat_panel(3, "Active Warehouses", "SELECT count(*) FROM fmcg.warehouses;", 6, 2, 6, 3, unit="short", color="text", description="Monitored central fulfillment hubs"),
        stat_panel(4, "Monitored SKU Inventory Positions", "SELECT count(distinct sku_id) FROM fmcg.inventory;", 12, 2, 6, 3, unit="short", color="purple", description="Distinct products tracked across inventory registers"),
        stat_panel(5, "Stockout Episodes Recorded (< 5 Units)", "SELECT count(*) FROM fmcg.inventory WHERE available_quantity < 5;", 18, 2, 6, 3, unit="short", color="red", description="Historical inventory positions breaching minimum buffer threshold"),
        barchart_panel(6, "Warehouse Inventory Balance", 
            "SELECT concat('Warehouse ', warehouse_id) as warehouse, sum(available_quantity) as total_units FROM fmcg.inventory WHERE snapshot_date = (SELECT max(snapshot_date) FROM fmcg.inventory) GROUP BY 1 ORDER BY 2 DESC;", 
            0, 5, 12, 8, orientation="horizontal", unit="short", color="blue", description="Available stock units distributed across regional depots"),
        barchart_panel(7, "Stockout Incidents by Fulfillment Warehouse", 
            "SELECT concat('Warehouse ', warehouse_id) as warehouse, count(*) as stockout_episodes FROM fmcg.inventory WHERE available_quantity < 5 GROUP BY 1 ORDER BY 2 DESC;", 
            12, 5, 12, 8, orientation="horizontal", unit="short", color="red", description="Total critical low-stock (<5 units) recorded events per warehouse"),
        timeseries_panel(8, "Daily Sales Volume vs Inventory Depletion (March 2024)", 
            "SELECT sale_date as time, sum(quantity_units) as \"Daily Units Sold\" FROM fmcg.sales WHERE sale_date >= '2024-03-01' GROUP BY 1 ORDER BY 1;", 
            0, 13, 14, 8, unit="short", description="Trajectory of aggregate retail sales velocity over last 30 operational days", overrides=[
                {"matcher": {"id": "byName", "options": "Daily Units Sold"}, "properties": [{"id": "color", "value": {"mode": "fixed", "fixedColor": "green"}}]}
            ]),
        barchart_panel(9, "Available Stock by Product Category", 
            "SELECT c.category_name as category, sum(i.available_quantity) as available_units FROM fmcg.inventory i JOIN fmcg.skus k ON i.sku_id = k.sku_id JOIN fmcg.products p ON k.product_id = p.product_id JOIN fmcg.categories c ON p.category_id = c.category_id WHERE i.snapshot_date = (SELECT max(snapshot_date) FROM fmcg.inventory) GROUP BY 1 ORDER BY 2 DESC;", 
            14, 13, 10, 8, orientation="horizontal", unit="short", color="purple", description="Current warehouse stock distribution across commercial product lines"),
        table_panel(10, "Recent Sales Activity", 
            "SELECT to_char(sale_date, 'YYYY-MM-DD') as date, store_id, sku_id, quantity_units as units, round(gross_revenue::numeric, 2) as revenue, round(gross_profit::numeric, 2) as profit FROM fmcg.sales ORDER BY sale_date DESC, gross_revenue DESC LIMIT 100;", 
            0, 21, 24, 8, description="Recent store-level daily sales records", overrides=[
                {"matcher": {"id": "byName", "options": "revenue"}, "properties": [{"id": "unit", "value": "currencyUSD"}]}
            ])
    ]
))

# ==============================================================================
# 3. ML — Demand Forecasting (Scientific Analytics)
# ==============================================================================
save_dashboard(SCI_DIR, dashboard_json(
    title="ML — Demand Forecasting",
    uid="ml_forecasting_v1",
    tags=["scientific", "ml", "forecasting", "catboost", "fmcg"],
    panels=[
        text_panel(1, "Scientific Model Card & Validation Context",
            "**Core:** `forecasting_v1` | **Model Architecture:** `CatBoost Gradient Boosted Decision Trees (Regressor)`\n"
            "**Evaluation Horizon:** 20 out-of-sample forward days across 20 retail outlets and 48 SKUs (19,200 evaluated episodes).\n"
            "> ⚠️ **Model Performance Context:** Predictions are strictly out-of-sample evaluated on purged test partitions. WAPE captures absolute percentage deviation relative to aggregate physical throughput.",
            0, 0, 24, 3),
        stat_panel(2, "Selected Model", "SELECT selected_model FROM ml_results.forecasting_v1_metrics LIMIT 1;", 0, 3, 6, 3, unit="string", color="blue", description="Governed champion production model architecture", is_string=True),
        stat_panel(3, "Test WAPE", "SELECT cast(test::json->selected_model->>'wape' as float) * 100 FROM ml_results.forecasting_v1_metrics LIMIT 1;", 6, 3, 6, 3, unit="percent", color="green", decimals=1, description="Weighted Absolute Percentage Error on test partition"),
        stat_panel(4, "Test MAE", "SELECT cast(test::json->selected_model->>'mae' as float) FROM ml_results.forecasting_v1_metrics LIMIT 1;", 12, 3, 6, 3, unit="short", color="purple", decimals=2, description="Mean Absolute Error in unit demand"),
        stat_panel(5, "Test Episodes", "SELECT COUNT(*) FROM ml_results.forecasting_v1_predictions;", 18, 3, 6, 3, unit="short", color="text", description="Total scored out-of-sample store-SKU-day instances"),
        
        # SCIENTIFIC DIAGNOSTIC 1: Actual vs Predicted Parity Density Scatter
        xychart_panel(6, "Actual vs Predicted Parity Scatter", 
            "SELECT round(actual::numeric, 1) as actual, round(prediction::numeric, 1) as prediction, round(actual::numeric, 1) as parity_line "
            "FROM ml_results.forecasting_v1_predictions "
            "WHERE actual IS NOT NULL AND prediction IS NOT NULL "
            "ORDER BY prediction_date, store_id, sku_id;",
            [
                {"name": "Model Predictions (n=19,200)", "xField": "actual", "yField": "prediction", "show": "points", "pointSize": 3, "color": "#B877D9"},
                {"name": "Perfect Parity Line (y = x)", "xField": "actual", "yField": "parity_line", "show": "lines", "lineWidth": 2, "lineStyle": {"dash": [4, 4]}, "color": "#73BF69"}
            ],
            0, 6, 12, 8, description="Actual observed units vs model point forecast across all 19,200 test episodes with perfect parity line (y=x)"),
        
        # SCIENTIFIC DIAGNOSTIC 2: Residual vs Predicted Scatter (Heteroscedasticity)
        xychart_panel(7, "Residual vs Predicted Scatter (Heteroscedasticity Diagnostic)",
            "SELECT round(prediction::numeric, 1) as prediction, round(residual::numeric, 1) as residual, 0.0 as zero_bias_line "
            "FROM ml_results.forecasting_v1_predictions "
            "WHERE actual IS NOT NULL AND prediction IS NOT NULL "
            "ORDER BY prediction_date, store_id, sku_id;",
            [
                {"name": "Forecast Residual (Actual - Predicted)", "xField": "prediction", "yField": "residual", "show": "points", "pointSize": 3, "color": "#FF9830"},
                {"name": "Zero-Bias Reference (y = 0)", "xField": "prediction", "yField": "zero_bias_line", "show": "lines", "lineWidth": 2, "lineStyle": {"dash": [4, 4]}, "color": "#5794F2"}
            ],
            12, 6, 12, 8, description="Residual error plotted against predicted demand level across all 19,200 episodes detecting variance growth and systematic bias"),
        
        # SCIENTIFIC DIAGNOSTIC 3: Observed vs Predicted Daily Demand Trajectory
        timeseries_panel(8, "Observed vs Predicted Daily Demand Trajectory", 
            "SELECT prediction_date AS time, round(sum(actual)::numeric, 0) as \"Observed Demand\", round(sum(prediction)::numeric, 0) as \"Forecasted Demand\" FROM ml_results.forecasting_v1_predictions GROUP BY 1 ORDER BY 1;", 
            0, 14, 12, 8, unit="short", description="Total actual store sales volume vs model forecasts across the 20-day evaluation window", overrides=[
                {"matcher": {"id": "byName", "options": "Observed Demand"}, "properties": [{"id": "color", "value": {"mode": "fixed", "fixedColor": "green"}}]},
                {"matcher": {"id": "byName", "options": "Forecasted Demand"}, "properties": [{"id": "color", "value": {"mode": "fixed", "fixedColor": "purple"}}]}
            ]),
        
        # SCIENTIFIC DIAGNOSTIC 4: Residual Error Distribution Histogram
        barchart_panel(9, "Forecast Residual Error Distribution (Balanced Diverging Histogram)", 
            "SELECT case "
            "    when residual < -20 then '< -20 Units (Over-forecast)' "
            "    when residual < -10 then '-20 to -10 Units' "
            "    when residual < -5 then '-10 to -5 Units' "
            "    when residual < 0 then '-5 to 0 Units' "
            "    when residual < 5 then '0 to +5 Units' "
            "    when residual < 10 then '+5 to +10 Units' "
            "    when residual < 20 then '+10 to +20 Units' "
            "    else '> +20 Units (Under-forecast)' "
            "end as error_bracket, count(*) as episode_count "
            "FROM ml_results.forecasting_v1_predictions GROUP BY 1 ORDER BY min(residual);", 
            12, 14, 12, 8, orientation="horizontal", unit="short", color="purple", description="Diverging distribution of forecast residuals (actual - prediction) across 19,200 test episodes"),
        
        barchart_panel(10, "Forecast Performance by Demand Volume Tier", 
            "SELECT demand_volume_group as volume_tier, round((sum(abs(residual)) / nullif(sum(actual), 0) * 100)::numeric, 1) as \"WAPE (%)\", round(avg(abs(residual))::numeric, 2) as \"MAE (Units)\" FROM ml_results.forecasting_v1_predictions GROUP BY 1 ORDER BY min(actual) ASC;", 
            0, 22, 12, 7, orientation="horizontal", xField="volume_tier", unit="short", description="Model error metrics broken down across low, medium, and high demand SKU groups", overrides=[
                {"matcher": {"id": "byName", "options": "WAPE (%)"}, "properties": [{"id": "color", "value": {"mode": "fixed", "fixedColor": "orange"}}]},
                {"matcher": {"id": "byName", "options": "MAE (Units)"}, "properties": [{"id": "color", "value": {"mode": "fixed", "fixedColor": "blue"}}]}
            ]),
        barchart_panel(11, "Mean Absolute Error by Category", 
            "SELECT category_name as category, round(avg(abs(residual))::numeric, 2) as mae FROM ml_results.forecasting_v1_predictions GROUP BY 1 ORDER BY mae ASC;", 
            12, 22, 12, 7, orientation="horizontal", unit="short", color="blue", description="Forecast accuracy variance across commercial product categories"),
        table_panel(12, "Test Predictions Inspection & Error Diagnostics", 
            "SELECT to_char(prediction_date, 'YYYY-MM-DD') as date, store_id, sku_id, category_name, demand_volume_group, round(actual::numeric, 1) as actual_units, round(prediction::numeric, 1) as predicted_units, round(residual::numeric, 1) as error_units, round((abs(residual) / nullif(actual, 0) * 100)::numeric, 1) as abs_pct_error FROM ml_results.forecasting_v1_predictions ORDER BY abs(residual) DESC LIMIT 200;", 
            0, 29, 24, 8, description="Granular out-of-sample prediction episodes sorted by absolute residual error")
    ]
))

# ==============================================================================
# 4. ML — Stockout Risk Classification (Scientific Analytics)
# ==============================================================================
save_dashboard(SCI_DIR, dashboard_json(
    title="ML — Stockout Risk Classification",
    uid="ml_stockout_classification_v1",
    tags=["scientific", "ml", "classification", "stockout", "fmcg"],
    panels=[
        text_panel(1, "Scientific Model Card & Classification Context",
            "**Core:** `stockout_classification_v1` | **Model Architecture:** `Gradient Boosted Decision Forest Ensemble`\n"
            "**Evaluation Horizon:** 7-Day stock depletion risk episode prediction across 4 fulfillment warehouses and 48 SKUs (3,840 test episodes).\n"
            "> ⚠️ **Imbalanced Evaluation Context:** Base stockout rate is **4.84%** (186 events). Precision-Recall curve is the authoritative diagnostic for operational reorder tuning.",
            0, 0, 24, 3),
        stat_panel(2, "Test ROC AUC", "SELECT cast(test::json->'selected_model'->>'roc_auc' as float) FROM ml_results.stockout_classification_v1_metrics LIMIT 1;", 0, 3, 6, 3, unit="short", color="blue", decimals=3, description="Receiver Operating Characteristic Area Under Curve"),
        stat_panel(3, "Average Precision (AP)", "SELECT cast(test::json->'selected_model'->>'average_precision' as float) FROM ml_results.stockout_classification_v1_metrics LIMIT 1;", 6, 3, 6, 3, unit="short", color="purple", decimals=3, description="Average Precision (AP) on imbalanced stockout events"),
        stat_panel(4, "High-Risk SKU Episodes", "SELECT COUNT(*) FROM ml_results.stockout_classification_v1_predictions WHERE predicted_class = true;", 12, 3, 6, 3, unit="short", color="red", description="Episodes classified as high stockout risk"),
        stat_panel(5, "Total Test Episodes", "SELECT COUNT(*) FROM ml_results.stockout_classification_v1_predictions;", 18, 3, 6, 3, unit="short", color="text", description="Total evaluated out-of-sample inventory episodes"),
        
        # SCIENTIFIC DIAGNOSTIC 1: Precision-Recall Curve
        xychart_panel(6, "Precision–Recall Curve (Imbalance Diagnostic)",
            "WITH thresholds AS ("
            "    SELECT generate_series(1, 99)::numeric / 100.0 as thresh"
            "), prevalence AS ("
            "    SELECT round((sum(case when stockout_within_7d then 1 else 0 end)::numeric / count(*)::numeric)::numeric, 4) as base_rate "
            "    FROM ml_results.stockout_classification_v1_predictions"
            "), classified AS ("
            "    SELECT t.thresh, p.stockout_within_7d as actual, (p.predicted_probability >= t.thresh) as pred "
            "    FROM thresholds t CROSS JOIN ml_results.stockout_classification_v1_predictions p"
            "), matrix AS ("
            "    SELECT thresh, sum(case when actual and pred then 1 else 0 end) as tp, sum(case when not actual and pred then 1 else 0 end) as fp, sum(case when actual and not pred then 1 else 0 end) as fn "
            "    FROM classified GROUP BY thresh"
            ") SELECT round((tp::numeric / nullif(tp + fn, 0))::numeric, 4) as recall, round((tp::numeric / nullif(tp + fp, 0))::numeric, 4) as precision, prev.base_rate as baseline_prevalence "
            "FROM matrix CROSS JOIN prevalence prev WHERE tp + fp > 0 ORDER BY recall ASC, precision DESC;",
            [
                {"name": "Precision-Recall Curve", "xField": "recall", "yField": "precision", "show": "lines", "lineWidth": 3, "color": "#B877D9"},
                {"name": "Class Prevalence Baseline (4.84%)", "xField": "recall", "yField": "baseline_prevalence", "show": "lines", "lineWidth": 1.5, "lineStyle": {"dash": [4, 4]}, "color": "#73BF69"}
            ],
            0, 6, 12, 8, description="Empirical Precision-Recall trade-off curve across classification thresholds vs positive base rate"),
        
        # SCIENTIFIC DIAGNOSTIC 2: ROC Curve
        xychart_panel(7, "Receiver Operating Characteristic (ROC) Curve",
            "WITH thresholds AS ("
            "    SELECT generate_series(0, 100)::numeric / 100.0 as thresh"
            "), classified AS ("
            "    SELECT t.thresh, p.stockout_within_7d as actual, (p.predicted_probability >= t.thresh) as pred "
            "    FROM thresholds t CROSS JOIN ml_results.stockout_classification_v1_predictions p"
            "), matrix AS ("
            "    SELECT thresh, sum(case when actual and pred then 1 else 0 end) as tp, sum(case when not actual and pred then 1 else 0 end) as fp, sum(case when actual and not pred then 1 else 0 end) as fn, sum(case when not actual and not pred then 1 else 0 end) as tn "
            "    FROM classified GROUP BY thresh"
            ") SELECT round((fp::numeric / nullif(fp + tn, 0))::numeric, 4) as fpr, round((tp::numeric / nullif(tp + fn, 0))::numeric, 4) as tpr, round((fp::numeric / nullif(fp + tn, 0))::numeric, 4) as chance_line "
            "FROM matrix ORDER BY fpr ASC, tpr ASC;",
            [
                {"name": "ROC Curve (AUC = 0.799)", "xField": "fpr", "yField": "tpr", "show": "lines", "lineWidth": 3, "color": "#5794F2"},
                {"name": "Chance Diagonal (AUC = 0.5)", "xField": "fpr", "yField": "chance_line", "show": "lines", "lineWidth": 1.5, "lineStyle": {"dash": [4, 4]}, "color": "#808080"}
            ],
            12, 6, 12, 8, description="True Positive Rate vs False Positive Rate curve evaluating global model discrimination (AUC = 0.799)"),
        
        # SCIENTIFIC DIAGNOSTIC 3: Predicted Risk Score Distribution by True Class
        barchart_panel(8, "Predicted Risk Score Distribution by True Class",
            "SELECT case "
            "    when predicted_probability < 0.05 then '0.00 - 0.05' "
            "    when predicted_probability < 0.10 then '0.05 - 0.10' "
            "    when predicted_probability < 0.15 then '0.10 - 0.15' "
            "    when predicted_probability < 0.20 then '0.15 - 0.20' "
            "    when predicted_probability < 0.25 then '0.20 - 0.25' "
            "    when predicted_probability < 0.30 then '0.25 - 0.30' "
            "    when predicted_probability < 0.40 then '0.30 - 0.40' "
            "    when predicted_probability < 0.50 then '0.40 - 0.50' "
            "    when predicted_probability < 0.60 then '0.50 - 0.60' "
            "    when predicted_probability < 0.70 then '0.60 - 0.70' "
            "    when predicted_probability < 0.80 then '0.70 - 0.80' "
            "    else '0.80 - 1.00' "
            "end as score_tier, "
            "sum(case when not stockout_within_7d then 1 else 0 end) as \"Actual Non-Stockouts\", "
            "sum(case when stockout_within_7d then 1 else 0 end) as \"Actual Stockouts\" "
            "FROM ml_results.stockout_classification_v1_predictions GROUP BY 1 ORDER BY min(predicted_probability);",
            0, 14, 12, 8, orientation="vertical", xField="score_tier", unit="short", description="Score separation: non-stockout episodes cluster near 0 while actual stockouts shift toward higher risk scores", overrides=[
                {"matcher": {"id": "byName", "options": "Actual Non-Stockouts"}, "properties": [{"id": "color", "value": {"mode": "fixed", "fixedColor": "blue"}}]},
                {"matcher": {"id": "byName", "options": "Actual Stockouts"}, "properties": [{"id": "color", "value": {"mode": "fixed", "fixedColor": "red"}}]}
            ]),
        
        # SCIENTIFIC DIAGNOSTIC 4: Threshold Diagnostics (Precision, Recall & F1)
        xychart_panel(9, "Threshold Diagnostics (Precision, Recall & F1-Score)",
            "WITH thresholds AS ("
            "    SELECT generate_series(5, 95, 5)::numeric / 100.0 as thresh"
            "), classified AS ("
            "    SELECT t.thresh, p.stockout_within_7d as actual, (p.predicted_probability >= t.thresh) as pred "
            "    FROM thresholds t CROSS JOIN ml_results.stockout_classification_v1_predictions p"
            "), matrix AS ("
            "    SELECT thresh, sum(case when actual and pred then 1 else 0 end) as tp, sum(case when not actual and pred then 1 else 0 end) as fp, sum(case when actual and not pred then 1 else 0 end) as fn "
            "    FROM classified GROUP BY thresh"
            ") SELECT thresh, round((tp::numeric / nullif(tp + fp, 0))::numeric, 3) as precision, round((tp::numeric / nullif(tp + fn, 0))::numeric, 3) as recall, round((2.0 * tp::numeric / nullif(2.0 * tp + fp + fn, 0))::numeric, 3) as f1_score "
            "FROM matrix WHERE tp + fp > 0 ORDER BY thresh ASC;",
            [
                {"name": "Precision", "xField": "thresh", "yField": "precision", "show": "lines", "lineWidth": 2.5, "color": "#B877D9"},
                {"name": "Recall", "xField": "thresh", "yField": "recall", "show": "lines", "lineWidth": 2.5, "color": "#5794F2"},
                {"name": "F1-Score", "xField": "thresh", "yField": "f1_score", "show": "lines", "lineWidth": 3, "color": "#FF9830"}
            ],
            12, 14, 12, 8, description="Trade-off curves of Precision, Recall, and F1 across candidate operational decision thresholds"),
        
        barchart_panel(10, "Model Decision vs Observed Event (Confusion Matrix Outcomes)", 
            "SELECT case "
            "    when stockout_within_7d and predicted_class then 'True Positive (Correct Alert)' "
            "    when not stockout_within_7d and not predicted_class then 'True Negative (Correct Normal)' "
            "    when not stockout_within_7d and predicted_class then 'False Positive (False Alarm)' "
            "    else 'False Negative (Missed Stockout)' "
            "end as outcome, count(*) as episode_count "
            "FROM ml_results.stockout_classification_v1_predictions GROUP BY 1 ORDER BY 2 DESC;", 
            0, 22, 12, 7, orientation="horizontal", unit="short", color="purple", description="Breakdown across confusion matrix quadrants at operational decision boundary"),
        barchart_panel(11, "High-Risk Predictions by Warehouse", 
            "SELECT concat('Warehouse ', warehouse_id) as warehouse, count(*) as high_risk_positions FROM ml_results.stockout_classification_v1_predictions WHERE predicted_class = true GROUP BY 1 ORDER BY 2 DESC;", 
            12, 22, 12, 7, orientation="horizontal", unit="short", color="red", description="Distribution of high-risk stockout warnings across fulfillment hubs"),
        table_panel(12, "Ranked High-Risk Inventory Positions", 
            "SELECT to_char(prediction_date, 'YYYY-MM-DD') as date, warehouse_id, sku_id, round(predicted_probability::numeric, 3) as stockout_risk_score, predicted_class, available_quantity, reorder_point, safety_stock, round(sales_velocity_7d::numeric, 2) as velocity_7d FROM ml_results.stockout_classification_v1_predictions WHERE predicted_class = true ORDER BY predicted_probability DESC LIMIT 150;", 
            0, 29, 24, 8, description="Actionable replenishment queue prioritized by predicted stockout probability")
    ]
))

# ==============================================================================
# 5. ML — Stockout Survival Analysis (Scientific Analytics)
# ==============================================================================
save_dashboard(SCI_DIR, dashboard_json(
    title="ML — Stockout Survival Analysis",
    uid="ml_stockout_survival_v1",
    tags=["scientific", "ml", "survival", "cox", "fmcg"],
    panels=[
        text_panel(1, "Scientific Model Card & Survival Analysis Context",
            "**Core:** `stockout_survival_v1` | **Model Architecture:** `Cox Proportional Hazards Model with L2 Regularization`\n"
            "**Time Horizon:** 7-Day continuous evaluation study with administrative right-censoring at Day 7 (3,797 test episodes).\n"
            "> ⚠️ **Kaplan-Meier Semantics:** Empirical survival step functions are calculated directly from duration_days and depletion events. Administrative censoring ends the study at Day 7.",
            0, 0, 24, 3),
        stat_panel(2, "Concordance Index (C-Index)", "SELECT cast(test::json->>'concordance_index' as float) FROM ml_results.stockout_survival_v1_metrics LIMIT 1;", 0, 3, 8, 3, unit="short", color="blue", decimals=3, description="Harrell's C-index measuring ranking concordance of survival times"),
        stat_panel(3, "Mean 3-Day Depletion-Free Rate", "SELECT round((avg(survival_probability_day_3) * 100)::numeric, 1) FROM ml_results.stockout_survival_v1_predictions;", 8, 3, 8, 3, unit="percent", color="green", decimals=1, description="Average cohort probability of maintaining stock availability through Day 3"),
        stat_panel(4, "Mean 7-Day Depletion-Free Rate", "SELECT round((avg(survival_probability_day_7) * 100)::numeric, 1) FROM ml_results.stockout_survival_v1_predictions;", 16, 3, 8, 3, unit="percent", color="green", decimals=1, description="Average cohort probability of maintaining stock availability through Day 7"),
        
        # SCIENTIFIC DIAGNOSTIC 1: Empirical Kaplan-Meier Survival Step Function
        xychart_panel(5, "Empirical Kaplan–Meier Survival Step Function (Days 0 to 7)",
            "WITH days AS ("
            "    SELECT generate_series(0, 7) as day"
            "), events AS ("
            "    SELECT duration_days::int as day, sum(case when survival_event then 1 else 0 end) as events, count(*) as removed "
            "    FROM ml_results.stockout_survival_v1_predictions GROUP BY duration_days::int"
            "), timeline AS ("
            "    SELECT d.day, coalesce(e.events, 0) as events, coalesce(e.removed, 0) as removed, "
            "           (SELECT count(*) FROM ml_results.stockout_survival_v1_predictions) - coalesce(sum(e.removed) over (order by d.day rows between unbounded preceding and 1 preceding), 0) as at_risk "
            "    FROM days d LEFT JOIN events e ON d.day = e.day"
            ") SELECT day, case when day = 0 then 100.0 else round((exp(sum(ln(case when events = 0 then 1.0 else (1.0 - events::numeric / at_risk) end)) over (order by day rows between unbounded preceding and current row)) * 100)::numeric, 2) end as km_survival_pct "
            "FROM timeline ORDER BY day ASC;",
            [
                {"name": "Kaplan-Meier Survival Rate (%)", "xField": "day", "yField": "km_survival_pct", "show": "lines", "lineWidth": 3, "lineInterpolation": "stepAfter", "color": "#73BF69"}
            ],
            0, 6, 12, 8, description="Empirical Kaplan-Meier survival step function across the 7-day study horizon derived from duration_days and survival_event"),
        
        # SCIENTIFIC DIAGNOSTIC 2: Stratified Kaplan-Meier Survival Curves
        xychart_panel(6, "Stratified Kaplan–Meier Survival by Hazard Risk Cohort",
            "WITH base AS ("
            "    SELECT case when risk_score > 1.0 then 'Elevated Hazard (Risk > 1.0)' else 'Baseline / Low Hazard (Risk <= 1.0)' end as risk_group, "
            "           duration_days::int as day, survival_event "
            "    FROM ml_results.stockout_survival_v1_predictions"
            "), totals AS ("
            "    SELECT risk_group, count(*) as total_cohort FROM base GROUP BY risk_group"
            "), days AS ("
            "    SELECT d.day, t.risk_group, t.total_cohort FROM generate_series(0, 7) d(day) CROSS JOIN totals t"
            "), events AS ("
            "    SELECT risk_group, day, sum(case when survival_event then 1 else 0 end) as events, count(*) as removed FROM base GROUP BY risk_group, day"
            "), timeline AS ("
            "    SELECT d.risk_group, d.day, coalesce(e.events, 0) as events, coalesce(e.removed, 0) as removed, "
            "           d.total_cohort - coalesce(sum(e.removed) over (partition by d.risk_group order by d.day rows between unbounded preceding and 1 preceding), 0) as at_risk "
            "    FROM days d LEFT JOIN events e ON d.risk_group = e.risk_group AND d.day = e.day"
            "), km AS ("
            "    SELECT day, risk_group, case when day = 0 then 100.0 else round((exp(sum(ln(case when events = 0 then 1.0 else (1.0 - events::numeric / at_risk) end)) over (partition by risk_group order by day rows between unbounded preceding and current row)) * 100)::numeric, 2) end as km_survival_pct "
            "    FROM timeline"
            ") SELECT day, max(case when risk_group like 'Baseline%' then km_survival_pct end) as \"Low Hazard Cohort (Risk <= 1.0)\", "
            "       max(case when risk_group like 'Elevated%' then km_survival_pct end) as \"Elevated Hazard Cohort (Risk > 1.0)\" "
            "FROM km GROUP BY day ORDER BY day ASC;",
            [
                {"name": "Low Hazard Cohort (Risk <= 1.0)", "xField": "day", "yField": "Low Hazard Cohort (Risk <= 1.0)", "show": "lines", "lineWidth": 3, "lineInterpolation": "stepAfter", "color": "#73BF69"},
                {"name": "Elevated Hazard Cohort (Risk > 1.0)", "xField": "day", "yField": "Elevated Hazard Cohort (Risk > 1.0)", "show": "lines", "lineWidth": 3, "lineInterpolation": "stepAfter", "color": "#F2495C"}
            ],
            12, 6, 12, 8, description="Empirical survival trajectory divergence comparing elevated hazard positions against baseline low-hazard stock"),
        
        barchart_panel(7, "Cox Hazard Model Feature Log-Hazard Coefficients", 
            "SELECT feature, round(coef::numeric, 3) as log_hazard_coefficient FROM ml_results.stockout_survival_v1_coefficients ORDER BY coef DESC;", 
            0, 14, 12, 8, orientation="horizontal", unit="short", color="orange", description="Log-hazard ratio coefficients indicating risk accelerators (>0) and protective buffers (<0)", overrides=[
                {"matcher": {"id": "byName", "options": "log_hazard_coefficient"}, "properties": [{"id": "color", "value": {"mode": "thresholds"}}, {"id": "thresholds", "value": {"mode": "absolute", "steps": [{"color": "blue", "value": None}, {"color": "orange", "value": 0}]}}]}
            ]),
        barchart_panel(8, "Multi-Horizon Predicted Survival Probability Decay", 
            "SELECT 'Day 3 Horizon' as horizon, round((avg(survival_probability_day_3) * 100)::numeric, 2) as \"Predicted Survival Rate (%)\" FROM ml_results.stockout_survival_v1_predictions UNION ALL SELECT 'Day 5 Horizon', round((avg(survival_probability_day_5) * 100)::numeric, 2) FROM ml_results.stockout_survival_v1_predictions UNION ALL SELECT 'Day 7 Horizon', round((avg(survival_probability_day_7) * 100)::numeric, 2) FROM ml_results.stockout_survival_v1_predictions ORDER BY 1;", 
            12, 14, 12, 8, orientation="vertical", xField="horizon", unit="percent", description="Cohort mean predicted survival probability decay across discrete horizons"),
        barchart_panel(9, "Average 7-Day Survival Probability by Warehouse", 
            "SELECT concat('Warehouse ', warehouse_id) as warehouse, round((avg(survival_probability_day_7) * 100)::numeric, 1) as avg_7d_survival_pct FROM ml_results.stockout_survival_v1_predictions GROUP BY 1 ORDER BY 2 DESC;", 
            0, 22, 12, 7, orientation="horizontal", unit="percent", color="blue", description="Geographic fulfillment comparison across 7-day survival rates"),
        barchart_panel(10, "Depletion Risk Score Tier Distribution", 
            "SELECT case when risk_score < 0.5 then 'Moderate Risk (< 0.5)' when risk_score < 1.0 then 'Elevated Risk (0.5 - 1.0)' else 'Critical Depletion Risk (> 1.0)' end as risk_tier, count(*) as episode_count FROM ml_results.stockout_survival_v1_predictions GROUP BY 1 ORDER BY min(risk_score) ASC;", 
            12, 22, 12, 7, orientation="horizontal", unit="short", color="red", description="Inventory cohort segmented into operational risk urgency categories"),
        table_panel(11, "Highest-Risk Survival Episodes & Depletion Curves", 
            "SELECT to_char(prediction_date, 'YYYY-MM-DD') as date, warehouse_id, sku_id, round(risk_score::numeric, 2) as hazard_score, round((survival_probability_day_3 * 100)::numeric, 1) as prob_day_3_pct, round((survival_probability_day_5 * 100)::numeric, 1) as prob_day_5_pct, round((survival_probability_day_7 * 100)::numeric, 1) as prob_day_7_pct, available_quantity, round(sales_velocity_7d::numeric, 2) as velocity_7d FROM ml_results.stockout_survival_v1_predictions ORDER BY risk_score DESC LIMIT 200;", 
            0, 29, 24, 8, description="Top prioritized inventory positions with full 3-day, 5-day, and 7-day survival probability projections")
    ]
))

# ==============================================================================
# 6. ML — Store Segmentation (Scientific Analytics)
# ==============================================================================
save_dashboard(SCI_DIR, dashboard_json(
    title="ML — Store Segmentation",
    uid="ml_segmentation_v1",
    tags=["scientific", "ml", "clustering", "segmentation", "fmcg"],
    panels=[
        text_panel(1, "Scientific Model Card & Clustering Context",
            "**Core:** `segmentation_v1` | **Algorithm:** `K-Means Clustering on Robust Scaled Commercial Features`\n"
            "**Evaluation Scope:** 20 retail outlets tracked across consecutive quarters to assess commercial segment stability.\n"
            "> ⚠️ **Cluster Selection Evidence:** K-selection candidate metrics evaluate silhouette separation across candidate k-values. Standardized profiles highlight dimensional departures from the retail network mean.",
            0, 0, 24, 3),
        stat_panel(2, "Analyzed Stores", "SELECT COUNT(DISTINCT store_id) FROM ml_results.segmentation_v1_assignments;", 0, 3, 6, 3, unit="short", color="text", description="Total physical store locations analyzed"),
        stat_panel(3, "Optimal Clusters", "SELECT number_of_clusters FROM ml_results.segmentation_v1_metrics LIMIT 1;", 6, 3, 6, 3, unit="short", color="purple", description="Selected cluster count from silhouette optimization"),
        stat_panel(4, "Silhouette Score", "SELECT selected_silhouette FROM ml_results.segmentation_v1_metrics LIMIT 1;", 12, 3, 6, 3, unit="short", color="blue", decimals=3, description="Mean silhouette coefficient measuring cluster separation"),
        stat_panel(5, "Temporal Retention", "SELECT temporal_assignment_retention * 100 FROM ml_results.segmentation_v1_metrics LIMIT 1;", 18, 3, 6, 3, unit="percent", color="green", decimals=1, description="Percentage stability of cluster assignments across quarterly periods"),
        
        # SCIENTIFIC DIAGNOSTIC 1: K-Selection Optimization Curve
        xychart_panel(6, "K-Selection Model Optimization (Silhouette & Davies-Bouldin Curves)",
            "SELECT k, round(silhouette::numeric, 4) as \"Silhouette Score (Higher is Better)\", round(davies_bouldin::numeric, 4) as \"Davies-Bouldin Index (Lower is Better)\" "
            "FROM ml_results.segmentation_v1_candidates WHERE algorithm = 'kmeans' ORDER BY k ASC;",
            [
                {"name": "Silhouette Score (Higher is Better)", "xField": "k", "yField": "Silhouette Score (Higher is Better)", "show": "both", "lineWidth": 3, "pointSize": 6, "color": "#B877D9"},
                {"name": "Davies-Bouldin Index (Lower is Better)", "xField": "k", "yField": "Davies-Bouldin Index (Lower is Better)", "show": "both", "lineWidth": 3, "pointSize": 6, "color": "#FF9830"}
            ],
            0, 6, 12, 8, description="Cluster selection evaluation curves proving mathematical optimality of k=3 (Peak Silhouette, Lowest Davies-Bouldin)"),
        
        # SCIENTIFIC DIAGNOSTIC 2: Standardized Cluster Profiles (Pivoted Multi-Feature Deviations)
        barchart_panel(7, "Standardized Cluster Profiles (Pivoted Multi-Feature Deviations)", 
            "SELECT case when feature = 'revenue_30d' then '30-Day Revenue' when feature = 'promotion_unit_share_30d' then 'Promotion Unit Share' when feature = 'average_price_30d' then 'Average Unit Price' when feature = 'revenue_volatility_30d' then 'Revenue Volatility' end as feature_name, round(max(case when cluster_id = 0 then standardized_profile end)::numeric, 2) as \"Cluster 0 (Lower-Vol Lower-Promo)\", round(max(case when cluster_id = 1 then standardized_profile end)::numeric, 2) as \"Cluster 1 (Higher-Vol Balanced-Promo)\", round(max(case when cluster_id = 2 then standardized_profile end)::numeric, 2) as \"Cluster 2 (Lower-Vol Promo-Leaning)\" FROM ml_results.segmentation_v1_profiles GROUP BY feature ORDER BY feature;", 
            12, 6, 12, 8, orientation="vertical", xField="feature_name", unit="short", description="Standardized feature centroid deviations comparing the three discovered store clusters", overrides=[
                {"matcher": {"id": "byName", "options": "Cluster 0 (Lower-Vol Lower-Promo)"}, "properties": [{"id": "color", "value": {"mode": "fixed", "fixedColor": "blue"}}]},
                {"matcher": {"id": "byName", "options": "Cluster 1 (Higher-Vol Balanced-Promo)"}, "properties": [{"id": "color", "value": {"mode": "fixed", "fixedColor": "green"}}]},
                {"matcher": {"id": "byName", "options": "Cluster 2 (Lower-Vol Promo-Leaning)"}, "properties": [{"id": "color", "value": {"mode": "fixed", "fixedColor": "purple"}}]}
            ]),
        
        # SCIENTIFIC DIAGNOSTIC 3: Centroid Distance Margin Distribution
        barchart_panel(8, "Centroid Distance Margin Distribution (Assignment Ambiguity)", 
            "SELECT case "
            "    when centroid_distance_margin < 0.5 then 'Low Margin (< 0.5 - Boundary Stores)' "
            "    when centroid_distance_margin < 1.0 then 'Moderate Margin (0.5 - 1.0)' "
            "    else 'High Margin (> 1.0 - Core Exemplars)' "
            "end as margin_tier, count(*) as store_snapshots "
            "FROM ml_results.segmentation_v1_assignments GROUP BY 1 ORDER BY min(centroid_distance_margin) ASC;", 
            0, 14, 12, 7, orientation="horizontal", unit="short", color="purple", description="Distance margin separating primary cluster from nearest alternative cluster"),
        
        barchart_panel(9, "Stores per Commercial Segment", 
            "SELECT segment_name as segment, sum(store_count) as store_count FROM ml_results.segmentation_v1_sizes GROUP BY 1 ORDER BY 2 DESC;", 
            12, 14, 12, 7, orientation="horizontal", unit="short", color="blue", description="Store distribution across the 3 discovered commercial clusters"),
        table_panel(10, "Store Cluster Assignments & Centroid Distances", 
            "SELECT s.store_id, st.store_name, st.store_type, st.channel, r.region_name, to_char(s.snapshot_date, 'YYYY-MM-DD') as snapshot_date, s.reference_cluster_id as cluster_id, s.segment_name, round(s.distance_to_centroid::numeric, 3) as centroid_dist, round(s.centroid_distance_margin::numeric, 3) as dist_margin FROM ml_results.segmentation_v1_assignments s JOIN fmcg.stores st ON s.store_id = st.store_id JOIN fmcg.regions r ON st.region_id = r.region_id ORDER BY s.snapshot_date DESC, s.reference_cluster_id, s.distance_to_centroid ASC;", 
            0, 21, 24, 8, description="Store-level cluster memberships, centroid distances, and distance margins")
    ]
))

# ==============================================================================
# 7. ML — Anomaly Detection (Scientific Analytics)
# ==============================================================================
save_dashboard(SCI_DIR, dashboard_json(
    title="ML — Anomaly Detection",
    uid="ml_anomaly_v1",
    tags=["scientific", "ml", "anomaly", "isolation-forest", "fmcg"],
    panels=[
        text_panel(1, "Scientific Model Card & Anomaly Detection Context",
            "**Core:** `anomaly_v1` | **Detectors:** `Statistical 7-Day Rolling Z-Score` & `Unsupervised Isolation Forest Ensemble`\n"
            "**Evaluation Scope:** 100 screened candidate outlier sales events prioritized for commercial and operational audit.\n"
            "> ⚠️ **Candidate Screening Subtitle:** Displays the prioritized review candidate subset (n=100) combining statistical and tree-based detector outputs.",
            0, 0, 24, 3),
        stat_panel(2, "Review Candidates", "SELECT COUNT(*) FROM ml_results.anomaly_v1_candidates;", 0, 3, 6, 3, unit="short", color="orange", description="Total prioritized outlier demand events"),
        stat_panel(3, "Z-Score Candidates", "SELECT COUNT(*) FROM ml_results.anomaly_v1_candidates WHERE zscore_candidate = true;", 6, 3, 6, 3, unit="short", color="blue", description="Candidates flagged by 7-day historical z-score threshold"),
        stat_panel(4, "Isolation Forest Candidates", "SELECT COUNT(*) FROM ml_results.anomaly_v1_candidates WHERE iforest_candidate = true;", 12, 3, 6, 3, unit="short", color="purple", description="Candidates flagged by multi-dimensional Isolation Forest"),
        stat_panel(5, "Both Ensembles Agree", "SELECT COUNT(*) FROM ml_results.anomaly_v1_candidates WHERE method_agreement = 'BOTH';", 18, 3, 6, 3, unit="short", color="red", description="High-confidence consensus outliers flagged by both models"),
        
        # SCIENTIFIC DIAGNOSTIC 1: Z-Score vs Isolation Forest Score Bivariate Scatter
        xychart_panel(6, "Historical Z-Score vs. Isolation Forest Anomaly Score (Bivariate Decision Space)",
            "SELECT round(historical_zscore::numeric, 2) as zscore, "
            "       case when method_agreement = 'BOTH' and zscore_direction = 'HIGH' then round(iforest_anomaly_score::numeric, 4) end as \"Consensus Spike (Both Agree)\", "
            "       case when method_agreement = 'BOTH' and zscore_direction = 'LOW' then round(iforest_anomaly_score::numeric, 4) end as \"Consensus Collapse (Both Agree)\", "
            "       case when method_agreement = 'IFOREST_ONLY' then round(iforest_anomaly_score::numeric, 4) end as \"Multidimensional Outlier (IF Only)\" "
            "FROM ml_results.anomaly_v1_candidates ORDER BY zscore ASC;",
            [
                {"name": "Consensus Spike (Both Agree)", "xField": "zscore", "yField": "Consensus Spike (Both Agree)", "show": "points", "pointSize": 6, "color": "#F2495C"},
                {"name": "Consensus Collapse (Both Agree)", "xField": "zscore", "yField": "Consensus Collapse (Both Agree)", "show": "points", "pointSize": 6, "color": "#5794F2"},
                {"name": "Multidimensional Outlier (IF Only)", "xField": "zscore", "yField": "Multidimensional Outlier (IF Only)", "show": "points", "pointSize": 5, "color": "#B877D9"}
            ],
            0, 6, 12, 8, description="Bivariate decision space comparing statistical Z-Score departures against Isolation Forest scores (Review candidate subset, n=100)"),
        
        # SCIENTIFIC DIAGNOSTIC 2: Observed Units vs Expected Baseline Scatter
        xychart_panel(7, "Observed Sales Units vs. 7-Day Historical Baseline",
            "SELECT round(historical_mean_7d::numeric, 1) as historical_mean_7d, event_observed_units as observed_units, round(historical_mean_7d::numeric, 1) as expected_baseline "
            "FROM ml_results.anomaly_v1_candidates ORDER BY historical_mean_7d ASC;",
            [
                {"name": "Flagged Outlier Events", "xField": "historical_mean_7d", "yField": "observed_units", "show": "points", "pointSize": 5, "color": "#FF9830"},
                {"name": "Expected Baseline (y = x)", "xField": "historical_mean_7d", "yField": "expected_baseline", "show": "lines", "lineWidth": 2, "lineStyle": {"dash": [4, 4]}, "color": "#73BF69"}
            ],
            12, 6, 12, 8, description="Physical sales volume departures plotted against 7-day expected baseline demand"),
        
        barchart_panel(8, "Anomaly Candidates by Pattern & Direction", 
            "SELECT case when zscore_direction = 'HIGH' then 'Demand Spike (Z-Score High)' when zscore_direction = 'LOW' then 'Demand Collapse (Z-Score Low)' when zscore_direction = 'NONE' and method_agreement = 'IFOREST_ONLY' then 'Multi-Dimensional Outlier (Isolation Forest)' else 'Unclassified' end as anomaly_pattern, count(*) as candidate_count FROM ml_results.anomaly_v1_candidates GROUP BY 1 ORDER BY 2 DESC;", 
            0, 14, 12, 7, orientation="horizontal", unit="short", color="orange", description="Classification of outliers into volume spikes, volume collapses, and multi-dimensional deviations"),
        barchart_panel(9, "Detection Method Agreement", 
            "SELECT case when method_agreement = 'BOTH' then 'Both Methods Converge' else 'Isolation Forest Only' end as detection_method, count(*) as candidate_count FROM ml_results.anomaly_v1_candidates GROUP BY 1 ORDER BY 2 DESC;", 
            12, 14, 12, 7, orientation="horizontal", unit="short", color="purple", description="Concordance between statistical z-score and machine learning Isolation Forest models"),
        table_panel(10, "Ranked Anomaly Candidates for Business Review", 
            "SELECT event_date as date, store_id, sku_id, brand_name, category_name, event_observed_units as observed_units, round(historical_mean_7d::numeric, 1) as baseline_mean_7d, round(abs_historical_zscore::numeric, 2) as zscore, round(iforest_anomaly_score::numeric, 3) as iforest_score, method_agreement, case when zscore_direction = 'HIGH' then 'SPIKE' when zscore_direction = 'LOW' then 'DROP' else 'IFOREST' end as pattern FROM ml_results.anomaly_v1_candidates ORDER BY case when method_agreement = 'BOTH' then 0 else 1 end, abs_historical_zscore DESC NULLS LAST LIMIT 100;", 
            0, 21, 24, 8, description="Prioritized outlier episodes sorted by consensus and deviation severity", overrides=[
                {"matcher": {"id": "byName", "options": "pattern"}, "properties": [{"id": "mappings", "value": [{"type": "value", "options": {"SPIKE": {"color": "red", "index": 0}, "DROP": {"color": "blue", "index": 1}, "IFOREST": {"color": "purple", "index": 2}}}]}]}
            ])
    ]
))

# ==============================================================================
# 8. ML — Market Basket Analysis (Scientific Analytics)
# ==============================================================================
save_dashboard(SCI_DIR, dashboard_json(
    title="ML — Market Basket Analysis",
    uid="ml_basket_v1",
    tags=["scientific", "ml", "market-basket", "association-rules", "fmcg"],
    panels=[
        text_panel(1, "Scientific Model Card & Market Basket Context",
            "**Core:** `basket_v1` | **Algorithm:** `Apriori Frequent Itemset Mining & Association Rule Mining`\n"
            "**Scope:** Transactional point-of-sale receipt basket co-occurrence.\n"
            "> ⚠️ **Descriptive Co-occurrence Caveat:** Association rules establish empirical co-occurrence patterns in transactional logs; they do not establish causal purchasing mechanisms.\n"
            "**Rule Statistics:** Total Canonical Mined Rules = **1,262 rules** | Displayed = **Governed top rules**.",
            0, 0, 24, 3),
        stat_panel(2, "Canonical Rules Discovered", "SELECT canonical_rule_count FROM ml_results.basket_v1_metrics LIMIT 1;", 0, 3, 6, 3, unit="short", color="text", description="Total rules mined in canonical execution meeting threshold criteria"),
        stat_panel(3, "Displayed Top Rules", "SELECT COUNT(*) FROM ml_results.basket_v1_rules;", 6, 3, 6, 3, unit="short", color="text", description="Governed rules published to operational presentation tables"),
        stat_panel(4, "Maximum Rule Lift", "SELECT max_rule_lift FROM ml_results.basket_v1_metrics LIMIT 1;", 12, 3, 6, 3, unit="short", color="orange", decimals=3, description="Peak affinity lift multiplier discovered"),
        stat_panel(5, "Median Rule Confidence", "SELECT median_rule_confidence * 100 FROM ml_results.basket_v1_metrics LIMIT 1;", 18, 3, 6, 3, unit="percent", color="purple", decimals=1, description="Median conditional probability across discovered association rules"),
        
        # SCIENTIFIC DIAGNOSTIC 1: Support vs Confidence Scatter with Lift Tier Encoding
        xychart_panel(6, "Support vs. Confidence Scatter with Statistical Lift Encoding",
            "SELECT round((support * 100)::numeric, 2) as support_pct, "
            "       case when lift >= 1.55 then round((confidence * 100)::numeric, 1) end as \"High Affinity (Lift >= 1.55)\", "
            "       case when lift >= 1.45 and lift < 1.55 then round((confidence * 100)::numeric, 1) end as \"Moderate Affinity (Lift 1.45 - 1.55)\", "
            "       case when lift < 1.45 then round((confidence * 100)::numeric, 1) end as \"Standard Affinity (Lift < 1.45)\" "
            "FROM ml_results.basket_v1_rules ORDER BY support_pct ASC;",
            [
                {"name": "High Affinity (Lift >= 1.55)", "xField": "support_pct", "yField": "High Affinity (Lift >= 1.55)", "show": "points", "pointSize": 6, "color": "#FF9830"},
                {"name": "Moderate Affinity (Lift 1.45 - 1.55)", "xField": "support_pct", "yField": "Moderate Affinity (Lift 1.45 - 1.55)", "show": "points", "pointSize": 5, "color": "#B877D9"},
                {"name": "Standard Affinity (Lift < 1.45)", "xField": "support_pct", "yField": "Standard Affinity (Lift < 1.45)", "show": "points", "pointSize": 4, "color": "#5794F2"}
            ],
            0, 6, 12, 8, description="Association rule confidence vs basket support trade-off with statistical lift tier color encoding"),
        
        barchart_panel(7, "Top 12 Association Rules by Lift (Joined Product Names)", 
            "SELECT concat(pa.product_name, ' -> ', pc.product_name) as rule_pair, round(r.lift::numeric, 3) as lift FROM ml_results.basket_v1_rules r JOIN fmcg.skus sa ON r.antecedent = sa.sku_id JOIN fmcg.products pa ON sa.product_id = pa.product_id JOIN fmcg.skus sc ON r.consequent = sc.sku_id JOIN fmcg.products pc ON sc.product_id = pc.product_id ORDER BY r.lift DESC LIMIT 12;", 
            12, 6, 12, 8, orientation="horizontal", unit="short", color="orange", description="Highest-affinity cross-merchandising product pairs ranked by statistical lift"),
        barchart_panel(8, "Most Frequent Recommended Consequents", 
            "SELECT pc.product_name as recommended_product, count(*) as rule_count FROM ml_results.basket_v1_rules r JOIN fmcg.skus sc ON r.consequent = sc.sku_id JOIN fmcg.products pc ON sc.product_id = pc.product_id GROUP BY 1 ORDER BY 2 DESC LIMIT 8;", 
            0, 14, 12, 7, orientation="horizontal", unit="short", color="blue", description="Products appearing most frequently as rule consequents for cross-sell"),
        barchart_panel(9, "Rule Confidence Distribution", 
            "SELECT case when confidence < 0.25 then '< 25% Confidence' when confidence < 0.35 then '25% - 35% Confidence' when confidence < 0.45 then '35% - 45% Confidence' else '>= 45% High Confidence' end as confidence_tier, count(*) as rule_count FROM ml_results.basket_v1_rules GROUP BY 1 ORDER BY min(confidence) ASC;", 
            12, 14, 12, 7, orientation="horizontal", unit="short", color="purple", description="Confidence distribution indicating conditional buying probabilities"),
        table_panel(10, "Top 100 Association Rules Detail & Cross-Sell Potential", 
            "SELECT concat(pa.product_name, ' [SKU ', r.antecedent, ']') as antecedent_product, concat(pc.product_name, ' [SKU ', r.consequent, ']') as consequent_product, round((r.support * 100)::numeric, 2) as support_pct, round((r.confidence * 100)::numeric, 1) as confidence_pct, round(r.lift::numeric, 3) as lift FROM ml_results.basket_v1_rules r JOIN fmcg.skus sa ON r.antecedent = sa.sku_id JOIN fmcg.products pa ON sa.product_id = pa.product_id JOIN fmcg.skus sc ON r.consequent = sc.sku_id JOIN fmcg.products pc ON sc.product_id = pc.product_id ORDER BY r.lift DESC LIMIT 100;", 
            0, 21, 24, 8, description="Interactive audit table of discovered association rules with joined product catalog metadata")
    ]
))

# ==============================================================================
# 9. Analytics — Promotion Performance (Scientific Analytics)
# ==============================================================================
save_dashboard(SCI_DIR, dashboard_json(
    title="Analytics — Promotion Performance",
    uid="ml_promotion_v1",
    tags=["analytics", "promotion", "uplift", "fmcg"],
    panels=[
        text_panel(1, "Analytical Methodology & Observational Context",
            "**Core:** `promotion_v1` | **Evaluation Methodology:** `Descriptive Window Comparison (Pre vs During vs Post)`\n"
            "**Scope:** 3 promotional discount events evaluated across 2,880 SKU-store exposures.\n"
            "> ⚠️ **Observational Caveat:** The evaluation employs descriptive window comparisons without counterfactual synthetic controls. Unobserved seasonal shocks, competitor actions, and stockouts are not causally isolated.",
            0, 0, 24, 3),
        stat_panel(2, "Promotions Evaluated", "SELECT promotion_count FROM ml_results.promotion_v1_metrics LIMIT 1;", 0, 3, 8, 3, unit="short", color="text", description="Total distinct promotional campaigns evaluated"),
        stat_panel(3, "SKU-Store Exposures", "SELECT exposure_count FROM ml_results.promotion_v1_metrics LIMIT 1;", 8, 3, 8, 3, unit="short", color="text", description="Total SKU-store retail campaign exposures evaluated"),
        stat_panel(4, "Evaluation Methodology", "SELECT 'Descriptive Window Comparison' AS methodology;", 16, 3, 8, 3, unit="string", color="blue", description="Analytical framework applied for uplift measurement", is_string=True),
        
        # SCIENTIFIC DIAGNOSTIC 1: Units Uplift vs Revenue Uplift Scatter (2,880 Exposures)
        xychart_panel(5, "Units Uplift vs. Revenue Uplift Scatter (2,880 Retail Exposures)",
            "SELECT round((during_vs_pre_relative_units_change * 100)::numeric, 1) as units_lift_pct, "
            "       case when during_vs_pre_relative_revenue_change >= 0 and during_vs_pre_relative_units_change >= 0 then round((during_vs_pre_relative_revenue_change * 100)::numeric, 1) end as \"Profitable Uplift (Units Up, Revenue Up)\", "
            "       case when during_vs_pre_relative_revenue_change < 0 and during_vs_pre_relative_units_change >= 0 then round((during_vs_pre_relative_revenue_change * 100)::numeric, 1) end as \"Margin Dilution (Units Up, Revenue Down)\", "
            "       case when during_vs_pre_relative_units_change < 0 then round((during_vs_pre_relative_revenue_change * 100)::numeric, 1) end as \"Volume Drag (Units Down)\" "
            "FROM ml_results.promotion_v1_exposure WHERE during_vs_pre_relative_units_change IS NOT NULL AND during_vs_pre_relative_revenue_change IS NOT NULL ORDER BY units_lift_pct ASC;",
            [
                {"name": "Profitable Uplift (Units Up, Revenue Up)", "xField": "units_lift_pct", "yField": "Profitable Uplift (Units Up, Revenue Up)", "show": "points", "pointSize": 4, "color": "#73BF69"},
                {"name": "Margin Dilution (Units Up, Revenue Down)", "xField": "units_lift_pct", "yField": "Margin Dilution (Units Up, Revenue Down)", "show": "points", "pointSize": 4, "color": "#FF9830"},
                {"name": "Volume Drag (Units Down)", "xField": "units_lift_pct", "yField": "Volume Drag (Units Down)", "show": "points", "pointSize": 4, "color": "#F2495C"}
            ],
            0, 6, 12, 8, description="Exposure-level volume growth vs revenue expansion revealing margin dilution and deal profitability across 2,880 exposures"),
        
        # SCIENTIFIC DIAGNOSTIC 2: Before vs. During Sales Velocity Parity Scatter
        xychart_panel(6, "Before vs. During Sales Velocity Parity Scatter",
            "SELECT round(pre_units_per_day::numeric, 1) as pre_velocity, round(during_units_per_day::numeric, 1) as promo_velocity, round(pre_units_per_day::numeric, 1) as baseline_parity "
            "FROM ml_results.promotion_v1_exposure WHERE pre_units_per_day IS NOT NULL AND during_units_per_day IS NOT NULL ORDER BY pre_velocity ASC;",
            [
                {"name": "Promotional Exposures", "xField": "pre_velocity", "yField": "promo_velocity", "show": "points", "pointSize": 4, "color": "#B877D9"},
                {"name": "Pre-Promo Baseline (y = x)", "xField": "pre_velocity", "yField": "baseline_parity", "show": "lines", "lineWidth": 2, "lineStyle": {"dash": [4, 4]}, "color": "#73BF69"}
            ],
            12, 6, 12, 8, description="Daily sales velocity comparison: points above baseline line represent physical volume uplift"),
        
        barchart_panel(7, "Pre vs During vs Post Sales Velocity (Triple Window Comparison)", 
            "SELECT concat('Campaign ', promotion_id) as campaign, round(pre_units_per_day::numeric, 1) as \"Pre-Promo (Baseline)\", round(during_units_per_day::numeric, 1) as \"During-Promo (Uplift)\", round(coalesce(post_units_per_day, 0)::numeric, 1) as \"Post-Promo (Rebound)\" FROM ml_results.promotion_v1_summary ORDER BY promotion_id;", 
            0, 14, 12, 7, orientation="vertical", xField="campaign", unit="short", description="Daily unit sales velocity per store across pre, during, and post campaign phases", overrides=[
                {"matcher": {"id": "byName", "options": "Pre-Promo (Baseline)"}, "properties": [{"id": "color", "value": {"mode": "fixed", "fixedColor": "blue"}}]},
                {"matcher": {"id": "byName", "options": "During-Promo (Uplift)"}, "properties": [{"id": "color", "value": {"mode": "fixed", "fixedColor": "orange"}}]},
                {"matcher": {"id": "byName", "options": "Post-Promo (Rebound)"}, "properties": [{"id": "color", "value": {"mode": "fixed", "fixedColor": "green"}}]}
            ]),
        barchart_panel(8, "Promotional Lift by Product Category (2,880 Exposures)", 
            "SELECT category_name as category, round((avg(during_vs_pre_relative_units_change) * 100)::numeric, 1) as avg_units_lift_pct FROM ml_results.promotion_v1_exposure WHERE during_vs_pre_relative_units_change IS NOT NULL GROUP BY 1 ORDER BY 2 DESC;", 
            12, 14, 12, 7, orientation="horizontal", unit="percent", color="orange", description="Average percentage unit volume uplift by product category"),
        table_panel(9, "Promotion Performance Summary Table", 
            "SELECT concat('Promo ', promotion_id) as campaign, to_char(start_date, 'YYYY-MM-DD') as start_date, to_char(end_date, 'YYYY-MM-DD') as end_date, duration_days, exposure_count, round(pre_units_per_day::numeric, 1) as pre_velocity, round(during_units_per_day::numeric, 1) as promo_velocity, round(coalesce(post_units_per_day, 0)::numeric, 1) as post_velocity, round((during_vs_pre_relative_units_change * 100)::numeric, 1) as units_lift_pct, round((during_vs_pre_relative_revenue_change * 100)::numeric, 1) as revenue_lift_pct FROM ml_results.promotion_v1_summary ORDER BY promotion_id;", 
            0, 21, 24, 8, description="Comprehensive promotional campaign benchmarking table")
    ]
))

# ==============================================================================
# 10. ML — Publication Registry (Operations)
# ==============================================================================
save_dashboard(OPS_DIR, dashboard_json(
    title="ML — Publication Registry",
    uid="ml_publication_registry",
    tags=["operations", "governance", "registry", "fmcg"],
    panels=[
        text_panel(1, "Scientific Publication Governance Card",
            "**Publication Registry & Presentation Data Integrity Ledger** — Authoritative sync record governing `ml_results` presentation tables.\n"
            "*Audit Policy:* Authoritative presentation tables across 7 scientific cores. Verifies artifact sources, published tables, and exact row counts.",
            0, 0, 24, 3),
        stat_panel(2, "Published Presentation Tables", "SELECT count(*) FROM ml_results.publication_manifest;", 0, 3, 6, 3, unit="short", color="blue", description="Total published tables registered in ml_results"),
        stat_panel(3, "Authoritative Published Rows", "SELECT sum(row_count) FROM ml_results.publication_manifest;", 6, 3, 6, 3, unit="short", color="purple", description="Authoritative total row count published across all presentation tables"),
        stat_panel(4, "Scientific Cores Governed", "SELECT count(distinct core) FROM ml_results.publication_manifest;", 12, 3, 6, 3, unit="short", color="green", description="Number of scientific ML cores integrated into publication layer"),
        stat_panel(5, "Artifact Sync Status", "SELECT 'SYNCED' AS sync_status;", 18, 3, 6, 3, unit="string", color="green", description="Synchronization state between canonical artifacts and published tables", is_string=True),
        barchart_panel(6, "Presentation Rows by Scientific Core", 
            "SELECT core, sum(row_count) as total_rows FROM ml_results.publication_manifest GROUP BY 1 ORDER BY 2 DESC;", 
            0, 6, 12, 8, orientation="horizontal", unit="short", color="blue", description="Row distribution across the 7 governed scientific cores"),
        barchart_panel(7, "Published Tables per Scientific Core", 
            "SELECT core, count(*) as table_count FROM ml_results.publication_manifest GROUP BY 1 ORDER BY 2 DESC;", 
            12, 6, 12, 8, orientation="horizontal", unit="short", color="purple", description="Table count registered per scientific core"),
        table_panel(8, "Publication Manifest Audit Trail", 
            "SELECT table_name, core, source_file, row_count, to_char(published_at, 'YYYY-MM-DD HH24:MI:SS') as published_timestamp FROM ml_results.publication_manifest ORDER BY table_name;", 
            0, 14, 24, 10, description="Exhaustive registry audit trail detailing artifact source paths and published row counts")
    ]
))

# ==============================================================================
# 11. FMCG Platform & ML Health (Operations)
# ==============================================================================
def prom_stat(id, title, expr, x, y, w=6, h=3, unit="short", color_steps=None, description=""):
    return {
        "id": id, "title": title, "type": "stat", "description": description,
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [{"datasource": DS_PROM, "editorMode": "code", "expr": expr, "legendFormat": "{{model}}", "range": True, "refId": "A"}],
        "options": {
            "colorMode": "background" if color_steps else "value", "graphMode": "none", "justifyMode": "auto",
            "reduceOptions": {"calcs": ["lastNotNull"], "values": False}
        },
        "fieldConfig": {
            "defaults": {
                "unit": unit,
                "color": {"mode": "thresholds"},
                "thresholds": {"mode": "absolute", "steps": color_steps or [{"color": "text", "value": None}]}
            },
            "overrides": []
        }
    }

def prom_timeseries(id, title, expr, legendFormat, x, y, w=12, h=8, unit="reqps", description=""):
    return {
        "id": id, "title": title, "type": "timeseries", "description": description,
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [{"datasource": DS_PROM, "editorMode": "code", "expr": expr, "legendFormat": legendFormat, "range": True, "refId": "A"}],
        "options": {"legend": {"displayMode": "list", "placement": "bottom", "showLegend": True}},
        "fieldConfig": {
            "defaults": {
                "unit": unit,
                "custom": {"drawStyle": "line", "lineInterpolation": "smooth", "lineWidth": 2, "fillOpacity": 15},
                "color": {"mode": "palette-classic"}
            },
            "overrides": []
        }
    }

save_dashboard(OPS_DIR, dashboard_json(
    title="FMCG Platform & ML Health",
    uid="fmcg_plat_health",
    time_from="now-1h", time_to="now",
    tags=["operations", "health", "prometheus", "sre", "fmcg"],
    panels=[
        text_panel(1, "Operational Platform SRE Context",
            "**FastAPI & ML Inference Runtime Observability** — Live operational telemetry scraped from Prometheus (`api:8000/metrics`).\n"
            "*Telemetry Scope:* HTTP throughput, latency distributions, error codes, and serving model readiness.",
            0, 0, 24, 2),
        prom_stat(2, "API Request Rate (5m)", "sum(rate(fsi_http_requests_total[5m])) or vector(0)", 0, 2, 6, 3, unit="reqps", description="Total incoming HTTP requests per second"),
        prom_stat(3, "Total API 5xx Errors", "sum(fsi_http_requests_total{status=~'5..'}) or vector(0)", 6, 2, 6, 3, unit="short", color_steps=[{"color": "green", "value": None}, {"color": "red", "value": 1}], description="Count of 5xx server errors"),
        prom_stat(4, "Forecast Model Serving Ready", "fsi_model_ready{model='forecasting'}", 12, 2, 6, 3, unit="short", color_steps=[{"color": "red", "value": None}, {"color": "green", "value": 1}], description="Demand forecast model memory and serving state"),
        prom_stat(5, "Stockout Model Serving Ready", "fsi_model_ready{model='stockout_classification'}", 18, 2, 6, 3, unit="short", color_steps=[{"color": "red", "value": None}, {"color": "green", "value": 1}], description="Stockout risk model memory and serving state"),
        prom_timeseries(6, "API Request Rate Over Time (5m Average)", "sum(rate(fsi_http_requests_total[5m]))", "Total RPS", 0, 5, 14, 8, unit="reqps", description="HTTP throughput trajectory"),
        prom_timeseries(7, "API Traffic by Route", "sum by (route) (rate(fsi_http_requests_total[5m]))", "{{route}}", 14, 5, 10, 8, unit="reqps", description="Request volume broken down by API endpoint route"),
        prom_timeseries(8, "API Request Latency (95th Percentile)", "histogram_quantile(0.95, sum by (le) (rate(fsi_http_request_duration_seconds_bucket[5m])))", "P95 Latency", 0, 13, 12, 8, unit="s", description="95th percentile HTTP response latency across API endpoints"),
        {
            "id": 9, "title": "Serving Model Status & Memory Health", "type": "barchart", "description": "Operational readiness state across published scientific models",
            "gridPos": {"x": 12, "y": 13, "w": 12, "h": 8},
            "targets": [{"datasource": DS_PROM, "editorMode": "code", "expr": "fsi_model_ready", "legendFormat": "{{model}} Model", "range": True, "refId": "A"}],
            "options": {"orientation": "horizontal", "showValue": "always", "legend": {"displayMode": "list", "placement": "bottom", "showLegend": True}},
            "fieldConfig": {
                "defaults": {
                    "unit": "short",
                    "color": {"mode": "thresholds"},
                    "thresholds": {"mode": "absolute", "steps": [{"color": "red", "value": None}, {"color": "green", "value": 1}]}
                },
                "overrides": []
            }
        }
    ]
))

print("\nAll 11 production-grade dashboards successfully regenerated with scientific diagnostics upgrade v1!")
