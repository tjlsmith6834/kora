import React, { FormEvent, useRef, useState } from "react";
import Card from "../components/card/card"
import FormField from "../components/formField/formField"
import ActionButtonContainer from "../components/actionButtonContainer/actionButtonContainer";
import Spinner from "../components/spinner/spinner";
import useSurveyHandler from "../hooks/useSurveyHandler";
import {useSelector} from "react-redux";
import {RootState} from "../redux/store";

interface QuestionCardProps {
}

const QuestionCard: React.FC<QuestionCardProps> = ({
}) => {
	const formRef = useRef<HTMLFormElement>(null);

	const questions = useSelector((state: RootState) => state.questions.questions);
	const currentIndex = useSelector((state: RootState) => state.questions.currentIndex);
	const [response, setResponse] = useState('');
	const [submitting, setSubmitting] = useState(false)

	const { handleSubmitAnswer, handleSkipQuestion, handleFinishSurvey } = useSurveyHandler();

    const submitAnswer = async () => {
		setSubmitting(true)
        await handleSubmitAnswer(response)
        setResponse('')
	    setSubmitting(false)
    }

    return (
	    <Card>
		    <form
			    ref={formRef}
			    onSubmit={(e) => {
				    e.preventDefault();
				    submitAnswer();
			    }}
		    >
			    <h2>Question:</h2>
			    <FormField
				    id="response"
				    label={questions[currentIndex] || "No question available"}
				    required
				    type="text"
				    isTextarea
				    value={response}
				    onChange={(e) => setResponse(e.target.value)}
			    />
			    {!submitting? (
				    <ActionButtonContainer
					    yesButton={{
						    onClick: () => formRef.current?.requestSubmit(),
						    text: "Submit",
						    variant: "primary",
						    disabled: !response?.trim()
					    }}
					    noButton={{
						    onClick: () => handleSkipQuestion(),
						    text: "Skip this question",
						    variant: "secondary",
						    disabled: false
					    }}
					    centerButton={{
						    onClick: () => handleFinishSurvey(response),
						    text: "Finish survey",
						    variant: "tertiary",
						    disabled: false
					    }}
				    />
			    ) : (
					<Spinner/>
		        )}
		    </form>
	    </Card>
    );
};

export default QuestionCard;