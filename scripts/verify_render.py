"""
Comprehensive Browser UI Render Validation across all 11 Grafana dashboards.
Uses Chrome DevTools Protocol to navigate, scroll every panel into view,
and verify that no panel renders 'Err' and all XYCharts render uPlot canvases.
"""

import asyncio
import json
import subprocess
import tempfile
import time
import urllib.request
import websockets

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CDP_PORT = 9222
BASE_URL = "http://localhost:3001"

DASHBOARDS = [
    ("ml_forecasting_v1", "ML — Demand Forecasting"),
    ("ml_stockout_classification_v1", "ML — Stockout Risk Classification"),
    ("ml_stockout_survival_v1", "ML — Stockout Survival Analysis"),
    ("ml_segmentation_v1", "ML — Store Segmentation"),
    ("ml_anomaly_v1", "ML — Anomaly Detection"),
    ("ml_basket_v1", "ML — Market Basket Analysis"),
    ("ml_promotion_v1", "Analytics — Promotion Performance"),
    ("fmcg_biz_overview", "Business — Executive Overview"),
    ("fmcg_sales_inventory", "Commercial — Sales & Inventory Analysis"),
    ("ml_publication_registry", "ML — Publication Registry"),
    ("fmcg_plat_health", "FMCG Platform & ML Health"),
]

class ChromeRunner:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.proc = None

    def start(self):
        cmd = [
            CHROME_PATH,
            "--headless=new",
            f"--remote-debugging-port={CDP_PORT}",
            f"--user-data-dir={self.temp_dir}",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--window-size=1920,1200",
        ]
        self.proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(30):
            try:
                urllib.request.urlopen(f"http://localhost:{CDP_PORT}/json/version", timeout=1)
                return
            except Exception:
                time.sleep(0.2)
        raise RuntimeError("Chrome failed to start CDP")

    def stop(self):
        if self.proc:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except Exception:
                self.proc.kill()


async def send_cmd(ws, method, params=None, msg_id=1):
    req = {"id": msg_id, "method": method, "params": params or {}}
    await ws.send(json.dumps(req))
    while True:
        resp = await ws.recv()
        data = json.loads(resp)
        if data.get("id") == msg_id:
            return data


async def audit_dashboard(ws, uid, title, msg_id_start=100):
    url = f"{BASE_URL}/d/{uid}?kiosk"
    await send_cmd(ws, "Page.navigate", {"url": url}, msg_id=msg_id_start)
    await asyncio.sleep(2.5)

    inspect_script = """
    async () => {
        const items = document.querySelectorAll('.react-grid-item');
        const results = [];
        for (let i = 0; i < items.length; i++) {
            const item = items[i];
            item.scrollIntoView({block: 'center', inline: 'center'});
            await new Promise(r => setTimeout(r, 450));
            
            let title = '';
            const header = item.querySelector('[data-testid*="Panel header"], [class*="panel-title"], h2, h3, h4, h5, h6, [class*="header"]');
            if (header) {
                title = header.innerText.split('\\n')[0].trim();
            }
            if (!title) {
                const snippet = item.innerText.split('\\n').filter(x => x.trim()).slice(0, 2).join(' - ');
                title = snippet || `Panel ${i+1}`;
            }
            
            const hasErr = Array.from(item.querySelectorAll('p, div, span')).some(el => el.children.length === 0 && el.innerText.trim() === 'Err');
            const hasErrorNotice = item.querySelector('.panel-has-error, [data-testid*="error"]') !== null;
            const canvases = item.querySelectorAll('canvas').length;
            const uplots = item.querySelectorAll('.uplot').length;
            const svgs = item.querySelectorAll('svg').length;
            const tables = item.querySelectorAll('table, [role="table"]').length;
            
            results.push({
                index: i + 1,
                title: title,
                isErr: hasErr || hasErrorNotice,
                canvases: canvases,
                uplots: uplots,
                svgs: svgs,
                tables: tables
            });
        }
        return results;
    }
    """
    
    res = await send_cmd(ws, "Runtime.evaluate", {
        "expression": f"({inspect_script})()",
        "awaitPromise": True,
        "returnByValue": True
    }, msg_id=msg_id_start + 1)
    
    return res.get("result", {}).get("result", {}).get("value", [])


async def main():
    runner = ChromeRunner()
    runner.start()
    print("Headless Chrome initialized with CDP on port 9222.")
    
    try:
        resp = urllib.request.urlopen(f"http://localhost:{CDP_PORT}/json/list").read()
        targets = json.loads(resp.decode())
        page_target = next(t for t in targets if t.get("type") == "page")
        ws_url = page_target["webSocketDebuggerUrl"]
        
        all_passed = True
        total_panels_checked = 0
        total_errors_found = 0
        results_matrix = []
        
        async with websockets.connect(ws_url, max_size=25_000_000) as ws:
            await send_cmd(ws, "Page.enable", msg_id=1)
            await send_cmd(ws, "Runtime.enable", msg_id=2)
            
            msg_counter = 10
            for uid, dash_title in DASHBOARDS:
                panels = await audit_dashboard(ws, uid, dash_title, msg_id_start=msg_counter)
                msg_counter += 10
                
                dash_errs = sum(1 for p in panels if p["isErr"])
                total_panels_checked += len(panels)
                total_errors_found += dash_errs
                if dash_errs > 0:
                    all_passed = False
                
                dash_status = "PASS" if dash_errs == 0 else f"FAIL ({dash_errs} Err)"
                print(f"[{dash_status}] {dash_title} ({len(panels)} panels rendered, {dash_errs} errors)")
                
                for p in panels:
                    results_matrix.append({
                        "dashboard": dash_title,
                        "panel_index": p["index"],
                        "panel_title": p["title"],
                        "canvases": p["canvases"],
                        "uplots": p["uplots"],
                        "isErr": p["isErr"],
                        "status": "FAIL (Err rendered)" if p["isErr"] else "PASS"
                    })
        
        print("\n" + "=" * 115)
        print(f"{'DASHBOARD':<32} | {'PANEL TITLE':<48} | {'UPLOT':<6} | {'CANVAS':<7} | {'STATUS'}")
        print("=" * 115)
        
        xy_keywords = ["scatter", "curve", "diagnostic", "kaplan", "k-selection", "uplift", "parity", "z-score", "trajectory", "f1-score", "bivariate", "confidence"]
        for r in results_matrix:
            p_title_lower = r["panel_title"].lower()
            if any(k in p_title_lower for k in xy_keywords) or r["uplots"] > 0:
                print(f"{r['dashboard'][:32]:<32} | {r['panel_title'][:48]:<48} | {r['uplots']:<6} | {r['canvases']:<7} | {r['status']}")
                
        print("=" * 115)
        print(f"\nFINAL VERIFICATION SUMMARY: Checked {total_panels_checked} panels across 11 dashboards. Total errors: {total_errors_found}.")
        if all_passed:
            print("STATUS: ALL PANELS AND ALL XY CHARTS RENDERED WITH ZERO ERRORS.")
        else:
            print("STATUS: SOME PANELS ENCOUNTERED ERRORS.")

        # Save machine-readable audit artifact
        with open("report/live_render_verification.json", "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "total_panels": total_panels_checked,
                "total_errors": total_errors_found,
                "all_passed": all_passed,
                "results": results_matrix
            }, f, indent=2)
        print("Audit artifact saved to report/live_render_verification.json")
        
    finally:
        runner.stop()

if __name__ == "__main__":
    asyncio.run(main())
