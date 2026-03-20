import React, { FormEvent, useRef, useState, useEffect} from "react";

import { getFormQuestions, getLinkConfig } from "../hooks/useJobsApi";
import useApplicationApi from "../hooks/useApplicationApi";

import { useJobID } from "../context/jobContext";

import {LinkConfig} from "../types/job";

import Card from "../components/card/card"
import VerticalDisplay from "../components/verticalDisplay/verticalLayout";
import HorizontalDisplay from "../components/horizontalDisplay/horizontalDisplay";
import FormField from "../components/formField/formField"
import FileDrop from "../components/fileDrop/fileDrop";
import ActionButtonContainer from "../components/actionButtonContainer/actionButtonContainer";
import Loader from "../components/loader/loader"

interface ResumeCardProps {
}

const ResumeCard: React.FC<ResumeCardProps> = ({
}) => {
	const formRef = useRef<HTMLFormElement>(null);


	const jobId = useJobID();
	const [loading, setLoading] = useState<boolean>(true);
	const [formQuestions, setFormQuestions] = useState<string[]>([]);
	const [linkConfig, setLinkConfig] = useState<LinkConfig | null>(null)
	const showAnyLinks = linkConfig?.require_linkedin || linkConfig?.require_portfolio || linkConfig?.require_github;


	const [resume, setResume] = useState<File | null>(null);
	const [lastName, setLastName] = useState('');
    const [firstName, setFirstName] = useState('');
    const [email, setEmail] = useState('');
	const [linkedin, setLinkedin] = useState('');
	const [portfolio, setPortfolio] = useState('');
	const [github, setGithub] = useState('');
	const [formAnswers, setFormAnswers] = useState<string[]>([]);

	useEffect(() => {
		if (!jobId) return;

		const loadData = async () => {
			setLoading(true);

			try {
				const [questions, linkConfig] = await Promise.all([
					getFormQuestions(jobId),
					getLinkConfig(jobId)
				]);

				if (questions) {
					setFormQuestions(questions);
					setFormAnswers(questions.map(() => ""));
				}

				if (linkConfig) {
					setLinkConfig(linkConfig);

				}
			} catch (error) {
				console.error("❌ Error loading form questions or link config:", error);
			} finally {
				setLoading(false);
			}
		};

		loadData();

	}, [jobId]);

    const { handleApplicationUpload, handleSaveFormQuestionAnswer } = useApplicationApi();

	const applicationUpload = async (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault();

		if (!resume || !lastName.trim() || !firstName.trim() || !email.trim()) {
			alert("Please complete all fields.");
			return;
		}

		try {
			const savedAppId: string = await handleApplicationUpload(
				firstName,
				lastName,
				email,
				resume,
				linkedin,
				portfolio,
				github,
			);

			await Promise.all(
				formQuestions.map((question, index) =>
					handleSaveFormQuestionAnswer(question, formAnswers[index], savedAppId)
				)
			);

			console.log("Application and all form answers saved!");
		} catch (err) {
			console.error("Error uploading application:", err);
		}
	};

    return (
	    <Card>
		    <Loader
			    loading={loading}
			    error={false}
		    >
			    <h1>Let's get to know you!</h1>
			    <form
				    ref={formRef}
				    onSubmit={applicationUpload}
			    >
				    <VerticalDisplay align={"flex-start"}>
					    <h2>Personal Information:</h2>
				        <HorizontalDisplay>
	                        <FormField
								id="firstName"
								label="First Name"
								required = {true}
								type="text"
								value={firstName}
								onChange={(e) => setFirstName(e.target.value)}
							/>
	                        <FormField
								id="lastName"
								label="Last Name"
								required
								type="text"
								value={lastName}
								onChange={(e) => setLastName(e.target.value)}
							/>
				        </HorizontalDisplay>
					    <FormField
							id="email"
							label="Email"
							required
							type="email"
							value={email}
							onChange={(e) => setEmail(e.target.value)}
						/>

					    {showAnyLinks && (
							<>
								<h2>Links:</h2>
								{linkConfig.require_linkedin && (
									<FormField
										id="linkedin"
										label="LinkedIn URL"
										required
										type="url"
										value={linkedin}
										onChange={(e) => setLinkedin(e.target.value)}
									/>
								)}
								{linkConfig.require_portfolio && (
									<FormField
										id="portfolio"
										label="Portfolio URL"
										required
										type="url"
										value={portfolio}
										onChange={(e) => setPortfolio(e.target.value)}
									/>
								)}
								{linkConfig.require_github && (
									<FormField
										id="github"
										label="GitHub URL"
										required
										type="url"
										value={github}
										onChange={(e) => setGithub(e.target.value)}
									/>
								)}
							</>
						)}
					    {formQuestions.length > 0 && (
							<>
								<h2>Just a couple more questions:</h2>
								{formQuestions.map((question, index) => (
									<FormField
										key={index}
										id={`form-question-${index}`}
										label={question}
										required
										type="text"
										value={formAnswers[index] || ""}
										onChange={(e) => {
											const updatedAnswers = [...formAnswers];
											updatedAnswers[index] = e.target.value;
											setFormAnswers(updatedAnswers);
										}}
									/>
								))}
							</>
						)}
					    <h2>Resume:</h2>
					    <FileDrop onFileSelect={setResume}/>
					    <ActionButtonContainer
						    centerButton={{
							    onClick: () => formRef.current?.requestSubmit(),
							    text: "Submit",
							    variant: "primary",
							    disabled: !resume || !lastName?.trim() || !firstName?.trim() || !email?.trim()
						    }}
					    />
				    </VerticalDisplay>
			    </form>
		    </Loader>
	    </Card>
    );
};

export default ResumeCard;