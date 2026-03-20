import React, {useState, useRef, FormEvent} from "react";
import VerticalDisplay from "../../../components/verticalDisplay/verticalDisplay";
import HorizontalDisplay from "../../../components/horizontalDisplay/horizontalDisplay";
import SmallButton from "../../../components/smallButton/smallButton";
import Spinner from "../../../components/spinner/spinner";
import ActionButton from "../../../components/actionButton/actionButton";
import {postFormQuestions} from "../../../hooks/useJobsApi";
import toast from "react-hot-toast";


interface FormQuestionEditorProps {
	jobId: string
    formQuestions?: string[];
	saveFormQuestions?: (updated: string[]) => void;
}

const FormQuestionEditor: React.FC<FormQuestionEditorProps> = ({
	jobId,
	formQuestions = [],
	saveFormQuestions
}) => {

	const formRef = useRef<HTMLFormElement>(null);
	const [questions, setQuestions] = useState<string[]>(formQuestions.length > 0 ? formQuestions : [""]);
	const [saving, setSaving] = useState<boolean>(false)

	const handleChangeQuestion = (index: number, value: string) => {
		const updated = [...questions];
		updated[index] = value;
		setQuestions(updated);
	};

	const handleRemoveQuestion = (index: number) => {
		const updated = [...questions];
		updated.splice(index, 1);
		setQuestions(updated);
	};

	const handleAddQuestion = (e: React.MouseEvent) => {
		e.preventDefault();
		setQuestions([...questions, ""]);
	};

	const handleSubmit = async (e: FormEvent) => {
		e.preventDefault();
		setSaving(true);

		const toastId = toast.loading("Saving questions...");

		const cleanedQuestions = questions
		.map(q => q.trim())
		.filter(q => q.length > 0);

		try {
			const savedQuestions = await postFormQuestions(jobId, cleanedQuestions);
			if (savedQuestions && saveFormQuestions) {
				saveFormQuestions(savedQuestions)
			}
			toast.success("Questions saved!", { id: toastId });
		} catch (error) {
			toast.error("Oops something went wrong. Questions not saved.", { id: toastId });
		} finally {
			setSaving(false);
		}
	};

	return (
	    <form
		    ref={formRef}
		    onSubmit={handleSubmit}
		>
		    <VerticalDisplay align={"flex-start"}>
				<h2>Questions:</h2>
			    {questions.map((question, index) => (
					<HorizontalDisplay key={index} gap="var(--spacing-xs)">
						<input
							type="text"
							required
							value={question}
							onChange={(e) => handleChangeQuestion(index, e.target.value)}
							style={{ flex: 1 }}
						/>
						<SmallButton onClick={() => handleRemoveQuestion(index)}>-</SmallButton>
					</HorizontalDisplay>
			    ))}
			    <button onClick={handleAddQuestion}>
				    ➕ Add New Question
			    </button>
		        {!saving ? (
				    <ActionButton
					    onClick={() => formRef.current?.requestSubmit()}
					    text="Submit"
					    variant= "primary"
				    />
		        ) : (
					<Spinner/>
		        )}
            </VerticalDisplay>
        </form>
	);
}

export default FormQuestionEditor;