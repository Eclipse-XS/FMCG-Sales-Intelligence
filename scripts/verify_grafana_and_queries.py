import json
import base64
import urllib.request
import urllib.parse
import psycopg
import re

GRAFANA_URL = "http://localhost:3001"
AUTH = base64.b64encode(b"admin:change_me").decode("ascii")
HEADERS = {"Authorization": f"Basic {AUTH}"}

PG_CONN = "postgresql://fmcg:change_me@localhost:55432/fmcg"
PROM_URL = "http://localhost:9090"

def get_grafana_dashboards():
    req = urllib.request.Request(f"{GRAFANA_URL}/api/search", headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        items = json.loads(resp.read().decode("utf-8"))
    dashboards = [it for it in items if it.get("type") == "dash-db"]
    return dashboards

def get_dashboard_detail(uid):
    req = urllib.request.Request(f"{GRAFANA_URL}/api/dashboards/uid/{uid}", headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def query_prometheus(expr):
    params = urllib.parse.urlencode({"query": expr})
    url = f"{PROM_URL}/api/v1/query?{params}"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("status") == "success":
                result = data.get("data", {}).get("result", [])
                return True, f"{len(result)} series returned"
            return False, data.get("error", "Unknown error")
    except Exception as e:
        return False, str(e)

def clean_sql_for_test(sql, templating_list):
    # substitute Grafana macros
    clean = re.sub(r"\$__timeFilter\(([^)]+)\)", r"\1 BETWEEN '2024-01-01 00:00:00' AND '2024-03-31 23:59:59'", sql)
    # substitute common template variables
    var_defaults = {
        "time_granularity": "day",
        "min_support": "0.01",
        "min_confidence": "0.05",
        "min_lift": "1.0",
        "cluster_id": "All",
        "candidate_type": "All",
        "warehouse_filter": "All",
        "sku_filter": "All",
        "category_filter": "All",
        "cluster": "All",
        "store": "All",
        "model": "All",
    }
    for var in templating_list:
        name = var.get("name")
        curr = var.get("current", {})
        val = curr.get("value")
        if isinstance(val, list):
            val = val[0] if val else "All"
        if val is not None and val != "$__all":
            var_defaults[name] = str(val)
        elif val == "$__all" or name not in var_defaults:
            var_defaults[name] = "All"

    # Replace Grafana variables $var or ${var}
    for k, v in var_defaults.items():
        if v == "All" or v == "$__all":
            # Replace expressions like "warehouse_id = '$warehouse_filter'" or "(warehouse_id = '$warehouse_filter' OR '$warehouse_filter' = 'All')"
            clean = re.sub(rf"'\${k}'", f"'{v}'", clean)
            clean = re.sub(rf"\${k}", f"'{v}'", clean)
        else:
            clean = re.sub(rf"'\${k}'", f"'{v}'", clean)
            clean = re.sub(rf"\${k}", f"{v}", clean)
    return clean

def main():
    dashboards = get_grafana_dashboards()
    print(f"=== Grafana Provisioned Dashboards ({len(dashboards)}) ===")
    for d in sorted(dashboards, key=lambda x: (x.get("folderTitle", ""), x.get("title", ""))):
        print(f"[{d.get('folderTitle', 'General'):<20}] {d.get('title'):<40} UID: {d.get('uid')}")

    print("\n" + "="*110)
    print(f"{'DASHBOARD':<30} | {'PANEL':<32} | {'DS':<6} | {'STATUS':<7} | {'ROWS / VALUE'}")
    print("="*110)

    conn = psycopg.connect(PG_CONN)
    cursor = conn.cursor()

    total_panels = 0
    passed_panels = 0
    failed_panels = 0

    for d in sorted(dashboards, key=lambda x: (x.get("folderTitle", ""), x.get("title", ""))):
        uid = d.get("uid")
        detail = get_dashboard_detail(uid)
        dash_obj = detail.get("dashboard", {})
        panels = dash_obj.get("panels", [])
        templating = dash_obj.get("templating", {}).get("list", [])

        for p in panels:
            p_type = p.get("type")
            p_title = p.get("title") or f"Panel {p.get('id')}"
            if p_type in ["text", "row"]:
                continue
            
            targets = p.get("targets", [])
            if not targets:
                continue

            total_panels += 1
            ds = targets[0].get("datasource", {})
            ds_type = ds.get("type", "unknown") if isinstance(ds, dict) else "unknown"

            if ds_type == "postgres":
                sql = targets[0].get("rawSql", "")
                test_sql = clean_sql_for_test(sql, templating)
                try:
                    cursor.execute(test_sql)
                    rows = cursor.fetchall()
                    row_count = len(rows)
                    if row_count == 1 and len(rows[0]) == 1:
                        val_str = f"1 value ({rows[0][0]})"
                    else:
                        val_str = f"{row_count} rows"
                    status = "PASS"
                    passed_panels += 1
                except Exception as e:
                    conn.rollback()
                    status = "FAIL"
                    val_str = f"ERROR: {str(e)[:40]}"
                    failed_panels += 1

                print(f"{d.get('title')[:30]:<30} | {p_title[:32]:<32} | {'PG':<6} | {status:<7} | {val_str}")

            elif ds_type == "prometheus":
                expr = targets[0].get("expr", "")
                ok, res_str = query_prometheus(expr)
                if ok:
                    status = "PASS"
                    passed_panels += 1
                else:
                    status = "FAIL"
                    failed_panels += 1
                print(f"{d.get('title')[:30]:<30} | {p_title[:32]:<32} | {'PROM':<6} | {status:<7} | {res_str}")

    print("="*110)
    print(f"TOTAL EVALUATED: {total_panels} | PASSED: {passed_panels} | FAILED: {failed_panels}")

if __name__ == "__main__":
    main()
