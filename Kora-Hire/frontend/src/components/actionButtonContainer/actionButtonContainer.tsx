import React from "react";
import ActionButton, {ActionButtonProps} from "../actionButton/actionButton";
import "./actionButtonContainer.css";

interface ActionButtonContainerProps {
    centerButton?: ActionButtonProps;
    yesButton?: ActionButtonProps;
    noButton?: ActionButtonProps;
}

const ActionButtonContainer: React.FC<ActionButtonContainerProps> = ({
    centerButton,
    yesButton,
    noButton
}) => {
    return (
        <div className="action-button-container">
            {(yesButton || noButton) && (
                <div className="choice-button-container">
                    {yesButton && <ActionButton {...yesButton} variant="primary" />}
                    {noButton && <ActionButton {...noButton} variant="secondary" />}
                </div>
            )}
            {centerButton && (
                <div className="center-button">
                    <ActionButton {...centerButton} variant={yesButton ? "tertiary" : "primary"} />
                </div>
            )}
        </div>
    );
};

export default ActionButtonContainer;