// HorizontalDisplay.tsx
import React, {CSSProperties} from "react";
import "./horizontalDisplay.css";

interface HorizontalDisplayProps {
  children: React.ReactNode;
  gap?: string;         // optional override, e.g. "1rem" or "16px"
  justify?: string;     // e.g. "center", "space-between"
  align?: string;       // e.g. "flex-start", "center"
  style?: CSSProperties;
}

const HorizontalDisplay: React.FC<HorizontalDisplayProps> = ({
	children,
	gap,
	justify,
	align,
	style = {},
}) => {
	const inlineStyles: CSSProperties = {
		...(gap && { gap }),
		...(justify && { justifyContent: justify }),
		...(align && { alignItems: align }),
		...style,
	};

	return (
		<div className="horizontal-display" style={inlineStyles}>
			{children}
		</div>
	);
};

export default HorizontalDisplay;