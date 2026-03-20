import { createSlice, PayloadAction } from "@reduxjs/toolkit";

interface ApplicationState {
    applicationId: string | null;
    resumeTitle: string | null;
    firstName: string | null;
    lastName: string | null;
    email: string | null;
}

const initialState: ApplicationState = {
    applicationId: null,
    resumeTitle: null,
    firstName: null,
    lastName: null,
    email: null
};

const applicationSlice = createSlice({
    name: "application",
    initialState,
    reducers: {
        setApplicationId: (state, action: PayloadAction<string>) => {
            state.applicationId = action.payload;
        },
        setResumeTitle: (state, action: PayloadAction<string | null>) => {
            state.resumeTitle = action.payload;
        },
        setFirstName: (state, action: PayloadAction<string | null>) => {
            state.firstName = action.payload;
        },
        setLastName: (state, action: PayloadAction<string | null>) => {
            state.lastName = action.payload;
        },
        setFullName: (state, action: PayloadAction<string | null>) => {
            state.firstName = action.payload;
        },
        setEmail: (state, action: PayloadAction<string | null>) => {
            state.email = action.payload;
        },
    },
});

export const { setApplicationId, setResumeTitle, setLastName, setFirstName, setFullName, setEmail} = applicationSlice.actions;
export default applicationSlice.reducer;