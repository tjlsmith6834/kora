import React, { createContext, useContext, useReducer, ReactNode, Dispatch } from "react";

type InterviewModalState = {
  isModalOpen: boolean;
  modalStage: string;
  applicationId: string | null;
};

type InterviewModalAction =
	| { type: "OPEN_MODAL" }
	| { type: "CLOSE_MODAL" }
	| { type: "OPEN_MODAL_STAGE"; payload: string }
	| { type: "SET_APPLICATION_ID"; payload: string | null };

const initialState: InterviewModalState = {
  isModalOpen: false,
  modalStage: "INTERVIEWER_QUESTION",
  applicationId: null,
};

function reducer(state: InterviewModalState, action: InterviewModalAction): InterviewModalState {
  switch (action.type) {

    case "CLOSE_MODAL":
      return { ...state, isModalOpen: false, modalStage: initialState.modalStage };

    case "OPEN_MODAL_STAGE":
      return { ...state, isModalOpen: true, modalStage: action.payload };

    case "SET_APPLICATION_ID":
      return { ...state, applicationId: action.payload };

    default:
      return state;
  }
}

type InterviewModalContextValue = {
	state: InterviewModalState;
	dispatch: Dispatch<InterviewModalAction>;
};

const InterviewModalContext = createContext<InterviewModalContextValue | undefined>(undefined);

export function InterviewModalProvider({ children }: { children: ReactNode }) {
	const [state, dispatch] = useReducer(reducer, initialState);

	return (
		<InterviewModalContext.Provider value={{ state, dispatch }}>
			{children}
		</InterviewModalContext.Provider>
	);
}

export function useInterviewModal() {
	const ctx = useContext(InterviewModalContext);
	if (!ctx) throw new Error("useInterviewModal must be used within an InterviewModalProvider");
	return ctx;
}