import React, { ReactNode } from "react";
import "./contentSection.css";

interface ContentSectionProps {
  id: string;
  activeTab: string;
  children: ReactNode;
}

const ContentSection: React.FC<ContentSectionProps> = ({ id, activeTab, children }) => {
  return (
    <section
      id={id}
      className={`content-section ${activeTab === id ? "active" : "hidden"}`}
    >
      {activeTab === id && children}
    </section>
  );
};

export default ContentSection;