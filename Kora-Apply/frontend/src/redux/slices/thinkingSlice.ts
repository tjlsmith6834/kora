import { createSlice, PayloadAction } from "@reduxjs/toolkit";

// Define the Question State Type
interface ThinkingState {
    thinking: boolean;
}

// Initial state
const initialState: ThinkingState = {
    thinking: false,
};

// Create the slice
const thinkingSlice = createSlice({
    name: "thinking",
    initialState,
    reducers: {
        setThinking: (state, action: PayloadAction<boolean>) => {
            state.thinking = action.payload;
        },
    },
});

// Export actions and reducer
export const { setThinking } = thinkingSlice.actions;
export default thinkingSlice.reducer;