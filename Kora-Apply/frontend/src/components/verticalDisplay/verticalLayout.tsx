// VerticalDisplay.tsx
import React from "react";
import "./verticalDisplay.css";

interface VerticalDisplayProps {
  children: React.ReactNode;
  gap?: string;         // optional override, e.g. "1rem" or "16px"
  justify?: string;     // e.g. "center", "space-between"
  align?: string;       // e.g. "flex-start", "center"
}

const VerticalDisplay: React.FC<VerticalDisplayProps> = ({
  children,
  gap = "0rem",
  justify = "flex-start",
  align = "center",
}) => (
  <>
    <style>
      {`
        .vertical-display{
          display: flex;
          flex-direction: column;
          gap: 0;
        }
      `}
    </style>
    <div
      className="vertical-display"
      style={{ gap, justifyContent: justify, alignItems: align }}
    >
      {children}
    </div>
  </>
);

export default VerticalDisplay;