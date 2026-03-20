// HorizontalDisplay.tsx
import React from "react";
import "./horizontalDisplay.css";

interface HorizontalDisplayProps {
  children: React.ReactNode;
  gap?: string;         // optional override, e.g. "1rem" or "16px"
  justify?: string;     // e.g. "center", "space-between"
  align?: string;       // e.g. "flex-start", "center"
}

const HorizontalDisplay: React.FC<HorizontalDisplayProps> = ({
  children,
  gap,
  justify = "flex-start",
  align = "center",
}) => (
    <>
      <style>
        {`
          .horizontal-display {
            width: 100%;
            max-width: 100%;
            display: flex;
            flex-direction: row;
            flex-wrap: wrap;
            align-items: flex-start;
            gap: 0 var(--spacing-sm);
          }
          
          .horizontal-display > * {
            flex: 1 1 200px;
          }
        `}
      </style>
      <div
        className="horizontal-display"
        style={{ gap, justifyContent: justify, alignItems: align }}
      >
        {children}
      </div>
    </>
);

export default HorizontalDisplay;