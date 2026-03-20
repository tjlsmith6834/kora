import React from "react";
import Breadcrumb from "../breadcrumb/breadcrumb";
import Tabs from "../tabs/tabs";
import "./header.css";

// Define Props Type
interface BreadcrumbItem {
  label: string;
  path: string;
  isActive?: boolean;
}

interface TabItem {
  id: string;
  label: string;
}

interface HeaderProps {
  title: string;
  crumbs?: BreadcrumbItem[];
  tabs?: TabItem[];
  activeTab?: string;
  onTabChange?: (tabId: string) => void;
}

// Convert Header to TypeScript with Props
const Header: React.FC<HeaderProps> = ({ title, crumbs, tabs, onTabChange, activeTab }) => {
  return (
    <header className="header">
      <div className="header-content-wrapper">
        {crumbs && <Breadcrumb crumbs={crumbs} />}
        <h1>{title}</h1>
        {tabs && (
          <Tabs
            tabs={tabs}
            activeTab={activeTab || ""}
            onTabChange={onTabChange || (() => {})} // Ensure function default
          />
        )}
      </div>
    </header>
  );
};

export default Header;