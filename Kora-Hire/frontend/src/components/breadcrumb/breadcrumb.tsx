import React from "react";
import { Link } from "react-router-dom";
import "./breadcrumb.css";

// Define Props Type
interface BreadcrumbItem {
  label: string;
  path: string;
  isActive?: boolean; // Optional, defaults to false if not provided
}

interface BreadcrumbProps {
  crumbs: BreadcrumbItem[];
}

// Convert Breadcrumb to TypeScript with Props
const Breadcrumb: React.FC<BreadcrumbProps> = ({ crumbs }) => {
  return (
    <nav className="breadcrumb-container">
      <ul className="breadcrumb-list">
        {crumbs.map((crumb, index) => (
          <li key={index} className="breadcrumb-item">
            {crumb.isActive ? (
              <span className="breadcrumb-active">{crumb.label}</span>
            ) : (
              <Link to={crumb.path} className="breadcrumb-link">
                {crumb.label}
              </Link>
            )}
            {index < crumbs.length - 1 && <span className="breadcrumb-separator">/</span>}
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default Breadcrumb;