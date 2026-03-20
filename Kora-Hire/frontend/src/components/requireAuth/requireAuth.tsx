// components/requireAuth/requireAuth.tsx
import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import Spinner from "../spinner/spinner"; // Or use a spinner / null if you prefer

const RequireAuth: React.FC = () => {
	const { isLoggedIn, authLoading } = useAuth();

	if (authLoading) {
		return <Spinner />;
	}

	if (!isLoggedIn) {
		return <Navigate to="/" replace />;
	}

	return <Outlet />;
};

export { RequireAuth };