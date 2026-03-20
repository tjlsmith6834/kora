import React from "react";
import ReactDOM from "react-dom/client";
import { Provider } from "react-redux";
import store from "./redux/store";
import App from "./App";
import { JobProvider } from "./context/jobContext";
import { SHADOW_CSS_STRING } from "./shadowStyles";

interface KoraApplyOptions {
  jobID: string;
  publicKey: string;
}

const KoraApplyWidget = {
  init: (
    selector = "kora-apply-container",
    options: Partial<KoraApplyOptions> = {}
  ) => {
    console.log("KoraApplyWidget.init() called with selector:", selector);

    if (!options.jobID) {
      console.error("`jobID` is required.");
      return;
    }

    if (!options.publicKey) {
      console.error("`publicKey` is required.");
      return;
    }

    // Get or create host element
    let host = document.getElementById(selector);
    if (!host) {
      host = document.createElement("div");
      host.id = selector;
      document.body.appendChild(host);
    }

    // Prevent double init
    if (host.dataset.initialized) {
      console.warn("Widget already initialized.");
      return;
    }
    host.dataset.initialized = "true";

    console.log("Attaching Shadow Root...");
    const shadow = host.attachShadow({ mode: "open" });

    // ----------------------------------------
    // 1️⃣ Inject your CSS inside the shadow root
    // ----------------------------------------
    const styleTag = document.createElement("style");
    styleTag.textContent = SHADOW_CSS_STRING; // <— put your shadow-safe CSS here
    shadow.appendChild(styleTag);

    // ----------------------------------------
    // 2️⃣ Create Shadow DOM mount point
    // ----------------------------------------
    const reactContainer = document.createElement("div");
    reactContainer.className = "kora-root";
    shadow.appendChild(reactContainer);

    // ----------------------------------------
    // 3️⃣ Mount React INTO shadow DOM
    // ----------------------------------------
    console.log("Mounting React inside shadow DOM...");
    const root = ReactDOM.createRoot(reactContainer);

    root.render(
      <Provider store={store}>
        <JobProvider jobID={options.jobID} publicKey={options.publicKey}>
          <App />
        </JobProvider>
      </Provider>
    );

    console.log("KoraApplyWidget successfully initialized!");
  },
};

// ✅ Default export for UMD / module consumers
export default KoraApplyWidget;

// ✅ Explicit global for <script src="...kora-apply.js">
if (typeof window !== "undefined") {
  // TS typing comfort, but at runtime this is just assignment
  (window as any).KoraApplyWidget = KoraApplyWidget;
}