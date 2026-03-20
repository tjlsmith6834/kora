import React, { useEffect } from "react";
import { useSelector } from "react-redux";
import { RootState } from "./redux/store";

import ResumeCard from "./cards/resumeCard";
import UploadingCard from "./cards/uploadingCard";
import SurveyRequestCard from "./cards/sureyRequestCard";
import BuildingSurveyCard from "./cards/buildingSurveyCard";
import QuestionCard from "./cards/questionCard";
import ErrorPreUploadCard from "./cards/errorPreUploadCard";
import ErrorPostUploadCard from "./cards/errorPostUploadCard";
import CompleteCard from "./cards/completeCard";

const App: React.FC = () => {
    const step = useSelector((state: RootState) => state.step.step);
    const questions = useSelector((state: RootState) => state.questions.questions);

    useEffect(() => {
        console.log("Step changed to:", step);
    }, [step]);

    return (
        <div className="app-container">
            <div className="content-container">
                {step === "APPLY" && (
                    <ResumeCard/>
                )}
                {step === "UPLOADING" && (
                    <UploadingCard/>
                )}
                {step === "UPLOAD_SUCCESS" && (
                    <SurveyRequestCard/>
                )}
                {step === "ERROR_PRE_UPLOAD" && (
                    <ErrorPreUploadCard/>
                )}
                {step === "GET_QUESTIONS" && (
                    <BuildingSurveyCard/>
                )}
                {step === "SURVEY" && questions.length > 0 && (
                    <QuestionCard/>
                )}
                {step === "ERROR_POST_UPLOAD" && (
                    <ErrorPostUploadCard/>
                )}
                {step === "COMPLETE" && (
                    <CompleteCard/>
                )}
            </div>
        </div>
    );
};

export default App;