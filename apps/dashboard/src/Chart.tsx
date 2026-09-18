import {useEffect,useRef} from "react";
import * as echarts from "echarts/core";
import {BarChart,LineChart} from "echarts/charts";
import {GridComponent,LegendComponent,TooltipComponent} from "echarts/components";
import {CanvasRenderer} from "echarts/renderers";
import type {EChartsCoreOption} from "echarts/core";
echarts.use([BarChart,LineChart,GridComponent,LegendComponent,TooltipComponent,CanvasRenderer]);
export default function Chart({option}:{option:EChartsCoreOption}){const ref=useRef<HTMLDivElement>(null);useEffect(()=>{if(!ref.current)return;const chart=echarts.init(ref.current);chart.setOption(option);const resize=()=>chart.resize();window.addEventListener("resize",resize);return()=>{window.removeEventListener("resize",resize);chart.dispose()}},[option]);return <div ref={ref} style={{height:420}}/>}
