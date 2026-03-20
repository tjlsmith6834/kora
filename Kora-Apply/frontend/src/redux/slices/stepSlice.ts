import { createSlice, PayloadAction } from "@reduxjs/toolkit";

// Define Step States
export enum STEPS {
    APPLY = "APPLY",
    UPLOADING = "UPLOADING",
    UPLOAD_SUCCESS = "UPLOAD_SUCCESS",
    GET_QUESTIONS = "GET_QUESTIONS",
    SURVEY = "SURVEY",
    COMPLETE = "COMPLETE",
    ERROR_PRE_UPLOAD = "ERROR_PRE_UPLOAD",
    ERROR_POST_UPLOAD = "ERROR_POST_UPLOAD"
}

// Define Step State Type
interface StepState {
    step: STEPS;
}

// Initial State
const initialState: StepState = {
    step: STEPS.APPLY,
};

// Create Redux Slice
const stepSlice = createSlice({
    name: "step",
    initialState,
    reducers: {
        setStep: (state, action: PayloadAction<STEPS>) => {
            state.step = action.payload;
        },
        resetStep: () => initialState,
    },
});

// Export actions and reducer
export const { setStep, resetStep } = stepSlice.actions;
export default stepSlice.reducer;