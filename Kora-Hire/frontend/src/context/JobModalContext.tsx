import React, {
    createContext,
    useContext,
    useReducer,
    ReactNode,
    Dispatch,
} from "react";

import type { Rubric } from "../types/job";

type JobModalContext = {
    title: string | null;
    jobId: string | null;
    jobTitle: string | null;
    editorRubric?: Rubric;
    formQuestions?: string[];
    file?: File | null;
    fileName?: string | null;
    modalStage: string;
    isModalOpen: boolean;
};

type JobModalAction =
    | { type: "SET_TITLE";          payload: string }
    | { type: "SET_JOB_ID";         payload: string }
    | { type: "SET_JOB_TITLE";      payload: string }
    | { type: "SET_EDITOR_RUBRIC";  payload: Rubric }
    | { type: "SET_FORM_QUESTIONS"; payload: string[] }
    | { type: "SET_MODAL_STAGE";    payload: string }
    | { type: "SET_FILE";           payload: File | null }
    | { type: "SET_FILE_NAME";      payload: string | null }
    | { type: "OPEN_MODAL";         payload: string }
    | { type: "CLOSE_MODAL" };

const initialState: JobModalContext = {
    title:        null,
    jobId:        null,
    jobTitle:     null,
    editorRubric: undefined,
    file:         null,
    fileName:     null,
    modalStage:   "EDIT_JD",
    isModalOpen:  false,
};

function reducer(
    state: JobModalContext,
    action: JobModalAction
): JobModalContext {
    switch (action.type) {
        case "SET_TITLE":
            return { ...state, title: action.payload}
        case "SET_JOB_ID":
            return { ...state, jobId: action.payload };
        case "SET_JOB_TITLE":
            return { ...state, jobTitle: action.payload };
        case "SET_EDITOR_RUBRIC":
            return { ...state, editorRubric: action.payload };
        case "SET_FORM_QUESTIONS":
            return { ...state, formQuestions: action.payload };
        case "SET_MODAL_STAGE":
            return { ...state, modalStage: action.payload}
        case "SET_FILE":
            return { ...state, file: action.payload };
        case "SET_FILE_NAME":
            return { ...state, fileName: action.payload };
        case "OPEN_MODAL":
            return { ...state, isModalOpen: true, modalStage: action.payload };
        case "CLOSE_MODAL":
            return { ...state, isModalOpen: false };
        default:
            return state;
    }
}

const JobModalContext = createContext<{
    state: JobModalContext;
    dispatch: Dispatch<JobModalAction>;
}>({
    state: initialState,
    dispatch: () => undefined,
});

export function JobModalProvider({ children }: { children: ReactNode }) {
    const [state, dispatch] = useReducer(reducer, initialState);
    return (
        <JobModalContext.Provider value={{ state, dispatch }}>
            {children}
        </JobModalContext.Provider>
    );
}

export function useJobModal() {
    const ctx = useContext(JobModalContext);
    if (!ctx) {
        throw new Error("useJobModal must be used within a JobModalProvider");
    }
    return ctx;
}