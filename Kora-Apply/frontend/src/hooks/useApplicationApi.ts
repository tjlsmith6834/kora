import { useCallback, useState } from "react";
import axios from "axios";
import { useDispatch, useSelector } from "react-redux";
import { RootState } from "../redux/store";
import { setStep, STEPS} from "../redux/slices/stepSlice";
import {setApplicationId, setFirstName, setLastName, setEmail} from "../redux/slices/applicationSlice";
import { setQuestions } from "../redux/slices/questionSlice";
import { useJobContext } from "../context/jobContext";

const api = axios.create({
    baseURL: process.env.REACT_APP_API_BASE_URL || "http://localhost:8000",
    withCredentials: true,
    headers: {
        "Content-Type": "application/json",
    },
})

export const useApplicationApi = () => {
    const dispatch = useDispatch();
    const { applicationId } = useSelector((state: RootState) => state.application);
    const { questions } = useSelector((state: RootState) => state.questions);
    const currentResponse = useSelector((state: RootState) => state.questions.currentResponse);

    const { jobID, publicKey } = useJobContext();

    const handleApplicationUpload = useCallback(async (
        firstName: string,
        lastName: string,
        email:  string,
        resume: File,
        linkedinUrl?: string,
        portfolioUrl?: string,
        githubUrl?: string,
    ) => {
        try {
            dispatch(setStep(STEPS.UPLOADING));
            const formData = new FormData();
            formData.append("job_id", jobID);
            formData.append("first_name", firstName);
            formData.append("last_name", lastName);
            formData.append("candidate_email", email);
            formData.append("resume", resume);

            if (linkedinUrl) formData.append("linkedin_url", linkedinUrl);
            if (portfolioUrl) formData.append("portfolio_url", portfolioUrl);
            if (githubUrl) formData.append("github_url", githubUrl);

            const response = await api.post(
                `/applications/`,
                formData,
                {headers:
                    {
                        "Content-Type": "multipart/form-data",
                        "X-Job-ID": jobID,
                        "X-Public-Key": publicKey,
                    },
                }
            );

            dispatch(setApplicationId(response.data.application_id));
            dispatch(setFirstName(firstName))
            dispatch(setLastName(lastName))
            dispatch(setEmail(email))
            dispatch(setStep(STEPS.UPLOAD_SUCCESS));
            return response.data.application_id
        } catch (error) {
            dispatch(setStep(STEPS.ERROR_PRE_UPLOAD))
        }
    }, [dispatch, jobID]);

    const handleGetSurvey = useCallback(async () => {
        if (!applicationId) {
            console.error("Application is missing");
            return;
        }
        try {
            dispatch(setStep(STEPS.GET_QUESTIONS));

            // Post request and get taskId
            const dispatchResponse = await api.post(
                `/surveys/?application_id=${applicationId}`,
                {},
                {headers:
                    {
                        "X-Job-ID": jobID,
                        "X-Public-Key": publicKey,
                    },
                }
            );

            const taskId = dispatchResponse.data.task_id;
            if (!taskId) {
                console.error("No task id returned");
                return;
            }
            console.log("Dispatched task id:", taskId);

            // Poll for the task result using the status endpoint.
            const pollTaskStatus = async (id : string, maxRetries = 100, delay = 3000) => {
                for (let i = 0; i < maxRetries; i++) {
                    const statusResponse = await api.get(
                        `/tasks/?task_id=${id}`,
                        {headers:
                            {
                                "X-Job-ID": jobID,
                                "X-Public-Key": publicKey,
                            },
                        }
                    );
                    const { state, result } = statusResponse.data;
                    console.log("Task state:", state);
                    if (state === "SUCCESS" && result) {
                        return result;
                    } else if (state === "FAILURE") {
                        throw new Error("Survey generation task failed");
                    }
                    // Wait before retrying
                    await new Promise((resolve) => setTimeout(resolve, delay));
                }
                throw new Error("Task did not complete in time");
            };

            const surveyData = await pollTaskStatus(taskId);

            if (surveyData && Array.isArray(surveyData.questions) && surveyData.questions.length > 0) {
                dispatch(setQuestions(surveyData.questions));
                dispatch(setStep(STEPS.SURVEY));
            } else {
                console.error("No questions returned.");
            }
        } catch (error) {
            console.error("Error fetching survey:", error);
            dispatch(setStep(STEPS.ERROR_POST_UPLOAD));
        }
    }, [dispatch, applicationId]);

    const handleSaveFormQuestionAnswer = useCallback(async ( question: string, answer: string, application_id?: string) => {
        if (!application_id) {
            if (!applicationId) {
                console.error("Application is missing");
                return;
            }
            application_id=applicationId
        }
        if (!answer.trim()) {
            alert("Please complete all fields.");
            return;
        }

        try {
            // Construct the JSON payload
            const payload = { question, answer };

            // Send the request as JSON. httpx (and axios) will automatically
            // set the "Content-Type" header to "application/json"
            const response = await api.post(
                `/applications/${application_id}/form_question_answers/`,
                payload,
                { headers:
                    {
                        "Content-Type": "application/json",
                        "X-Job-ID": jobID,
                        "X-Public-Key": publicKey,
                    }
                }
            );

            console.log("Response:", response.data);
            // Handle response here (e.g., update state or notify the user)
        } catch (error) {
            console.error("Failed to save answer:", error);
            dispatch(setStep(STEPS.ERROR_POST_UPLOAD));
        }
    }, [dispatch, applicationId]);

    const handleSaveAnswer = useCallback(async (question: string, answer: string) => {
        if (!applicationId) {
            console.error("Application is missing");
            return;
        }

        if (!answer.trim()) {
            alert("Please complete all fields.");
            return;
        }

        try {
            // Construct the JSON payload
            const payload = { question, answer };

            // Send the request as JSON. httpx (and axios) will automatically
            // set the "Content-Type" header to "application/json"
            const response = await api.post(
                `/applications/${applicationId}/question_answers/`,
                payload,
                { headers:
                    {
                        "Content-Type": "application/json",
                        "X-Job-ID": jobID,
                        "X-Public-Key": publicKey,
                    }
                }
            );

            console.log("Response:", response.data);
            // Handle response here (e.g., update state or notify the user)
        } catch (error) {
            console.error("Failed to save answer:", error);
            dispatch(setStep(STEPS.ERROR_POST_UPLOAD));
        }
    }, [dispatch, applicationId]);

    const handleCompleteApplication = useCallback(async () => {
        if (!applicationId) {
            console.error("Application is missing");
            return;
        }

        try {
            const response = await api.post(
                `/applications/${applicationId}/complete`,
                {},
                { headers:
                    {
                        "X-Job-ID": jobID,
                        "X-Public-Key": publicKey,
                    }
                }
            );

            console.log("Response:", response.data);
            dispatch(setStep(STEPS.COMPLETE))
        } catch (error) {
            console.error("Failed to set complete")
            dispatch(setStep(STEPS.COMPLETE))
        }
    }, [dispatch, applicationId]);

    //Return object
    return {
        handleApplicationUpload,
        handleGetSurvey,
        handleSaveAnswer,
        handleCompleteApplication,
        handleSaveFormQuestionAnswer
    };
};

export default useApplicationApi;