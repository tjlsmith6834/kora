import React, {
	createContext,
	useContext,
	useState,
	ReactNode,
	useEffect
} from "react";

interface AuthContext {
	isLoggedIn: boolean;
	authLoading: boolean;
	login: (token: string) => void;
	logout: () => void;
}

const AuthContext = createContext<AuthContext | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
	const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
	const [authLoading, setAuthLoading] = useState<boolean>(true); // <-- NEW

	useEffect(() => {
		const token = localStorage.getItem("access_token");
		if (token) {
			setIsLoggedIn(true);
		}
		setAuthLoading(false); // <-- Done checking
	}, []);

	function login(token: string) {
		localStorage.setItem("access_token", token);
		setIsLoggedIn(true);
	}

	function logout() {
		localStorage.removeItem("access_token");
		setIsLoggedIn(false);
	}

	return (
		<AuthContext.Provider value={{ isLoggedIn, authLoading, login, logout }}>
			{children}
		</AuthContext.Provider>
	);
};

export function useAuth() {
	const ctx = useContext(AuthContext);
	if (!ctx) {
		throw new Error("useAuth must be used inside an AuthProvider");
	}
	return ctx;
}