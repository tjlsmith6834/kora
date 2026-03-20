import React from "react";
import ReactDOM from "react-dom/client";

import {JobModalProvider} from "./context/JobModalContext";
import {InterviewModalProvider} from "./context/InterviewModalContext";
import {AuthProvider} from "./context/AuthContext";
import App from "./App";

import "./index.css";

const rootElement = document.getElementById("root");

// Ensure the element exists before creating the root
if (rootElement) {
    const root = ReactDOM.createRoot(rootElement);

    root.render(
        <React.StrictMode>
            <AuthProvider>
                <JobModalProvider>
                <InterviewModalProvider>
                    <App />
                </InterviewModalProvider>
                </JobModalProvider>
            </AuthProvider>
        </React.StrictMode>
    );

} else {
    console.error("Root element not found");
}