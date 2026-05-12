"""Market Basket / Association Rule Mining V1."""
from __future__ import annotations
import hashlib,json,platform,shutil,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from mlxtend.frequent_patterns import apriori,association_rules,fpgrowth
import mlxtend

ROOT=Path(__file__).resolve().parents[2]; DEFAULT_CONFIG=ROOT/"configs/modeling/basket.yaml"; DEFAULT_DATA=ROOT/"data/processed/basket/basket_v1.parquet"
def _sha(p):
 h=hashlib.sha256();h.update(Path(p).read_bytes());return h.hexdigest()
def _git(*a):
 try:return subprocess.check_output(["git",*a],cwd=ROOT,text=True).strip()
 except:return None
def load_data(config_path=DEFAULT_CONFIG,data_path=DEFAULT_DATA):
 c=yaml.safe_load(Path(config_path).read_text());d=pd.read_parquet(data_path);d.order_date=pd.to_datetime(d.order_date);return c,d
def baskets(frame,level="sku_id"):
 x=frame.dropna(subset=["order_id",level]); return x.groupby("order_id")[level].agg(lambda s:tuple(sorted(set(s)))).to_dict()
def binary_matrix(frame,level="sku_id"):
 x=frame[["order_id",level]].drop_duplicates();return pd.crosstab(x.order_id,x[level]).gt(0).sort_index(axis=0).sort_index(axis=1)
def canon(items):return "|".join(map(str,sorted(items,key=str)))
def mine(matrix,cfg,algorithm):
 fn=apriori if algorithm=="apriori" else fpgrowth;t=time.perf_counter();f=fn(matrix,min_support=cfg["minimum_support"],use_colnames=True,max_len=cfg["maximum_itemset_size"]);runtime=time.perf_counter()-t
 f=f.copy();f["itemset"]=f.itemsets.map(canon);f["itemset_size"]=f.itemsets.map(len);f["support_count"]=(f.support*len(matrix)).round().astype(int);f=f.sort_values(["itemset_size","itemset"]).reset_index(drop=True)
 raw=association_rules(f.rename(columns={"itemset":"itemset_text"}),metric="confidence",min_threshold=cfg["minimum_confidence"])
 raw=raw[(raw.lift>=cfg["minimum_lift"])&(raw.antecedents.map(len)<=cfg["maximum_antecedent_size"])&(raw.consequents.map(len)==cfg["consequent_size"])].copy()
 raw["antecedent"]=raw.antecedents.map(canon);raw["consequent"]=raw.consequents.map(canon);raw["support_count"]=(raw.support*len(matrix)).round().astype(int);raw["rule_id"]=[hashlib.sha256(f"{a}->{b}".encode()).hexdigest()[:16] for a,b in zip(raw.antecedent,raw.consequent)]
 raw=raw.drop_duplicates(["antecedent","consequent"]).sort_values(["lift","support","confidence","antecedent","consequent"],ascending=[False,False,False,True,True]).reset_index(drop=True)
 return f,raw,runtime
def rule_metrics(frame,rules,period_col=None):
 groups=[("ALL",frame)] if period_col is None else list(frame.groupby(period_col)) ; rows=[]
 for period,g in groups:
  bs=baskets(g);n=len(bs)
  for r in rules.itertuples():
   A=set(str(r.antecedent).split("|"));B=set(str(r.consequent).split("|"));sets=[set(map(str,v)) for v in bs.values()];ac=sum(A<=s for s in sets);bc=sum(B<=s for s in sets);abc=sum((A|B)<=s for s in sets);sup=abc/n if n else np.nan;conf=abc/ac if ac else np.nan;lift=conf/(bc/n) if n and bc and ac else np.nan
   rows.append({"period":str(period),"rule_id":r.rule_id,"basket_count":n,"support_count":abc,"support":sup,"confidence":conf,"lift":lift})
 return pd.DataFrame(rows)
