import React, { useState, useRef, FormEvent } from "react";
import VerticalDisplay from "../../../components/verticalDisplay/verticalDisplay";
import Spinner from "../../../components/spinner/spinner";
import ActionButton from "../../../components/actionButton/actionButton";
import toast from "react-hot-toast";

import {QAResponse} from "../../../types/applicantProfile";

interface InterviewQuestionEditorProps {
  applicationId: string;
  suggestQuestion: boolean;
  onSave: (qa: QAResponse) => Promise<void>;
}

const FormQuestionEditor: React.FC<InterviewQuestionEditorProps> = ({
  applicationId,
	onSave,
  suggestQuestion = false,
}) => {
  const formRef = useRef<HTMLFormElement>(null);
  const [question, setQuestion] = useState<string>("");
  const [answer, setAnswer] = useState<string>("");
  const [saving, setSaving] = useState<boolean>(false);

  const PM_QUESTION_SUGGESTIONS: string[] = [
	  "Give an example of a product you improved post-launch. What signal told you it needed work, what did you change, and what changed in adoption or outcomes?",
	  "Tell me about a time you led user or customer research that changed your roadmap. What did you learn and what did you do differently as a result?",
	  "Describe how you’ve implemented or evolved an agile workflow on a team. What specific process change did you introduce, and what improved (cycle time, clarity, throughput, quality)?",
	  "Walk me through a strong set of requirements or user stories you created for a complex feature. What was included, and how did it reduce ambiguity for engineering and stakeholders?",
	  "Tell me about a time you upskilled or coached teammates (technical or non-technical). What did you teach, and what changed afterward?"
	];

	const handleSubmit = async (e: FormEvent) => {
	  e.preventDefault();
	  setSaving(true);

	  const toastId = toast.loading("Saving interview answer...");
	  try {
	    const newQA: QAResponse = { question, answer };

	    await onSave(newQA);

	    setQuestion("");
	    setAnswer("");
	    toast.success("Answer saved!", { id: toastId });
	  } catch (error) {
	    toast.error("Oops something went wrong. Answer not saved.", { id: toastId });
	  } finally {
	    setSaving(false);
	  }
	};

  const suggestNewQuestion = () => {
  const randomIndex = Math.floor(
    Math.random() * PM_QUESTION_SUGGESTIONS.length
  );
  setQuestion(PM_QUESTION_SUGGESTIONS[randomIndex]);
};

  return (
    <form ref={formRef} onSubmit={handleSubmit}>
      <VerticalDisplay align={"flex-start"} justify={"center"}>
      <div
      style={{
            width: "100%",
          }}
      >
        <h3>Question:</h3>
	      <textarea
		      required
		      value={question}
		      onChange={(e) => setQuestion(e.target.value)}
		      rows={4}
		      style={{width: "100%", boxSizing: "border-box", display: "block"}}
	      />

      </div>
	      <div
		      style={{
			      width: "100%",
		      }}>

		      <h3>Answer:</h3>
		      <textarea
			      required
			      value={answer}
			      onChange={(e) => setAnswer(e.target.value)}
			      rows={6}
			      style={{width: "100%", boxSizing: "border-box", display: "block"}}
		      />
	      </div>
	      {!saving ? (
			  <>
		      <ActionButton
			      onClick={() => formRef.current?.requestSubmit()}
			      text="Submit"
			      variant="primary"
			      disabled={!question.trim() || !answer.trim()}
            />
		      <ActionButton
			      onClick={suggestNewQuestion}
			      text="Suggest Questions"
			      variant="tertiary"
		      />
		      </>
        ) : (
          <Spinner />
        )}
      </VerticalDisplay>
    </form>
  );
};

export default FormQuestionEditor;