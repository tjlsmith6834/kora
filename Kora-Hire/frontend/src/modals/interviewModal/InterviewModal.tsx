import React, {useState} from "react";

import { useInterviewModal } from "../../context/InterviewModalContext";

import BlurredModal from "../../components/blurredModal/blurredModal";
import ContentSection from "../../components/contentSection/contentSection";
import Card from "../../components/card/card";

import InterviewQuestionEditor from "./components/interviewQuestionEditor";

import {QAResponse} from "../../types/applicantProfile";

interface InterviewModalProps {
    isOpen: boolean;
	modalStage: string;
    onInterviewQASaved: (qa: QAResponse) => void;
}

const InterviewModal: React.FC<InterviewModalProps> = ({
    isOpen,
    onInterviewQASaved,
	modalStage = "INTERVIEWER_QUESTION"
}) => {

    const { state, dispatch } = useInterviewModal();
    const {
        applicationId
    } = state;

    const closeModal = async () => {
        dispatch({ type: "CLOSE_MODAL"})
    }

    const askInterviewerQuestion = async () => {
	    dispatch({type: "OPEN_MODAL_STAGE", payload: "INTERVIEWER_QUESTION"});
    }

    return (
        <BlurredModal
            isOpen={isOpen}
            onRequestClose={closeModal}
            title={""}
        >
            <ContentSection id={"INTERVIEWER_QUESTION"} activeTab={modalStage}>
                <Card isClickable={false}>
                    {applicationId ? (
                        <InterviewQuestionEditor
                          applicationId={applicationId}
                          suggestQuestion={false}
                          onSave={async (qa) => {
                            await onInterviewQASaved(qa);
                            dispatch({ type: "CLOSE_MODAL" });
                          }}
                        />
                    ) : (
                        <p>Missing application id.</p> // or <Loader />
                    )}
                </Card>
            </ContentSection>
        </BlurredModal>
    );
}

export default InterviewModal