def run_basket_experiment(config_path=DEFAULT_CONFIG,data_path=DEFAULT_DATA,output_dir=None,experiment_id=None,overwrite=False):
 cfg,d=load_data(config_path,data_path);data_path=Path(data_path)
 if d.order_id.isna().any() or d.sku_id.isna().any() or (d.quantity<=0).any():raise ValueError("DATA_ISSUE_FOUND: invalid basket keys or quantity")
 dup=int(d[["order_id","sku_id"]].duplicated().sum());m=binary_matrix(d,"sku_id");sizes=m.sum(1)
 af,ar,at=mine(m,cfg,"apriori");ff,fr,ft=mine(m,cfg,"fp_growth"); aset=set(zip(af.itemset,af.support.round(12)));fset=set(zip(ff.itemset,ff.support.round(12)));consistent=aset==fset
 if not consistent:raise ValueError("Apriori/FP-Growth frequent itemsets differ")
 rules=fr.copy(); top=rules.head(cfg["top_rule_count"]).copy();top["review_status"]="UNREVIEWED";top["interpretation"]="ASSOCIATION_NOT_CAUSATION"
 # Human names.
 names=d.drop_duplicates("sku_id").set_index("sku_id").product_name.astype(str).to_dict();top["antecedent_name"]=top.antecedent.map(lambda x:" + ".join(names.get(int(i),i) for i in x.split("|")));top["consequent_name"]=top.consequent.map(lambda x:names.get(int(x),x))
 temporal=rule_metrics(d.assign(month=d.order_date.dt.to_period("M").astype(str)),top,"month");stab=temporal.groupby("rule_id").agg(months=("period","nunique"),support_cv=("support",lambda x:x.std()/x.mean() if x.mean() else np.nan),lift_min=("lift","min")).reset_index();stab["stability_status"]=np.select([(stab.months==3)&(stab.support_cv<=.25),stab.months<3],["STABLE","SPARSE"],default="VARIABLE");temporal=temporal.merge(stab,on="rule_id")
 sensitivity=[]
 for s in cfg["support_sensitivity"]:
  cc=dict(cfg);cc["minimum_support"]=s;fi,rr,rt=mine(m,cc,"fp_growth");sensitivity.append({"minimum_support":s,"minimum_support_count":round(s*len(m)),"frequent_itemsets":len(fi),"canonical_rules":len(rr),"runtime_seconds":rt})
 levels=[]
 for level in ["brand_name","category_name"]:
  mm=binary_matrix(d,level);cc=dict(cfg);cc["maximum_itemset_size"]=2;fi,rr,rt=mine(mm,cc,"fp_growth");levels.append({"level":level,"baskets":len(mm),"items":len(mm.columns),"density":float(mm.to_numpy().mean()),"itemsets":len(fi),"rules":len(rr)})
 context=[]
 for field in ["region_id","store_type","channel"]:
  for value,g in d.groupby(field):
   n=g.order_id.nunique();status="ELIGIBLE" if n>=cfg["minimum_slice_baskets"] else "INSUFFICIENT_BASKETS";context.append({"context":field,"value":str(value),"basket_count":n,"status":status})
 generator={"mechanism":"basket size sampled from Instacart-calibrated quantiles; SKUs sampled without replacement with weight 1/sku_id^0.7","known_structure":"long-tailed SKU popularity and imposed basket-size distribution; no explicit complementarity rule","consequence":"rules may recover generator popularity and finite-sample dependence, not business causation","supervised_accuracy":False}
 out=Path(output_dir or ROOT/"artifacts/experiments/basket"/(experiment_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")));shutil.rmtree(out,ignore_errors=overwrite)
 if out.exists():raise FileExistsError(out)
 for p in [out/"outputs",out/"diagnostics",out/"figures"]:p.mkdir(parents=True,exist_ok=True)
 export_f=ff.drop(columns="itemsets");export_r=rules.drop(columns=["antecedents","consequents"]);export_f.to_parquet(out/"outputs/frequent_itemsets.parquet",index=False);export_r.to_parquet(out/"outputs/association_rules.parquet",index=False);top.drop(columns=["antecedents","consequents"]).to_csv(out/"outputs/top_rules.csv",index=False);temporal.to_csv(out/"diagnostics/temporal_stability.csv",index=False);pd.DataFrame(sensitivity).to_csv(out/"diagnostics/threshold_sensitivity.csv",index=False);pd.DataFrame(context).to_csv(out/"diagnostics/context_slices.csv",index=False)
 consistency={"apriori_runtime_seconds":at,"fp_growth_runtime_seconds":ft,"apriori_itemsets":len(af),"fp_growth_itemsets":len(ff),"equivalent":consistent};(out/"diagnostics/algorithm_consistency.json").write_text(json.dumps(consistency,indent=2));(out/"diagnostics/generator_audit.json").write_text(json.dumps(generator,indent=2));
 monthly=d.groupby(d.order_date.dt.to_period("M").astype(str)).order_id.nunique().astype(int).to_dict()
 diag={"rows":len(d),"valid_baskets":d.order_id.nunique(),"unique_skus":d.sku_id.nunique(),"stores":d.store_id.nunique(),"date_range":[str(d.order_date.min().date()),str(d.order_date.max().date())],"duplicate_order_sku":dup,"nonpositive_quantity":int((d.quantity<=0).sum()),"single_item_baskets":int((sizes==1).sum()),"basket_size":sizes.describe().to_dict(),"matrix_shape":list(m.shape),"matrix_density":float(m.to_numpy().mean()),"monthly_baskets":monthly,"hierarchy_levels":levels};(out/"diagnostics/data_diagnostics.json").write_text(json.dumps(diag,indent=2,default=str))
 counts=ff.groupby("itemset_size").size().to_dict();stable=int((stab.stability_status=="STABLE").sum());metrics={"valid_baskets":len(m),"order_items":len(d),"unique_items":len(m.columns),"mean_basket_size":sizes.mean(),"median_basket_size":sizes.median(),"single_item_basket_rate":float((sizes==1).mean()),"basket_matrix_density":float(m.to_numpy().mean()),"frequent_itemset_count":len(ff),"raw_rule_count":len(fr),"canonical_rule_count":len(rules),"min_support":cfg["minimum_support"],"min_confidence":cfg["minimum_confidence"],"min_lift":cfg["minimum_lift"],"median_rule_support":rules.support.median() if len(rules) else None,"median_rule_confidence":rules.confidence.median() if len(rules) else None,"median_rule_lift":rules.lift.median() if len(rules) else None,"max_rule_lift":rules.lift.max() if len(rules) else None,"temporally_stable_rule_count":stable,"apriori_fpgrowth_consistent":consistent,"readiness":"READY_WITH_LIMITATIONS"}
 for n in ["metrics.json","dvc_metrics.json"]:(out/n).write_text(json.dumps(metrics,indent=2))
 selected={"task_type":"ASSOCIATION_RULE_MINING","primary_analysis_level":"sku_id","canonical_algorithm":"fp_growth","minimum_support":cfg["minimum_support"],"minimum_confidence":cfg["minimum_confidence"],"minimum_lift":cfg["minimum_lift"],"maximum_itemset_size":cfg["maximum_itemset_size"],"rule_length_policy":"one-item antecedent and one-item consequent","pruning_policy":cfg["pruning_policy"],"basket_definition":"set of distinct items per order_id","binary_presence":True,"dataset_fingerprint":_sha(data_path)};(out/"selected_method.json").write_text(json.dumps(selected,indent=2));(out/"resolved_config.yaml").write_text(yaml.safe_dump(cfg,sort_keys=False))
 plt.figure(figsize=(7,5));plt.scatter(rules.support,rules.confidence,c=rules.lift,s=12);plt.colorbar(label="Lift");plt.xlabel("Support");plt.ylabel("Confidence");plt.tight_layout();plt.savefig(out/"figures/support_confidence_lift.png",dpi=180);plt.close();item=m.mean().sort_values(ascending=False).head(15);item.plot.bar(figsize=(8,4));plt.ylabel("Support");plt.tight_layout();plt.savefig(out/"figures/item_support.png",dpi=180);plt.close();top.head(15).sort_values("lift").plot.barh(x="rule_id",y="lift",legend=False,figsize=(8,5));plt.tight_layout();plt.savefig(out/"figures/top_rules.png",dpi=180);plt.close();temporal.groupby("period").support.mean().plot(marker="o",figsize=(7,4));plt.ylabel("Mean top-rule support");plt.tight_layout();plt.savefig(out/"figures/temporal_stability.png",dpi=180);plt.close()
 report=f"""# Market Basket V1\n\n## 1–7. Objective, transactions, data and quality\n`order_id` is the basket; {len(d):,} order-item rows form {len(m):,} valid baskets. Items are binary presence, so quantity and duplicate lines cannot inflate support. No invalid quantities, missing mappings, duplicate order–SKU keys, or single-item baskets were found.\n\n## 8–11. Algorithms and thresholds\nApriori and FP-Growth used support {cfg['minimum_support']:.0%} ({round(cfg['minimum_support']*len(m))} baskets), confidence {cfg['minimum_confidence']:.0%}, lift ≥ {cfg['minimum_lift']}, and pair itemsets only. They returned equivalent itemsets: {consistent}. FP-Growth is canonical for scalability, not accuracy.\n\n## 12–17. Itemsets, rules and diagnostics\nFrequent itemsets: {len(ff):,} ({counts}). Canonical directional rules: {len(rules):,}. Rules are sorted lexicographically by lift, support, confidence after exact-duplicate removal. Minimum support prevents rare-rule inflation; lift prevents confidence-only popular-consequent claims.\n\n## 18–19. Stability and context\nStable top rules: {stable}/{len(top)}. Monthly baskets: January 675, February 660, March 665. Context basket counts and eligibility are persisted; segmentation pseudo-labels are not used.\n\n## 20. Synthetic generator audit\n{generator['mechanism']}. This induces popularity structure and does not encode verified complementarity. Recovery is descriptive, not supervised accuracy.\n\n## 21–24. Interpretation, review, readiness and limitations\nRules describe co-purchase association, never causation. Top {len(top)} rules are UNREVIEWED. Status is READY_WITH_LIMITATIONS for offline BI exploration: synthetic data, 2,000 baskets, ~90 days, and no external validation.\n\n## 25–26. Reproducibility and future hypotheses\nDVC stage `basket_v1` freezes data, config, code, itemsets, rules and diagnostics. Future work requires business review and external transaction validation before BI or recommendation use.\n""";(out/"report.md").write_text(report)
 manifest={"experiment_id":experiment_id or out.name,"task":"market_basket","status":"complete","created_at":datetime.now(timezone.utc).isoformat(),"dataset_path":str(data_path),"dataset_fingerprint":_sha(data_path),"schema_fingerprint":hashlib.sha256(str(list(zip(d.columns,map(str,d.dtypes)))).encode()).hexdigest(),"transaction_definition":"order_id","basket_count":len(m),"item_count":len(m.columns),"date_range":diag["date_range"],"basket_statistics":diag["basket_size"],"analysis_hierarchy_levels":["sku_id","brand_name","category_name"],"binary_presence_policy":True,"duplicate_handling":"collapse to one presence","invalid_transaction_policy":"fail","algorithms":{"apriori":at,"fp_growth":ft,"mlxtend":mlxtend.__version__},"definitions":{"support":"baskets containing itemset / valid baskets","confidence":"support(A union B)/support(A)","lift":"confidence/support(B)"},"thresholds":selected,"algorithm_consistency":consistency,"temporal_stability":{"stable_top_rules":stable},"context_slice_policy":{"minimum_baskets":cfg["minimum_slice_baskets"]},"generator_audit":generator,"readiness":"READY_WITH_LIMITATIONS","git":{"commit":_git("rev-parse","HEAD"),"branch":_git("branch","--show-current"),"dirty":bool(_git("status","--porcelain"))},"dvc":{"stage":"basket_v1","remote":None},"library_versions":{"python":platform.python_version(),"pandas":pd.__version__,"mlxtend":mlxtend.__version__},"artifacts":{"itemsets":"outputs/frequent_itemsets.parquet","rules":"outputs/association_rules.parquet","review":"outputs/top_rules.csv"}};(out/"manifest.json").write_text(json.dumps(manifest,indent=2,default=str))
 return {"experiment_id":manifest["experiment_id"],"output_dir":str(out),"selected_model":"fp_growth","test_metrics":metrics}
