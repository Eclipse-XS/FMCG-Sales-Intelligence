import {afterEach, describe, expect, it, vi} from "vitest";
import {api} from "./api";

describe("API client",()=>{
  afterEach(()=>vi.unstubAllGlobals());
  it("returns parsed data",async()=>{vi.stubGlobal("fetch",vi.fn().mockResolvedValue({ok:true,json:async()=>({status:"ok"})}));expect(await api<{status:string}>("/health")).toEqual({status:"ok"})});
  it("surfaces backend failures",async()=>{vi.stubGlobal("fetch",vi.fn().mockResolvedValue({ok:false,status:503,text:async()=>"not ready"}));await expect(api("/ready")).rejects.toThrow("503")});
});
