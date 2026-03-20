import React, { CSSProperties } from "react";
import "./verticalDisplay.css";

interface VerticalDisplayProps {
	children: React.ReactNode;
	gap?: string;
	justify?: string;
	align?: string;
	style?: CSSProperties;
}

const VerticalDisplay: React.FC<VerticalDisplayProps> = ({
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
		<div className="vertical-display" style={inlineStyles}>
			{children}
		</div>
	);
};

export default VerticalDisplay;