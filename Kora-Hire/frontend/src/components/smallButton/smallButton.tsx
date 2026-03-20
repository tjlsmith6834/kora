import React from "react";
import "./smallButton.css";

export interface SmallButtonProps {
    onClick: () => void;
    disabled?: boolean;
    variant?: "secondary" | "tertiary";
    symbol?: boolean;
    noBorder?: boolean;
    className?: string;
    children: React.ReactNode;
}

const SmallButton: React.FC<SmallButtonProps> = ({ children, onClick, variant, symbol = false, noBorder = true, disabled = false, className}) => {

    const handleClick = async () => {

        try {
            await onClick();
        } finally {

        }
    };

    return (
        <button
            className={`small-button ${variant ?? ""} ${symbol ? "symbol" : ""} ${noBorder ? "no-border" : ""} ${className ?? ""}`}
            onClick={handleClick}
            disabled={disabled}
        >
            {children}
        </button>
    );
};

export default SmallButton;