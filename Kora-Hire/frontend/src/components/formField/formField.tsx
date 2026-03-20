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
	);
};

export default FormField;