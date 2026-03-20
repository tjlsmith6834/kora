import React from "react";
import "./spinner.css";

interface SpinnerProps {
}

const Spinner: React.FC<SpinnerProps> = ({}) => {
    return (
	    <div className="spinner-container">
		    <div className="spinner2"></div>
		</div>
	);
};

export default Spinner;