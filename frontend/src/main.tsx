import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.tsx";
import TestApp from "./TestApp.tsx";
import SimpleApp from "./SimpleApp.tsx";
import "./index.css";

// Use full App (Monaco editor, language switching, results panel)
const USE_SIMPLE_APP = false;

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>{USE_SIMPLE_APP ? <SimpleApp /> : <App />}</React.StrictMode>
);
