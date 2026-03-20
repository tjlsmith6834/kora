// actionButtonContainer.tsx
import React from "react";
import ActionButton, {ActionButtonProps} from "../actionButton/actionButton";
import "./actionButtonContainer.css";
import VerticalDisplay from "../verticalDisplay/verticalLayout";
import HorizontalDisplay from "../horizontalDisplay/horizontalDisplay";

interface StepContainerProps {
    centerButton?: ActionButtonProps;
    yesButton?: ActionButtonProps;
    noButton?: ActionButtonProps;
}

const ActionButtonContainer: React.FC<StepContainerProps> = ({ centerButton, yesButton, noButton }) => {
    return (
        <>
            <style>
                {`
                  .action-button-container {
                      width: 100%;
                      padding-top: var(--spacing-sm);
                    }
                    
                    .center-button {
                      display: flex;
                      width: 100%;
                    }
                    
                    .center-button > .action-button {
                      margin: 0;         /* no more auto margins */
                      max-width: none;   /* remove the 1140px cap if you want it edge-to-edge */
                      flex: 1;           /* grow to fill the wrapper’s 100% width */
                    }
                `}
            </style>
            <div className="action-button-container">
                <VerticalDisplay gap={"var(--spacing-sm)"}>
                {(yesButton || noButton) && (
                    <HorizontalDisplay>
                        {yesButton && <ActionButton {...yesButton} variant="primary" />}
                        {noButton && <ActionButton {...noButton} variant="secondary" />}
                    </HorizontalDisplay>
                )}
                {centerButton &&
                    <div className="center-button">
                        <ActionButton {...centerButton} variant={yesButton ? "tertiary" : "primary"} />
                    </div>
                }
                </VerticalDisplay>
            </div>
        </>
    );
};

export default ActionButtonContainer;