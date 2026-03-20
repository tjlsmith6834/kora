// components/FormField.tsx
import React from "react";
import "./formField.css";

interface FormFieldProps {
	  id: string;
	  label: string;
	  required?: boolean;
	  type?: string;
	  isTextarea?: boolean;
	  helperText?: string;
	  errorText?: string;
	  value: string;
	  onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
}

const FormField: React.FC<FormFieldProps> = ({
	id,
	label,
	required = false,
	type = "text",
	isTextarea,
	helperText,
	errorText,
	value,
	onChange,
}) => {
	const errorId = `${id}-error`;
	const helpId = `${id}-help`;
	const hasError = Boolean(errorText);

	return (
		<>
			<style>
	            {`
		            .form-group {
					    width: 100%;
					    max-width: 100%;
					    display: flex;
					    flex-direction: column;
					    margin-bottom: var(--spacing-sm);
					}
					
					label {
					    font-size: var(--font-size-h3);
					    margin-bottom: var(--spacing-xs);
					}
					
					.required {
					    color: red;
					    margin-right: 4px;
					}
					
					input {
					    font-family: var(--typeface-user-input);
					    padding: var(--spacing-xs);
					    border: var(--input-border);
					    border-radius: var(--radius-sm);
					    font-size: var(--font-size-user-input);
					    margin: 0;
					}
					
					textarea {
					    font-family: var(--typeface-user-input);
					    padding: var(--spacing-xs);
					    border: var(--input-border);
					    border-radius: var(--radius-sm);
					    font-size: var(--font-size-user-input);
					    overflow-y: auto;     /* Enable vertical scrolling */
					    overflow-x: hidden;
					    resize: none;
					}
					
					input[aria-invalid="true"] {
					    border-color: red;
					}
	            `}
			</style>
			<div className="form-group">
				<label htmlFor={id}>
				    {label}
				</label>
				{isTextarea ?
					(
						<textarea
							id={id}
							required={required}
							value={value}
							onChange={onChange}
							aria-invalid={hasError}
							aria-describedby={hasError ? errorId : helperText ? helpId : undefined}
							rows={4}
						/>
					) : (
						<input
							id={id}
							type={type}
							required={required}
							value={value}
							onChange={onChange}
							aria-invalid={hasError}
							aria-describedby={hasError ? errorId : helperText ? helpId : undefined}
						/>
					)
				}
				{hasError && <p id={errorId} className="error-text">{errorText}</p>}
				{!hasError && helperText && <p id={helpId} className="helper-text">{helperText}</p>}
			</div>
		</>
	);
};

export default FormField;