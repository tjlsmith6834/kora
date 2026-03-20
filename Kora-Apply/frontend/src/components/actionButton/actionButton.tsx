import React from "react";
import { useSelector, useDispatch } from "react-redux";
import { RootState } from "../../redux/store";
import { setThinking } from "../../redux/slices/thinkingSlice";

export interface ActionButtonProps {
    onClick: () => void;
    disabled?: boolean;
    text: string;
    variant?: "primary" | "secondary" | "tertiary";
}

const ActionButton: React.FC<ActionButtonProps> = ({ onClick, text, variant, disabled = false}) => {
    const dispatch = useDispatch();
    const isThinking = useSelector((state: RootState) => state.thinking.thinking);

    const handleClick = async () => {
        dispatch(setThinking(true));

        try {
            await onClick();
        } finally {
            dispatch(setThinking(false));
        }
    };

    return (
        <>
            <style>
                {`
                    .action-button {
                      max-width: 1140px;
                      font-family: inherit;
                      font-size: var(--font-size-h3);
                      line-height: inherit;
                      flex: 1;
                      flex-basis: auto;
                      border: none;
                      border-radius: var(--radius-sm);
                      margin: 0 auto;
                      padding: 12px 20px;
                      /*box-shadow: 0 4px 6px rgba(0,0,0,0.1);*/
                      cursor: pointer;
                      transition: background-color 0.2s ease-in-out;
                      color: white;
                    }
                    
                    /* PRIMARY: positive (purple) */
                    .action-button.primary {
                      background-color: var(--color-postive-base);
                      color: var(--color-postive-text);
                    }
                    .action-button.primary:hover:not(:disabled) {
                      background-color: var(--color-positive-hover);
                    }
                    
                    /* SECONDARY: negative (white) */
                    .action-button.secondary {
                      background-color: var(--color-negative-base);
                      color: var(--color-negative-text);
                      border: 1px solid var(--color-negative-hover);
                    }
                    .action-button.secondary:hover:not(:disabled) {
                      background-color: var(--color-negative-hover);
                    }
                    
                    /* TERTIARY: indigo */
                    .action-button.tertiary {
                      background-color: var(--color-tertiary-base);
                      color: var(--color-tertiary-text);
                    }
                    .action-button.tertiary:hover:not(:disabled) {
                      background-color: var(--color-tertiary-hover);
                    }
                    
                    /* DISABLED */
                    .action-button:disabled {
                      background-color: var(--color-disabled);
                      color: var(--color-dsiabled-text);
                      cursor: not-allowed;
                    }
                `}
            </style>
            <button
                className={`action-button ${variant ? variant : ""}`}
                onClick={handleClick}
                disabled={disabled || isThinking}
            >
                {text}
            </button>
        </>
    );
};

export default ActionButton;