"""Derive compact empirical parameters without materializing large donor tables."""
from __future__ import annotations

from fmcg_sales_intelligence.common.paths import PROJECT_ROOT
import json, zipfile, math
import pandas as pd
ROOT = PROJECT_ROOT
PROCESSED=ROOT/"data/processed"; PROCESSED.mkdir(parents=True,exist_ok=True)
def instacart():
    archive=next((ROOT/"data/raw/instacart").glob("*.zip"))
    with zipfile.ZipFile(archive) as z:
        names=z.namelist(); prior=next(n for n in names if n.endswith("order_products__prior.csv"))
        orders=next(n for n in names if n.endswith("orders.csv"))
        counts={}; reordered=total=0
        with z.open(prior) as f:
            for chunk in pd.read_csv(f,usecols=["order_id","reordered"],chunksize=1_000_000):
                vc=chunk.groupby("order_id").size()
                for size,n in vc.value_counts().items(): counts[int(size)]=counts.get(int(size),0)+int(n)
                reordered+=int(chunk["reordered"].sum()); total+=len(chunk)
        # Chunk boundaries split a small number of orders; quantiles are therefore approximate.
        def weighted_quantile(q):
            target=q*sum(counts.values()); cumulative=0
            for size,n in sorted(counts.items()):
                cumulative+=n
                if cumulative>=target:return float(size)
            return float(max(counts))
        with z.open(orders) as f: od=pd.read_csv(f,usecols=["order_dow","order_hour_of_day","days_since_prior_order"])
    return {"source":"psparks/instacart-market-basket-analysis","basket_size_quantiles":{str(q):weighted_quantile(q) for q in (.25,.5,.75,.9,.95)},"reorder_rate":reordered/total,"order_dow_distribution":od.order_dow.value_counts(normalize=True).sort_index().round(6).to_dict(),"order_hour_distribution":od.order_hour_of_day.value_counts(normalize=True).sort_index().round(6).to_dict(),"days_since_prior_quantiles":{str(q):float(od.days_since_prior_order.quantile(q)) for q in (.25,.5,.75,.9)},"limitations":"Basket quantiles are approximate because chunk boundaries can split orders; used only as generator calibration."}
def favorita():
    archive=next((ROOT/"data/raw/favorita").glob("*.zip"))
    with zipfile.ZipFile(archive) as z:
        names=z.namelist()
        def member(end):return next(n for n in names if n.endswith(end))
        with z.open(member("stores.csv")) as f:stores=pd.read_csv(f)
        with z.open(member("items.csv")) as f:items=pd.read_csv(f)
        selected_stores=[]
        for _,g in stores.sort_values(["type","cluster","store_nbr"]).groupby("type"):
            selected_stores += g.iloc[[0,-1]]["store_nbr"].drop_duplicates().astype(int).tolist()
        per_family=max(1,math.ceil(400/items.family.nunique())); selected_items=[]
        for _,g in items.sort_values(["family","class","item_nbr"]).groupby("family"):
            step=max(1,len(g)//per_family);selected_items += g.iloc[::step].head(per_family).item_nbr.astype(int).tolist()
        frames=[]
        with z.open(member("train.csv")) as f:
            for chunk in pd.read_csv(f,chunksize=1_000_000,parse_dates=["date"]):
                x=chunk[(chunk.date.between("2016-01-01","2016-12-31")) & chunk.store_nbr.isin(selected_stores) & chunk.item_nbr.isin(selected_items)]
                if len(x):frames.append(x)
        subset=pd.concat(frames,ignore_index=True);subset.to_parquet(PROCESSED/"favorita_dev_subset.parquet",index=False)
    return {"source":"evgeniypolin/favorita-grocery-sales-forecasting","upstream":"favorita-grocery-sales-forecasting competition","window":["2016-01-01","2016-12-31"],"stores":len(set(selected_stores)),"items":len(set(selected_items)),"rows":len(subset),"promotion_rate":float(subset.onpromotion.fillna(False).mean()),"positive_sales_quantiles":{str(q):float(subset.loc[subset.unit_sales>0,"unit_sales"].quantile(q)) for q in (.25,.5,.75,.9,.95)},"negative_return_rate":float((subset.unit_sales<0).mean()),"selection":"Two stores per store type across cluster ordering; up to 400 items stratified across family/class; one continuous full-year window.","limitations":"Mirror license is unspecified. Subset is representative by dimensions, not a probability sample of the enterprise."}
def m5():
    raw=ROOT/"data/raw/m5"; calendar=pd.read_csv(raw/"calendar.csv"); sales=pd.read_csv(raw/"sales_train_evaluation.csv")
    selected=[]
    for _,g in sales.sort_values(["cat_id","dept_id","store_id","item_id"]).groupby(["cat_id","store_id"]):
        selected.append(g.iloc[::max(1,len(g)//40)].head(40))
    sample=pd.concat(selected,ignore_index=True);sample.to_parquet(PROCESSED/"m5_sales_subset.parquet",index=False)
    keys=sample[["store_id","item_id"]].drop_duplicates(); price_parts=[]
    for chunk in pd.read_csv(raw/"sell_prices.csv",chunksize=1_000_000):
        price_parts.append(chunk.merge(keys,on=["store_id","item_id"],how="inner"))
    prices=pd.concat(price_parts,ignore_index=True);prices.to_parquet(PROCESSED/"m5_price_subset.parquet",index=False)
    day=[c for c in sample if c.startswith("d_")];vals=sample[day].to_numpy()
    grp=prices.groupby(["store_id","item_id"]).sell_price
    ratio=(prices.sell_price/grp.transform("max")).dropna()
    return {"source":"Zenodo 10.5281/zenodo.10203108","upstream":"M5 Forecasting Accuracy / Mcompetitions","series":len(sales),"items":int(sales.item_id.nunique()),"stores":int(sales.store_id.nunique()),"days":len(day),"calendar_rows":len(calendar),"sample_series":len(sample),"price_rows_in_subset":len(prices),"daily_units_quantiles":{str(q):float(pd.Series(vals.ravel()).quantile(q)) for q in (.5,.75,.9,.95,.99)},"nonzero_rate":float((vals>0).mean()),"price_to_series_max_quantiles":{str(q):float(ratio.quantile(q)) for q in (.05,.25,.5,.75,.95)},"schema_verified":True,"md5_verified":True,"limitations":"Walmart hierarchy and prices are statistical donors only; identifiers are never joined to Favorita or canonical SKUs."}
def main():
    result={"instacart":instacart(),"favorita":favorita(),"m5":m5()}
    out=ROOT/"data/metadata/donor_calibration.json";out.write_text(json.dumps(result,indent=2),encoding="utf-8");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
