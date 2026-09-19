from pathlib import Path
import pandas as pd
from fmcg_sales_intelligence.science import run_experiment
from fmcg_sales_intelligence.science.basket import binary_matrix,baskets,canon,load_data,mine,rule_metrics
ROOT=Path(__file__).resolve().parents[2]
def test_basket_grain_binary_quantity_and_duplicates():
 c,d=load_data(); assert d.order_id.nunique()==2000 and len(d)==24370 and not d[["order_id","sku_id"]].duplicated().any()
 x=pd.DataFrame({"order_id":[1,1,1,2],"sku_id":[1,1,2,2],"quantity":[5,2,1,8]});b=baskets(x);m=binary_matrix(x)
 assert b[1]==(1,2) and m.loc[1,1] and m.loc[1,2] and m.sum().sum()==3
def test_hierarchy_dedup_and_single_item():
 x=pd.DataFrame({"order_id":[1,1,2],"sku_id":[1,2,3],"brand_name":["A","A","B"],"quantity":[1,1,1]});assert baskets(x,"brand_name")[1]==("A",) and binary_matrix(x,"brand_name").shape==(2,2)
def test_algorithms_equivalent_and_thresholds():
 c,d=load_data();m=binary_matrix(d);a,ar,_=mine(m,c,"apriori");f,fr,_=mine(m,c,"fp_growth")
 assert set(zip(a.itemset,a.support.round(12)))==set(zip(f.itemset,f.support.round(12)))
 assert (fr.support>=c["minimum_support"]).all() and (fr.confidence>=c["minimum_confidence"]).all() and (fr.lift>=c["minimum_lift"]).all()
 assert (fr.antecedents.map(len)==1).all() and (fr.consequents.map(len)==1).all()
def test_support_confidence_lift_and_direction():
 d=pd.DataFrame({"order_id":[1,1,2,2,3],"sku_id":[1,2,1,2,1],"order_date":pd.to_datetime(["2024-01-01"]*5)});c={"minimum_support":.1,"minimum_confidence":0,"minimum_lift":0,"maximum_itemset_size":2,"maximum_antecedent_size":1,"consequent_size":1}
 _,r,_=mine(binary_matrix(d),c,"fp_growth");ab=r[(r.antecedent=="1")&(r.consequent=="2")].iloc[0];ba=r[(r.antecedent=="2")&(r.consequent=="1")].iloc[0]
 assert ab.support_count==2 and ab.support==2/3 and ab.confidence==2/3 and ab.lift==1 and ba.confidence==1
def test_canonical_ids_and_temporal_metrics():
 c,d=load_data();_,r,_=mine(binary_matrix(d),c,"fp_growth");assert r.rule_id.is_unique and canon({2,1})=="1|2";assert len(rule_metrics(d.assign(month=d.order_date.dt.month),r.head(2),"month"))==6
def test_public_api_artifacts_no_supervised_metrics(tmp_path):
 z=run_experiment("basket",output_dir=tmp_path/"b",experiment_id="test",overwrite=True);o=Path(z["output_dir"]);t=pd.read_csv(o/"outputs/top_rules.csv")
 assert set(t.review_status)=={"UNREVIEWED"} and not {"accuracy","precision","recall","f1","roc_auc"}&set(z["test_metrics"])
