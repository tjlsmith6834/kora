import React, {useState} from "react";

import { useJobModal } from "../../context/JobModalContext";

import BlurredModal from "../../components/blurredModal/blurredModal";
import FileUploader from "../../components/fileUploader/fileUploader";
import ActionButtonContainer from "../../components/actionButtonContainer/actionButtonContainer";
import RubricTable from "../../components/rubricTable/rubricTable";
import ContentSection from "../../components/contentSection/contentSection";
import Card from "../../components/card/card";
import CardContent from "../../components/cardContent/cardContent";

import { postJobRubric, postJobDescription, postJobForOrganization } from "../../hooks/useJobsApi"
import { handlePostRequestSmartRubric } from "../../hooks/useSmartRubricApi";
import { handlePollTask } from "../../hooks/useTaskApi";

import { Rubric, JobFrame, Job } from "../../types/job";
import FormQuestionEditor from "./components/formQuestionEditor";

interface JobModalProps {
    isOpen: boolean;
    saveNewJob?: (new_job: Job) => void;
    saveDescriptionTitle?: (updated: string) => void;
    saveRubric?: (updated: Rubric) => void;
    saveFormQuestions?: (updated: string[]) => void;
}

const JobModal: React.FC<JobModalProps> = ({
    isOpen,
    saveNewJob,
    saveDescriptionTitle,
    saveRubric,
    saveFormQuestions
}) => {

    const { state, dispatch } = useJobModal();
    const {
        title,
        modalStage,
        file,
        fileName,
        editorRubric,
        jobId,
    } = state;
    const [titleInput, setTitleInput] = useState("");

    const closeModal = async () => {
        dispatch({ type: "CLOSE_MODAL"})
    }

    const setStage = async (stage: string) => {
        dispatch({ type: "SET_MODAL_STAGE", payload: stage})
    }

    const onFileChange = (f: File | null) =>
        dispatch({ type: "SET_FILE", payload: f });

    const onSaveNewJob = async(new_title: string) => {
        dispatch({ type: "SET_MODAL_STAGE", payload:"UPLOAD_NEW_JOB"});
        try{
            const new_job: JobFrame = {
                title: new_title
            }
            const saved_job = await postJobForOrganization(new_job)
            dispatch({type:"SET_JOB_ID", payload:saved_job.job_id})
            dispatch({type:"SET_JOB_TITLE", payload:saved_job.title})
            if (saveNewJob){
                saveNewJob(saved_job)
            }
            dispatch({type:"SET_MODAL_STAGE", payload:"UPLOAD_NEW_JOB_SUCCESS"})
        } catch(error){
            console.warn(error)
            throw error;
        }
    }

    const onUploadDescription = async () => {
        dispatch({ type: "OPEN_MODAL", payload: "UPLOAD_JD" });
        try{
            if (!jobId){
                throw new Error("No job ID to save description for")
            }
            if (!file){
                throw new Error("No file to save")
            }
            const { file_name } = await postJobDescription(jobId, file);
            dispatch({ type: "SET_FILE_NAME", payload: file_name });
            if (saveDescriptionTitle){
                saveDescriptionTitle(file_name)
            }
            dispatch({ type: "OPEN_MODAL", payload: "UPLOAD_JD_SUCCESS" });
        } catch(error){
            console.warn(error)
            throw error;
        }
    };

    const onEditRubric = async (rubric: Rubric) => {
        dispatch({ type: "SET_EDITOR_RUBRIC", payload: rubric})
    }

    const onSaveRubric = async () => {
        dispatch({ type: "OPEN_MODAL", payload: "UPLOAD_RUBRIC" });
        try{
            if (!jobId){
                throw new Error("No job ID to save rubric for")
            }
            if (!editorRubric){
                throw new Error("No rubric to save")
            }
            const saved = await postJobRubric(jobId, editorRubric);
            if (saveRubric){
                saveRubric(saved)
            }
            dispatch({ type: "SET_EDITOR_RUBRIC", payload: saved });
            dispatch({ type: "OPEN_MODAL", payload: "UPLOAD_RUBRIC_SUCCESS" });
        } catch (error) {
            console.warn(error)
            throw error;
        }
    };

    const onSaveFormQuestions = async (formQuestions: string[]) => {
        try{
            if (saveFormQuestions) {
                saveFormQuestions(formQuestions);
            }
            dispatch({type: "SET_FORM_QUESTIONS", payload: formQuestions})
        } catch (error) {
            console.warn(error)
            throw error;
        }
    }

    const handleRequestSmartRubric = async (): Promise<void> => {
        dispatch({ type: "SET_MODAL_STAGE", payload: "REQUEST_SMART_RUBRIC" })
        try {
            if (!jobId){
                throw new Error("No job ID to request rubric for")
            }

            const task = await handlePostRequestSmartRubric(jobId);
            const pollResult = await handlePollTask<Rubric>(task.task_id);

            if (!pollResult.result) {
              throw new Error("Task completed but did not return a rubric");
            }

            dispatch({ type: "SET_EDITOR_RUBRIC", payload: pollResult.result});
            dispatch({ type: "SET_MODAL_STAGE", payload: "EDIT_RUBRIC"})
        } catch (error) {
            console.error("Request for new smart rubric failed", error);
            throw error;
        }
    };


    return (
        <BlurredModal
            isOpen={isOpen}
            onRequestClose={closeModal}
            title={title}
        >
            <ContentSection id={"JOB_BASICS"} activeTab={modalStage}>
                <Card isClickable={false}>
                    <h3>Role Overview:</h3>
                    <div className="input-group">
                        <label htmlFor="title">Job Title:</label>
                        <input
                            type="text"
                            placeholder="Enter the title of the role"
                            value={titleInput}
                            onChange={e => setTitleInput(e.target.value)}
                        />
                    </div>
                    <ActionButtonContainer
                        yesButton={{
                            onClick: () => onSaveNewJob(titleInput),
                            text: "Save New Job",
                            variant: "primary",
                            disabled: false
                        }}

                        noButton={{
                            onClick: closeModal,
                            text: "Cancel",
                            variant: "secondary",
                            disabled: false
                        }}
                    />
                </Card>
            </ContentSection>

            <ContentSection id={"UPLOAD_NEW_JOB"} activeTab={modalStage}>
                <Card isClickable={false}>
                    <CardContent
                        title={"Uploading..."}
                        content={"Given us one moment while we store this away."}
                        loading={true}
                    />
                </Card>
            </ContentSection>

            <ContentSection id={"UPLOAD_NEW_JOB_SUCCESS"} activeTab={modalStage}>
                <Card isClickable={false}>
                    <CardContent
                        title={"You're on your way!"}
                        content={"Let's keep moving by uploading a job description for this role."}
                    />
                    <ActionButtonContainer
                        centerButton={{
                            onClick: () => setStage("EDIT_JD"),
                            text: "Ok",
                            variant: "primary"
                        }}
                    />
                </Card>
            </ContentSection>

            <ContentSection id={"EDIT_JD"} activeTab={modalStage}>
                <Card isClickable={false}>
                    <FileUploader
                        isEditable={true}
                        onFileChange={onFileChange}
                    />
                    <ActionButtonContainer
                        centerButton={{
                            onClick: onUploadDescription,
                            text: "Upload Description",
                            variant: "primary",
                            disabled: !(jobId && file)
                        }}
                    />
                </Card>
            </ContentSection>

            <ContentSection id={"UPLOAD_JD"} activeTab={modalStage}>
                <Card isClickable={false}>
                    <CardContent
                        title={"Uploading..."}
                        content={"Given us one moment while we store this away."}
                        loading={true}
                    />
                </Card>
            </ContentSection>

            <ContentSection id={"UPLOAD_JD_SUCCESS"} activeTab={modalStage}>
                <Card isClickable={false}>
                    <CardContent
                        title={"Success!"}
                        content={"Your new job description is saved." +
                            "\nAfter uploading a new job description we suggest updating your rubric so that candidate interviews and scores match your job description. Would you like to edit your rubric?"}
                    />
                    <ActionButtonContainer
                        yesButton={{
                            onClick: () => setStage("EDIT_RUBRIC"),
                            text: "Yes, edit rubric"
                        }}
                        noButton={{
                            onClick: closeModal,
                            text: "No thanks, go back to job applicants"
                        }}
                    />
                </Card>
            </ContentSection>

            <ContentSection id={"EDIT_FORM_QUESTIONS"} activeTab={modalStage}>
                <Card isClickable={false}>
                    { jobId?
                        (
                            <FormQuestionEditor
                                jobId={jobId}
                                saveFormQuestions={onSaveFormQuestions}
                                formQuestions={state.formQuestions}
                            />
                        ) : (
                            <p>No Role Found!</p>
                        )
                    }
                </Card>
            </ContentSection>

            <ContentSection id={"EDIT_RUBRIC"} activeTab={modalStage}>
                <Card isClickable={false}>
                    <RubricTable
                        rubric={editorRubric}
                        editable={true}
                        onChange={onEditRubric}
                    />
                    <ActionButtonContainer
                        yesButton={{
                            onClick: onSaveRubric,
                            text: "Save"
                        }}
                        noButton={{
                            onClick: closeModal,
                            text: "Cancel"
                        }}
                        centerButton={{
                            onClick: handleRequestSmartRubric,
                            text: "Build me a smart rubric"
                        }}
                    />
                </Card>
            </ContentSection>

            <ContentSection id={"UPLOAD_RUBRIC"} activeTab={modalStage}>
                <Card isClickable={false}>
                    <CardContent
                        title={"Uploading your new rubric..."}
                        content={"Given us one moment while we store this away."}
                        loading={true}
                    />
                </Card>
            </ContentSection>

            <ContentSection id={"UPLOAD_RUBRIC_SUCCESS"} activeTab={modalStage}>
                <Card isClickable={false}>
                    <CardContent
                        title={"Success!"}
                        content={"Your new job rubric has been saved!" +
                            "\nWould you like to keep editing?"}
                    />
                    <ActionButtonContainer
                        yesButton={{
                            onClick: () => setStage("EDIT_RUBRIC"),
                            text: "Yes, edit rubric"
                        }}
                        noButton={{
                            onClick: closeModal,
                            text: "No thanks, I'm done"
                        }}
                    />
                </Card>
            </ContentSection>

            <ContentSection id={"REQUEST_SMART_RUBRIC"} activeTab={modalStage}>
                <Card isClickable={false}>
                    <CardContent
                        title={"Generating new smart rubric..."}
                        content={"Analyzing your job, running our models, blah bla blah."}
                        loading={true}
                    />
                </Card>
            </ContentSection>
        </BlurredModal>
    );
}

export default JobModal