"""Generate a small coherent demo profile. Fixed seed; relationships are causal."""
from __future__ import annotations

from fmcg_sales_intelligence.common.paths import PROJECT_ROOT
import argparse
import csv
import json
import math
import random
from datetime import date,timedelta
ROOT = PROJECT_ROOT; OUT=ROOT/"data/generated"
def write(name,cols,rows):
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/f"{name}.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--days",type=int,default=90);ap.add_argument("--stores",type=int,default=20);ap.add_argument("--skus",type=int,default=48);a=ap.parse_args()
    rng=random.Random(20260915); start=date(2024,1,1)
    all_cal=json.loads((ROOT/"data/metadata/donor_calibration.json").read_text(encoding="utf-8")); fav=all_cal["favorita"]; m5=all_cal["m5"]
    promo_rate=fav["promotion_rate"]; nonzero_rate=m5["nonzero_rate"]; median_units=fav["positive_sales_quantiles"]["0.5"]; promo_price_ratio=m5["price_to_series_max_quantiles"]["0.25"]
    category_names=["Carbonated Soft Drinks","Energy Drinks","Juice","Water","RTD Tea","Coffee"]
    brand_names=["Northstar Cola","Volt","Orchard","ClearSpring","Leafline","RoastGo"]
    regions=[{"region_id":i,"region_name":n,"country":"Ukraine"} for i,n in enumerate(["North","South","East","West"],1)]
    categories=[{"category_id":i,"category_name":n,"parent_category_id":"","description":"Synthetic beverage category"} for i,n in enumerate(category_names,1)]
    brands=[{"brand_id":i,"brand_name":n,"manufacturer":"FMCG Demo Company","partner_brand":False,"active":True,"provenance":"synthetic"} for i,n in enumerate(brand_names,1)]
    products=[];skus=[]
    for sku in range(1,a.skus+1):
        product=sku; category=1+(sku-1)%6; volume=[250,330,500,1000,1500,2000][(sku-1)%6]; package=["CAN","CAN","PET","PET","PET","PET"][(sku-1)%6]
        products.append({"product_id":product,"category_id":category,"brand_id":category,"product_name":f"{brand_names[category-1]} Line {1+(sku-1)//6}","description":"Synthetic beverage product line","sugar_free":sku%5==0,"active":True,"provenance":"synthetic"})
        base=round(1.1+sku*.07,2)
        skus.append({"sku_id":sku,"product_id":product,"sku_code":f"SKU-{sku:04d}","flavor":["Original","Citrus","Berry","Orange"][sku%4],"package_type":package,"volume_ml":volume,"units_per_case":24 if volume<=500 else 12,"base_price":base,"standard_cost":round(base*.55,2),"active":True,"provenance":"synthetic"})
    stores=[{"store_id":i,"external_store_code":f"STORE-{i:03d}","store_name":f"Synthetic Store {i:03d}","region_id":1+(i-1)%4,"city":f"City {1+(i-1)%8}","store_type":["supermarket","discount","convenience","horeca"][i%4],"channel":["modern_trade","traditional_trade","convenience","horeca","ecommerce"][i%5],"floor_area_m2":200+i*35,"active":True,"opened_at":date(2018+(i%6),1+(i%12),1),"provenance":"synthetic"} for i in range(1,a.stores+1)]
    warehouses=[{"warehouse_id":i,"warehouse_code":f"WH-{i:02d}","warehouse_name":f"Regional Warehouse {i}","region_id":i,"city":f"City {i}","capacity_units":100000,"active":True} for i in range(1,5)]
    promotions=[]
    for p in range(1,4):
        ps=start+timedelta(days=(p-1)*30);promotions.append({"promotion_id":p,"promotion_name":f"Monthly Campaign {p}","promotion_type":"price_reduction","start_date":ps,"end_date":min(ps+timedelta(days=29),start+timedelta(days=a.days-1)),"discount_type":"percentage","discount_value":round((1-promo_price_ratio)*100,2),"description":"Synthetic campaign calibrated from donor price ratios","provenance":"synthetic"})
    write("categories",list(categories[0]),categories);write("brands",list(brands[0]),brands);write("products",list(products[0]),products);write("skus",list(skus[0]),skus)
    write("regions",list(regions[0]),regions);write("stores",list(stores[0]),stores);write("warehouses",list(warehouses[0]),warehouses);write("promotions",list(promotions[0]),promotions)
    promotion_skus=[{"promotion_id":p,"sku_id":s} for p in range(1,4) for s in range(1,a.skus+1)]
    promotion_stores=[{"promotion_id":p,"store_id":s} for p in range(1,4) for s in range(1,a.stores+1)]
    write("promotion_skus",list(promotion_skus[0]),promotion_skus);write("promotion_stores",list(promotion_stores[0]),promotion_stores)
    # Warehouse/SKU policies are heterogeneous and expressed in expected days
    # of demand. Replenishment is ordered after depletion and arrives later;
    # no stockout label is injected directly.
    policies={}
    state={}
    pending={(w,s):None for w in range(1,5) for s in range(1,a.skus+1)}
    for w in range(1,5):
        for sku in range(1,a.skus+1):
            expected_daily=max(3,median_units*(a.stores/4)*(1.5/(sku**.18)))
            reorder=max(8,int(expected_daily*rng.uniform(4.0,6.0)))
            safety=max(4,int(expected_daily*rng.uniform(1.5,2.8)))
            target=max(reorder+safety,int(expected_daily*rng.uniform(10.0,14.0)))
            policies[(w,sku)]={"expected_daily":expected_daily,"reorder":reorder,"safety":safety,"target":target}
            state[(w,sku)]=max(1,int(expected_daily*rng.uniform(7.0,13.0)))
    sales=[]; daily_demand=[]; inv=[]
    for di in range(a.days):
        d=start+timedelta(days=di); seasonal=1+.18*math.sin(2*math.pi*di/365); weekend=1.18 if d.weekday()>=5 else 1
        opening=dict(state); receipts={(w,s):0 for w in range(1,5) for s in range(1,a.skus+1)}
        for key,order in list(pending.items()):
            if order and order[0]<=di:
                receipts[key]=order[1];state[key]+=order[1];pending[key]=None
        fulfilled={(w,s):0 for w in range(1,5) for s in range(1,a.skus+1)};requested={(w,s):0 for w in range(1,5) for s in range(1,a.skus+1)}
        lost={(w,s):0 for w in range(1,5) for s in range(1,a.skus+1)}
        for st in range(1,a.stores+1):
            size=0.7+1.1*(st/a.stores)
            for sku in range(1,a.skus+1):
                popularity=median_units*(1.8/(sku**0.25)); promo=rng.random()<promo_rate; base_price=1.1+sku*.07; price=round(base_price*(promo_price_ratio if promo else 1),2)
                active_probability=min(.95,nonzero_rate*size*(1.6/(sku**.15)))
                demand_spike=rng.uniform(1.7,3.0) if rng.random()<(.025+(.025 if promo else 0)) else 1
                latent=0 if rng.random()>active_probability else max(0,int(rng.gauss(popularity*size*seasonal*weekend*(1.25 if promo else 1)*demand_spike,1.8)))
                warehouse=1+(st-1)%4;available_before=state[(warehouse,sku)];sold=min(latent,available_before);lost_units=latent-sold
                daily_demand.append({"observation_date":d,"store_id":st,"sku_id":sku,"warehouse_id":warehouse,"requested_demand_units":latent,"realized_sales_units":sold,"lost_sales_units":lost_units,"demand_censored_by_inventory":lost_units>0,"inventory_available_before":available_before,"promotion_id":1+di//30 if promo else ""})
                requested[(warehouse,sku)]+=latent;lost[(warehouse,sku)]+=lost_units
                if sold:
                    gross=round(sold*base_price,2); net=round(sold*price,2); cost=round((.55+sku*.035),2)
                    sales.append({"sale_date":d,"store_id":st,"sku_id":sku,"quantity_units":sold,"unit_price":price,"gross_revenue":gross,"discount_amount":round(gross-net,2),"net_revenue":net,"unit_cost":cost,"gross_profit":round(net-sold*cost,2),"promotion_id":1+di//30 if promo else "","provenance":"synthetic","external_source":"favorita-m5-calibrated","external_id":""})
                    fulfilled[(warehouse,sku)]+=sold; state[(warehouse,sku)]-=sold
        for w in range(1,5):
            for sku in range(1,a.skus+1):
                key=(w,sku);policy=policies[key];ordered=0;lead="";expected=""
                if state[key]<policy["reorder"] and pending[key] is None:
                    lead_days=rng.randint(2,5)+(rng.randint(1,3) if rng.random()<.10 else 0)
                    ordered=max(policy["reorder"],policy["target"]-state[key]);pending[key]=(di+lead_days,ordered)
                    lead=lead_days;expected=start+timedelta(days=di+lead_days)
                inv.append({"snapshot_date":d,"warehouse_id":w,"sku_id":sku,"opening_stock_quantity":opening[key],"stock_quantity":state[key],"reserved_quantity":0,"reorder_point":policy["reorder"],"safety_stock":policy["safety"],"replenishment_quantity":receipts[key],"replenishment_ordered_quantity":ordered,"replenishment_lead_time_days":lead,"expected_replenishment_date":expected,"demand_requested":requested[key],"demand_fulfilled":fulfilled[key],"lost_sales_quantity":lost[key],"adjustment_quantity":0})
    write("sales",list(sales[0]),sales);write("daily_demand",list(daily_demand[0]),daily_demand);write("inventory",list(inv[0]),inv)
    prices=[]
    for st in range(1,a.stores+1):
        for sku in range(1,a.skus+1):
            base=round(1.1+sku*.07,2)
            for offset in range(0,a.days,7):
                vf=start+timedelta(days=offset);vt=min(vf+timedelta(days=6),start+timedelta(days=a.days-1)); ratio=promo_price_ratio if (offset//7+st+sku)%5==0 else 1
                prices.append({"price_id":len(prices)+1,"store_id":st,"sku_id":sku,"valid_from":vf,"valid_to":vt,"regular_price":base,"selling_price":round(base*ratio,2),"provenance":"synthetic"})
    write("product_prices",list(prices[0]),prices)
    calibration=all_cal["instacart"]
    q=calibration["basket_size_quantiles"]; basket_choices=[int(q["0.25"]),int(q["0.5"]),int(q["0.75"]),int(q["0.9"]),int(q["0.95"])]
    orders=[];items=[]; item_id=1
    for oid in range(1,a.stores*100+1):
        st=1+(oid-1)%a.stores; od=start+timedelta(days=rng.randrange(a.days)); size=rng.choices(basket_choices,weights=[25,25,25,15,10])[0]
        chosen=[]; sku_population=list(range(1,a.skus+1)); sku_weights=[1/(s**.7) for s in sku_population]
        while len(chosen)<min(size,a.skus):
            sku=rng.choices(sku_population,weights=sku_weights)[0]
            if sku not in chosen:chosen.append(sku)
        subtotal=discount=0; staged=[]
        for sku in chosen:
            qty=rng.choices([1,2,3,4,6,12],weights=[35,30,15,10,7,3])[0]; price=round(1.1+sku*.07,2); disc=round(qty*price*.1,2) if (oid+sku)%11==0 else 0
            subtotal+=qty*price;discount+=disc;staged.append((sku,qty,price,disc))
        orders.append({"order_id":oid,"order_code":f"DEV-{oid:08d}","store_id":st,"order_date":od,"requested_delivery_date":od+timedelta(days=3),"actual_delivery_date":od+timedelta(days=2+rng.randrange(3)),"status":"delivered","subtotal":round(subtotal,2),"discount_amount":round(discount,2),"total_amount":round(subtotal-discount,2),"provenance":"synthetic","external_source":"instacart-calibrated","external_id":""})
        for sku,qty,price,disc in staged:
            items.append({"order_item_id":item_id,"order_id":oid,"sku_id":sku,"quantity":qty,"unit_price":price,"discount_amount":disc});item_id+=1
    write("orders",list(orders[0]),orders);write("order_items",list(items[0]),items)
    deliveries=[];delivery_items=[]
    for i,o in enumerate(orders,1):
        deliveries.append({"delivery_id":i,"delivery_code":f"DEL-{i:08d}","order_id":i,"warehouse_id":1+(int(o["store_id"])-1)%4,"store_id":o["store_id"],"shipped_at":f'{o["order_date"]} 08:00:00',"delivered_at":f'{o["actual_delivery_date"]} 12:00:00',"status":"delivered"})
    for x in items:delivery_items.append({"delivery_id":x["order_id"],"sku_id":x["sku_id"],"quantity":x["quantity"]})
    write("deliveries",list(deliveries[0]),deliveries);write("delivery_items",list(delivery_items[0]),delivery_items)
    print(f"generated sales={len(sales)} daily_demand={len(daily_demand)} inventory={len(inv)} orders={len(orders)} order_items={len(items)} prices={len(prices)} deliveries={len(deliveries)}")
if __name__=="__main__":main()
