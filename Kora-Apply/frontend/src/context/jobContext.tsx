import React, { createContext, useContext } from "react";

interface JobContextType {
	jobID: string;
	publicKey: string;
}

const JobContext = createContext<JobContextType | undefined>(undefined);

export const JobProvider: React.FC<{
	jobID: string;
	publicKey: string;
	children: React.ReactNode;
}> = ({ jobID, publicKey, children }) => {
	return (
		<JobContext.Provider value={{ jobID, publicKey }}>
			{children}
		</JobContext.Provider>
	);
};

// Hook to access both jobID and publicKey
export const useJobContext = (): JobContextType => {
	const context = useContext(JobContext);
	if (!context) {
		throw new Error("useJobContext must be used within a JobProvider");
	}
	return context;
};

// Optional: keep these if you want individual hooks
export const useJobID = (): string => useJobContext().jobID;
export const usePublicKey = (): string => useJobContext().publicKey;