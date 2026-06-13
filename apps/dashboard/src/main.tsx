import React, {lazy, Suspense} from "react";
import {createRoot} from "react-dom/client";
import "./styles.css";
const DashboardApp=lazy(()=>import("./DashboardApp"));
createRoot(document.getElementById("root")!).render(<React.StrictMode><Suspense fallback={<main>Loading dashboard…</main>}><DashboardApp/></Suspense></React.StrictMode>);
