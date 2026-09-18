export type Filters = {
  date_from: string; date_to: string; regions: string[]; channels: string[];
  stores: string[]; categories: string[]; brands: string[]; skus: string[]; promotion: string;
};
export const emptyFilters: Filters = {date_from:"",date_to:"",regions:[],channels:[],stores:[],categories:[],brands:[],skus:[],promotion:""};
export type FilterAction = {type:"set", key:keyof Filters, value:string|string[]} | {type:"clear"};
export function filterReducer(_:Filters, action:FilterAction):Filters {
  if(action.type==="clear") return {...emptyFilters};
  return {..._, [action.key]:action.value};
}
export function filtersFromSearch(search:string):Filters {
  const p=new URLSearchParams(search), out={...emptyFilters};
  (Object.keys(out) as (keyof Filters)[]).forEach(k=>{
    const values=p.getAll(k); if(Array.isArray(out[k])) (out as any)[k]=values; else (out as any)[k]=values[0]??"";
  }); return out;
}
export function filtersToSearch(filters:Filters):string {
  const p=new URLSearchParams();
  (Object.keys(filters) as (keyof Filters)[]).forEach(k=>{const value=filters[k]; Array.isArray(value)?value.forEach(x=>x&&p.append(k,x)):value&&p.set(k,value)});
  const text=p.toString(); return text?`?${text}`:"";
}
export function appendFilters(path:string, filters:Filters):string {
  const search=filtersToSearch(filters); if(!search)return path; return `${path}${path.includes("?")?"&":"?"}${search.slice(1)}`;
}
