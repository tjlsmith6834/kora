import React from "react";

interface SpinnerProps {
}

const Spinner: React.FC<SpinnerProps> = ({}) => {
    return (
		<>
		    <style>
			    {`
			        .spinner-container {
			          display: flex;
			          flex-direction: column;
			          align-items: center;
			          justify-content: center;
			          margin-top: var(--spacing-md);
			        }
			
			        .spinner {
			          width: var(--spacing-lg);
			          height: var(--spacing-lg);
			          border: 3px solid rgba(0, 0, 0, 0.1);
			          border-top-color: var(--color-spinner);
			          border-radius: 50%;
			          animation: kora-spin 1s linear infinite;
			        }
			
			        @keyframes kora-spin {
			          from { transform: rotate(0deg); }
			          to   { transform: rotate(360deg); }
			        }
		        `}
			</style>
			<div className="spinner-container">
				<div className="spinner"></div>
			</div>
		</>
)
	;
};

export default Spinner;