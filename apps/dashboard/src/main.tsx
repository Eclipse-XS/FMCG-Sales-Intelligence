import React, {useEffect, useState} from "react";
import {createRoot} from "react-dom/client";
import ReactECharts from "echarts-for-react";
import {api} from "./api";
import "./styles.css";

type Summary={date_from:string,date_to:string,units:number,revenue:number,average_selling_price:number,active_stores:number,active_skus:number,freshness_note:string};
type Point={date:string,units:number,revenue:number};
type Breakdown={key:string,units:number,revenue:number};
type Profile={profile_id:string,display_name:string,disclaimer:string,labels:Record<string,string>,theme:Record<string,string>};
type Model={name:string,version:string,task:string,ready:boolean,prediction_horizon:string,target:string,limitation:string};
type Capability={capability:string,status:string};
type Artifact={name:string,status:string,caveat:string,total:number,items:Record<string,unknown>[]};
const pages=["Home","Sales Overview","Brand / Product","Store / Outlet","Forecast","Stockout Risk","Segments","Anomaly Review","Basket Insights","Promotions","Model Catalog"];
const artifactFor:Record<string,string>={Segments:"segments","Anomaly Review":"anomalies","Basket Insights":"basket-rules",Promotions:"promotions"};

function App(){
 const [page,setPage]=useState("Home"),[summary,setSummary]=useState<Summary|null>(null),[series,setSeries]=useState<Point[]>([]),[profile,setProfile]=useState<Profile|null>(null),[models,setModels]=useState<Model[]>([]),[capabilities,setCapabilities]=useState<Capability[]>([]),[breakdown,setBreakdown]=useState<Breakdown[]>([]),[artifact,setArtifact]=useState<Artifact|null>(null),[error,setError]=useState("");
 useEffect(()=>{Promise.all([api<{items:Profile[],active:string}>("/api/v1/domain-packs"),api<Summary>("/api/v1/bi/summary"),api<{items:Point[]}>("/api/v1/bi/timeseries"),api<{items:Model[]}>("/api/v1/models"),api<{items:Capability[]}>("/api/v1/capabilities")]).then(([p,s,t,m,c])=>{setProfile(p.items.find(x=>x.profile_id===p.active)??p.items[0]);setSummary(s);setSeries(t.items);setModels(m.items);setCapabilities(c.items)}).catch(e=>setError(String(e)))},[]);
 useEffect(()=>{setArtifact(null);setBreakdown([]);const dim=page==="Brand / Product"?"brand":page==="Store / Outlet"?"store":"";if(dim)api<{items:Breakdown[]}>(`/api/v1/bi/breakdown/${dim}`).then(x=>setBreakdown(x.items)).catch(e=>setError(String(e)));const name=artifactFor[page];if(name)api<Artifact>(`/api/v1/analytics/${name}?limit=50`).then(setArtifact).catch(e=>setError(String(e)))},[page]);
 const trend={tooltip:{trigger:"axis"},legend:{data:["Revenue","Units"]},xAxis:{type:"category",data:series.map(x=>x.date)},yAxis:[{type:"value",name:"Revenue"},{type:"value",name:"Units"}],series:[{name:"Revenue",type:"line",smooth:true,data:series.map(x=>x.revenue)},{name:"Units",type:"bar",yAxisIndex:1,data:series.map(x=>x.units)}]};
 const bars={tooltip:{trigger:"axis"},xAxis:{type:"category",data:breakdown.map(x=>x.key),axisLabel:{rotate:35}},yAxis:{type:"value",name:"Revenue"},series:[{name:"Revenue",type:"bar",data:breakdown.map(x=>x.revenue)}]};
 return <div className="shell"><aside><h1>Sales Intelligence</h1><p>{profile?.display_name??"Loading profile"}</p>{pages.map(x=><button className={page===x?"active":""} onClick={()=>setPage(x)} key={x}>{x}</button>)}<a href="http://localhost:5000" target="_blank" rel="noreferrer">MLflow UI</a></aside><main><header><div><small>ACTIVE PROFILE</small><h2>{page}</h2></div><span className="pill">Local V1</span></header>{error&&<section className="error">{error}</section>}{!error&&!summary&&<section>Loading validated backend data…</section>}{summary&&<Page page={page} summary={summary} trend={trend} bars={bars} profile={profile} models={models} capabilities={capabilities} artifact={artifact}/>}<footer>{profile?.disclaimer}</footer></main></div>;
}
function Page({page,summary,trend,bars,profile,models,capabilities,artifact}:{page:string,summary:Summary,trend:object,bars:object,profile:Profile|null,models:Model[],capabilities:Capability[],artifact:Artifact|null}){
 if(page==="Home")return <><section className="cards"><Card label="Profile" value={profile?.display_name??"—"}/><Card label="Capabilities" value={`${capabilities.filter(x=>x.status==="AVAILABLE").length} available`}/><Card label="Data through" value={summary.date_to}/></section><section className="panel"><h3>Capability status</h3><DataTable rows={capabilities}/><p>{summary.freshness_note}</p></section></>;
 if(page==="Sales Overview")return <><Kpis s={summary}/><section className="panel"><h3>Sales over time</h3><ReactECharts option={trend} style={{height:420}}/><p>{summary.freshness_note} Range: {summary.date_from}—{summary.date_to}.</p></section></>;
 if(page==="Brand / Product"||page==="Store / Outlet")return <><Kpis s={summary}/><section className="panel"><h3>Revenue contribution</h3><ReactECharts option={bars} style={{height:420}}/><p>Descriptive historical contribution; revenue is not profit.</p></section></>;
 if(page==="Forecast"||page==="Stockout Risk"){const task=page==="Forecast"?"forecasting":"stockout_classification";const model=models.find(x=>x.task===task);return <section className="panel"><h3>Frozen serving model</h3><DataTable rows={model?[model]:[]}/><p>{page==="Forecast"?"The target is aggregate observed units in (t,t+7d]; this is model metadata, not a fabricated future chart.":"The score estimates occurrence within (t,t+7d]; it is not claimed to be a fully calibrated probability."}</p></section>}
 if(page==="Model Catalog")return <section className="panel"><h3>Model catalog</h3><DataTable rows={models}/><p>DVC owns reproducibility and canonical artifacts. MLflow owns run and registry metadata.</p></section>;
 return <section className="panel"><h3>{page}</h3>{artifact?<><p>{artifact.caveat}. Rows: {artifact.total}.</p><DataTable rows={artifact.items}/></>:<p>Loading versioned analytical artifact…</p>}<Caveat page={page}/></section>;
}
function Kpis({s}:{s:Summary}){return <section className="cards"><Card label="Revenue" value={s.revenue.toLocaleString()}/><Card label="Units sold" value={s.units.toLocaleString()}/><Card label="Avg selling price" value={s.average_selling_price.toFixed(2)}/><Card label="Stores / SKUs" value={`${s.active_stores} / ${s.active_skus}`}/></section>}
function Card({label,value}:{label:string,value:string}){return <article><small>{label}</small><strong>{value}</strong></article>}
function DataTable({rows}:{rows:object[]}){if(!rows.length)return <p>No supported rows available.</p>;const columns=Object.keys(rows[0]).slice(0,8);return <div className="table-wrap"><table><thead><tr>{columns.map(c=><th key={c}>{c}</th>)}</tr></thead><tbody>{rows.slice(0,50).map((r,i)=>{const values=r as Record<string,unknown>;return <tr key={i}>{columns.map(c=><td key={c}>{String(values[c]??"—")}</td>)}</tr>})}</tbody></table></div>}
function Caveat({page}:{page:string}){const notes:Record<string,string>={Segments:"Exploratory profiles; temporal retention is limited and assignment remains blocked.","Anomaly Review":"Candidates are unreviewed, not confirmed anomalies.","Basket Insights":"Association is neither causation nor recommendation.",Promotions:"PRE/DURING/POST comparisons are descriptive, not causal ROI."};return <p className="caveat">{notes[page]}</p>}
createRoot(document.getElementById("root")!).render(<React.StrictMode><App/></React.StrictMode>);
