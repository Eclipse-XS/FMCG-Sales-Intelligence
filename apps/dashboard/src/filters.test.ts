import {describe,expect,it} from "vitest";
import {appendFilters,emptyFilters,filterReducer,filtersFromSearch,filtersToSearch} from "./filters";
describe("global analytical filters",()=>{
 it("restores a region from URL",()=>expect(filtersFromSearch("?regions=4").regions).toEqual(["4"]));
 it("persists filters in URL",()=>expect(filtersToSearch({...emptyFilters,regions:["4"]})).toBe("?regions=4"));
 it("includes supported region in requests",()=>expect(appendFilters("/api/v1/bi/summary",{...emptyFilters,regions:["4"]})).toContain("regions=4"));
 it("clear resets every field",()=>expect(filterReducer({...emptyFilters,brands:["Burn"]},{type:"clear"})).toEqual(emptyFilters));
 it("preserves filters across navigation because page is outside reducer state",()=>{const f=filterReducer(emptyFilters,{type:"set",key:"regions",value:["2"]});expect(f.regions).toEqual(["2"])});
});
