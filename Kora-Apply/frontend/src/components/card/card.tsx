import React, { ReactNode } from "react";

interface CardProps {
  children: ReactNode;
}

const Card: React.FC<CardProps> = ({ children }) => {
  return (
    <>
      <style>
        {`
          .card {
            width: 100%;
            background-color: #FFFFFF;
            border: var(--card-border);
            box-shadow: var(--card-shadow);
            border-radius: var(--radius-lg);
            padding: var(--spacing-md);
            margin: 0;
          }
        `}
      </style>
      <div className="card">
        {children}
      </div>
    </>
  );
};

export default Card;