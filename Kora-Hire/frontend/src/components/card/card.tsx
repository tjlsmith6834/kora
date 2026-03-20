import React, { ReactNode } from "react";
import "./card.css";

interface CardProps {
  children: ReactNode;
  isClickable?: boolean;
  onClick?: () => void;
}

const Card: React.FC<CardProps> = ({ children, isClickable = false, onClick }) => {
  return (
    <div
      className={`card ${isClickable ? "clickable" : ""}`}
      onClick={isClickable ? onClick : undefined}
    >
      {children}
    </div>
  );
};

export default Card;