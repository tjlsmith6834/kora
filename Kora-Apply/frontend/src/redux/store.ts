import { configureStore } from "@reduxjs/toolkit";
import stepReducer from "./slices/stepSlice";
import thinkingReducer from "./slices/thinkingSlice"
import applicationReducer from "./slices/applicationSlice"
import questionReducer from "./slices/questionSlice";

// Define Root State Type
export const store = configureStore({
    reducer: {
        step: stepReducer,
        thinking: thinkingReducer,
        application: applicationReducer,
        questions: questionReducer,
    },
});

// Type for the Redux State
export type RootState = ReturnType<typeof store.getState>;

// Type for Dispatch
export type AppDispatch = typeof store.dispatch;

export default store;