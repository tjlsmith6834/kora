import React, { ReactNode } from "react";
import Spinner from "../spinner/spinner";

interface LoaderProps {
	children: ReactNode;
	loading: boolean
	error: boolean
	errorText?: string
}

const Loader: React.FC<LoaderProps> = ({ children, loading = false, error = false, errorText = "Error!" }) => {
	return (
		<div className="loader">
			{loading ? (
				<Spinner/>
			) : error ? (
				<p>errorText</p>
			) : (
				children
			)}
		</div>
	);
}

export default Loader;