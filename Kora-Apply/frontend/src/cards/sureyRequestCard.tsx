import React, { useState } from "react";
import Card from "../components/card/card"
import ActionButtonContainer from "../components/actionButtonContainer/actionButtonContainer";
import {useSelector} from "react-redux";
import {RootState} from "../redux/store";
import useApplicationApi from "../hooks/useApplicationApi";

interface SurveyRequestCardProps {
}

const SurveyRequestCard: React.FC<SurveyRequestCardProps> = ({
}) => {

    const firstName = useSelector((state: RootState) => state.application.firstName)
	const { handleGetSurvey, handleCompleteApplication } = useApplicationApi();

    return (
	    <Card>
		    <h1>Application uploaded.</h1>
		    <h2>Thank you for your applying{firstName ? `, ${firstName}` : ''}!</h2>
		    <p>
				Before you go, we think we can help you stand out if you answer a few more questions for us.
				<br />
				Would you be willing to give us a few more moments of your time?
			</p>
            <ActionButtonContainer
                yesButton={{
                    onClick: handleGetSurvey,
                    variant: "primary",
                    text: "Yes, ask away!"
                }}
                noButton={{
                    onClick: handleCompleteApplication,
                    variant: "primary",
                    text: "No thanks!"
                }}
            />
	    </Card>
    );
};

export default SurveyRequestCard;