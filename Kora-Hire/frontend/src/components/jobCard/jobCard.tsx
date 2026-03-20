import React from "react";
import Card from "../card/card";
import "./jobCard.css";

// Define Props Type
interface JobCardProps {
  id: string;
  title: string;
  isClickable?: boolean;
  onClick?: (id: string) => void;
}

// Convert JobCard to TypeScript
const JobCard: React.FC<JobCardProps> = ({ id, title, isClickable = true, onClick }) => {
  return (
    <Card
      isClickable={isClickable}
      onClick={isClickable && onClick ? () => onClick(id) : undefined}
    >
      <div className="summary-wrapper">
        <h3>{title}</h3>
      </div>
    </Card>
  );
};

export default JobCard;