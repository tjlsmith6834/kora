import { useDispatch, useSelector } from "react-redux";
import { RootState } from "../redux/store";
import useApplicationApi from "./useApplicationApi";
import { setCurrentIndex } from "../redux/slices/questionSlice";
import { setStep, STEPS } from "../redux/slices/stepSlice";

const useSurveyHandler = () => {
    const dispatch = useDispatch();
    const questions = useSelector((state: RootState) => state.questions.questions);
    const currentIndex = useSelector((state: RootState) => state.questions.currentIndex);

    const { handleSaveAnswer, handleCompleteApplication } = useApplicationApi();

    const handleSubmitAnswer = async (answer: string) => {
        const question = questions[currentIndex];
        console.log(`Saving response for question: "${question}"`);
        try{
            await handleSaveAnswer(question, answer);
        } catch (error) {
            console.error("Failed to save answer:", error);
        }
        if (currentIndex + 1 < questions.length) {
            dispatch(setCurrentIndex(currentIndex + 1));

        } else {
            console.log("All questions answered or skipped.");
            setStep(STEPS.COMPLETE);
        }
    };

    const handleSkipQuestion = async () => {
        const question = questions[currentIndex];
        console.log(`Skipping question: "${question}"`);

        if (currentIndex + 1 < questions.length) {
            dispatch(setCurrentIndex(currentIndex + 1));
        } else {
            console.log("All questions answered or skipped.");
            dispatch(setStep(STEPS.COMPLETE));
        }
    };

    const handleFinishSurvey = async (answer?: string) => {
        if (answer && answer.trim()) {
            const question = questions[currentIndex];
            console.log(`Saving response for question: "${question}"`);
            try{
                await handleSaveAnswer(question, answer);
            } catch (error) {
                console.error("Failed to save answer:", error);
            }
        }
        await handleCompleteApplication();
    }

    //Return object
    return {
        handleSubmitAnswer,
        handleSkipQuestion,
        handleFinishSurvey
    };
}

export default useSurveyHandler;