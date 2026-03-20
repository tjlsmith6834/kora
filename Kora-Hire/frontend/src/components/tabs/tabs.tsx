import React from "react";
import "./tabs.css"; // Separate CSS file for tab styles

// Define Type for a Single Tab
interface TabItem {
  id: string;
  label: string;
}

// Define Props Type for the Tabs Component
interface TabsProps {
  tabs: TabItem[];
  activeTab: string;
  onTabChange: (tabId: string) => void;
}

// Convert Tabs to TypeScript
const Tabs: React.FC<TabsProps> = ({ tabs, activeTab, onTabChange }) => {
  return (
    <nav className="tab-container">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          className={`tab ${activeTab === tab.id ? "selected" : ""}`}
          onClick={() => onTabChange(tab.id)}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  );
};

export default Tabs;