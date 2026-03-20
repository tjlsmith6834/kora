import { createSlice, PayloadAction } from "@reduxjs/toolkit";

// Define the Question State Type
interface QuestionState {
    questions: string[];
    currentIndex: number;
    currentResponse: string;
}

// Initial state
const initialState: QuestionState = {
    questions: [],
    currentIndex: 0,
    currentResponse: "",
};

// Create the slice
const questionSlice = createSlice({
    name: "questions",
    initialState,
    reducers: {
        setQuestions: (state, action: PayloadAction<string[]>) => {
            state.questions = action.payload;
        },
        setCurrentIndex: (state, action: PayloadAction<number>) => {
            state.currentIndex = action.payload;
        },
        setCurrentResponse: (state, action: PayloadAction<string>) => {
            state.currentResponse = action.payload;
        },
    },
});

// Export actions and reducer
export const { setQuestions, setCurrentIndex, setCurrentResponse } = questionSlice.actions;
export default questionSlice.reducer;