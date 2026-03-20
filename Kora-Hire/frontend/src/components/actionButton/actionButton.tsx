import React from "react";
import "./actionButton.css";

export interface ActionButtonProps {
    onClick: () => void;
    disabled?: boolean;
    text: string;
    variant?: "primary" | "secondary" | "tertiary";
}

const ActionButton: React.FC<ActionButtonProps> = ({ onClick, text, variant, disabled = false}) => {

    const handleClick = async () => {

        try {
            await onClick();
        } finally {

        }
    };

    return (
        <button
            className={`action-button ${variant ? variant : ""}`}
            onClick={handleClick}
            disabled={disabled}
        >
            {text}
        </button>
    );
};

export default ActionButton;