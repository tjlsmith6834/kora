import React, { useEffect, useState } from "react";
import { useParams, useLocation } from "react-router-dom";

import {
	getApplicationById,
	getApplicationRubric,
	getApplicationFormQuestionAnswers,
	getApplicationInterviewQuestionAnswers,
	postApplicationInterviewQuestionAnswer
} from "../hooks/useApplicationApi";
import { getJobRubric } from "../hooks/useJobsApi"

import { QAResponse } from "../types/applicantProfile";
import { Profile, ProfileCategoryScore } from "../types/profiles"
import { Rubric } from "../types/job"

import {useInterviewModal} from "../context/InterviewModalContext";

import Header from "../components/header/header";
import Card from "../components/card/card"
import ApplicantSummary from "../components/applicantSummary/applicantSummary";
import BarChart from "../components/barchart/barChart";
import ApplicantBulletDisplay from "../components/applicantBulletDisplay/applicantBulletDisplay";
import VerticalDisplay from "../components/verticalDisplay/verticalDisplay";
import Loader from "../components/loader/loader";
import DisplayList from "../components/displayList/displayList";
import ActionButton from "../components/actionButton/actionButton";

import InterviewModal from "../modals/interviewModal/InterviewModal";

const INTERVIEW_QA_CACHE: Map<string, QAResponse[]> = new Map();

function loadCachedInterviewQA(applicationId: string): QAResponse[] | null {
	const mem = INTERVIEW_QA_CACHE.get(applicationId);

	if (mem && Array.isArray(mem)) return mem;

	try {
		const raw = localStorage.getItem(`interviewQA:${applicationId}`);
		if (!raw) return null;
		const parsed = JSON.parse(raw);
		if (Array.isArray(parsed)) {
			INTERVIEW_QA_CACHE.set(applicationId, parsed);
			return parsed;
		}
	}catch {

	}
	return null;
}

function saveCachedInterviewQA(applicationId: string, data: QAResponse[]) {
	INTERVIEW_QA_CACHE.set(applicationId, data);
	try {
		localStorage.setItem(`interviewQA:${applicationId}`, JSON.stringify(data));
	}catch {

	}
}

const ApplicantDetailsPage: React.FC = () => {
	const location = useLocation();

	const { state, dispatch } = useInterviewModal();

	const { applicationId } = useParams<{ applicationId?: string }>();
	const { jobId = "", jobTitle = "", applicant, jobRubric } = (location.state || {}) as {
		jobId: string;
		jobTitle: string;
		applicant?: Profile;
		jobRubric?: Rubric;
	};

	const [activeTab, setActiveTab] = useState("summary");

	const [applicationSummary, setApplicationSummary] = useState<Profile | undefined>(applicant);
	const [formQuestionResponses, setFormQuestionResponses] = useState<QAResponse[]>([])
	const [rubricData, setRubricData] = useState<ProfileCategoryScore[]>([]);

	const [interviewQuestionResponses, setInterviewQuestionResponses] = useState<QAResponse[]>([])
	const [loadingInterviewQuestionResponses, setLoadingInterviewQuestionsResponses] = useState<boolean>(true)
	const cachedInterviewQA = applicationId
		? loadCachedInterviewQA(applicationId)
		: null;

	useEffect(() => {
		if (!applicationId) return;
		dispatch({ type: "SET_APPLICATION_ID", payload: applicationId });

		const fetchApplicantSummary = async () => {
			try {
				if (applicant) {
					// Use passed applicant from state
					setApplicationSummary(applicant);
				} else {
					// Fall back to API fetch
					const data = await getApplicationById(applicationId);
					setApplicationSummary(data);
				}
			} catch (error) {
				console.error("Failed to fetch applicant summary:", error);
			}
		};

		const fetchFormQuestionResponses = async() => {
			try {
				const qaResponses = await getApplicationFormQuestionAnswers(applicationId)
				setFormQuestionResponses(qaResponses)
			} catch (error) {
					console.error("Failed to fetch form question answers:", error);
				}
		}

		const fetchRubricData = async () => {
			if (!applicationId) return;

			try {
				// Use passed-in rubric or fetch it
				const rubric = jobRubric ?? await getJobRubric(jobId);

				// Use rubric scores from applicant if present, otherwise fetch
				const profileRubric = applicant?.profile_rubric ?? await getApplicationRubric(applicationId);

				console.log("Rubric:", rubric);
				console.log("Profile Rubric:", profileRubric);

				if (!rubric) {
					console.warn("No rubric found.");
					return;
				}

				if (!applicant) {
					console.warn("No applicant passed in state — skipping rubric merge.");
					return;
				}

				const merged = mergeRubricAndProfile(rubric, {
					...applicant,
					profile_rubric: profileRubric,
				});
				setRubricData(merged);
				console.log("Merged rubric data:", merged);
				setRubricData(merged);
			} catch (err) {
				console.error("Error fetching rubric/profile data", err);
			}
		};

		const fetchInterviewQuestionResponses = async () => {
			if (!applicationId) return;

			if (cachedInterviewQA) {
				setInterviewQuestionResponses(cachedInterviewQA);
				setLoadingInterviewQuestionsResponses(false);
				return;
			}

			try {
				setLoadingInterviewQuestionsResponses(true);
				const data: QAResponse[] =
				await getApplicationInterviewQuestionAnswers(applicationId);

				setInterviewQuestionResponses(data);
				saveCachedInterviewQA(applicationId, data);
			} catch (error) {
				console.error("Failed to fetch interview questions and answers", error);
			} finally {
				setLoadingInterviewQuestionsResponses(false);
			}
		};

		fetchApplicantSummary();
		fetchFormQuestionResponses()
		fetchRubricData()
		fetchInterviewQuestionResponses()
	}, [applicationId]);

	function mergeRubricAndProfile(
		rubric: Rubric,
		profile: Profile
	): ProfileCategoryScore[] {
		const profileMap = new Map(
			profile.profile_rubric.category_scores.map((score) => [score.category_id, score])
		);

		return rubric.categories.map((cat) => {
			const profileScore = profileMap.get(cat.category_id);

			return {
				category_id: cat.category_id,
				category: cat.category,
				category_score: profileScore?.category_score ?? 0,
				category_score_reason: profileScore?.category_score_reason ?? "No score provided",
			};
		});
	}

	const viewResume = (applicationId: string) => {
		const resumeUrl = `${process.env.REACT_APP_BFF_BASE_URL}/applications/${applicationId}/resume/`;
		window.open(resumeUrl, "_blank");
	};

	const handleAddInterviewClick = () => {
		if (!applicationId) return; // optional guard
		dispatch({ type: "SET_APPLICATION_ID", payload: applicationId });
		dispatch({ type: "OPEN_MODAL_STAGE", payload: "INTERVIEWER_QUESTION" });
	};

	const handleInterviewQASaved = async (qa: QAResponse): Promise<void> => {
	  if (!applicationId) return;

	  // Snapshot current state for rollback
	  const prev = interviewQuestionResponses;

	  // ✅ optimistic UI + cache
	  const next = [qa, ...prev];
	  setInterviewQuestionResponses(next);
	  saveCachedInterviewQA(applicationId, next);

	  try {
	    // ✅ persist to DB
	    await postApplicationInterviewQuestionAnswer(applicationId, qa);

	    // Optional: if you want canonical server ordering / ids:
	    const fresh = await getApplicationInterviewQuestionAnswers(applicationId);
	    setInterviewQuestionResponses(fresh);
	    saveCachedInterviewQA(applicationId, fresh);

	  } catch (err) {
	    // ✅ rollback UI + cache
	    setInterviewQuestionResponses(prev);
	    saveCachedInterviewQA(applicationId, prev);

	    // ✅ propagate error so editor toast shows failure
	    throw err;
	  }
	};

	const breadcrumbs = [
		{ label: "Open Roles", path: "/jobs", isActive: false },
		{ label: jobTitle || "Loading...", path: `/jobs/${jobId}/applicants`, isActive: false },
		{ label: applicationSummary?.applicant_name || "Loading...", path: "", isActive: true },
	];

	const tabsConfig = [
		{ id: "summary", label: "Summary" },
		{ id: "resume", label: "Resume" },
		{ id: "interview", label: "Interview QA"}
	];

	return (
		<div>
			<Header
				title={applicationSummary?.applicant_name || "Applicant Details"}
				crumbs={breadcrumbs}
				tabs={tabsConfig}
				onTabChange={(tabId) => setActiveTab(tabId)}
				activeTab={activeTab}
			/>
			{activeTab === "summary" && (
				<Loader
					loading={!applicant}
					error={false}
				>
					<section>
						<VerticalDisplay>
							<Card isClickable={false}>
								{applicationSummary ? (
									<ApplicantSummary
										name={applicationSummary.applicant_name}
										summary={applicationSummary.profile_score.headline}
										score={applicationSummary.profile_score.profile_score}
										applicant_career={applicationSummary.applicant_career}
										applicant_roles={applicationSummary.recent_roles}
									/>
								) : (
									<p>Loading...</p>
								)}
							</Card>
							{ (applicationSummary?.linkedin_url || applicationSummary?.portfolio_url || applicationSummary?.github_url) &&(
								<Card isClickable={false}>
									<ul style={{ paddingLeft: "1rem", paddingTop: "1rem", margin: 0 }}>
										{applicationSummary?.linkedin_url && (
											<li>
												<a href={applicationSummary.linkedin_url} target="_blank" rel="noopener noreferrer">
													LinkedIn →
												</a>
											</li>
										)}
										{applicationSummary?.portfolio_url && (
											<li>
												<a href={applicationSummary.portfolio_url} target="_blank" rel="noopener noreferrer">
													Portfolio →
												</a>
											</li>
										)}
										{applicationSummary?.github_url && (
											<li>
												<a href={applicationSummary.github_url} target="_blank" rel="noopener noreferrer">
													GitHub →
												</a>
											</li>
										)}
									</ul>
								</Card>
							)}
							<div>
								<h2 className="h2-underlined">Candidate Rubric Scores</h2>
								<BarChart canvasId="barChartCanvas" data={rubricData} />
							</div>
							<Card isClickable={false}>
								{applicationSummary ? (
									<ApplicantBulletDisplay
										strengthBullets={applicationSummary.profile_bullets.liked_bullets
											.slice()
											.sort((a, b) => b.order - a.order)
											.map((b) => b.detail)}
										weaknessBullets={applicationSummary.profile_bullets.disliked_bullets
											.slice()
											.sort((a, b) => b.order - a.order)
											.map((b) => b.detail)}
									/>
								) : (
									<p>Loading bullets...</p>
								)}
							</Card>
						</VerticalDisplay>
					</section>
				</Loader>
			)}

			{activeTab === "resume" && (
				<section>
					<Card
						isClickable={true}
						onClick={() => viewResume(applicationId!)}
					>
						<h3>View Full Screen →</h3>
					</Card>
					<iframe
						src={`${process.env.REACT_APP_BFF_BASE_URL}/applications/${applicationId}/resume/`}
						width="100%"
						height="800px"
						title="Resume Preview"
						style={{border: "none"}}
					/>
				</section>
			)}

			{activeTab === "interview" && (
				<section>
					<ActionButton
						onClick={() => handleAddInterviewClick()}
						text="Add a question"
						variant="primary"
					/>
					<Loader
						loading={loadingInterviewQuestionResponses}
						error={false}
					>
						<DisplayList
							emptyText="No interview questions yet!"
						>
						{ interviewQuestionResponses.map((qa, index) => (
								<Card
									key = {index}
									isClickable={false}
								>
									<h3>Question:</h3>
									<p>{qa.question}</p>
									<h3>Answer:</h3>
									<p>{qa.answer}</p>
								</Card>
							))}
						</DisplayList>
					</Loader>
				</section>
			)}
			<InterviewModal
				isOpen={state.isModalOpen}
				modalStage={state.modalStage}
				onInterviewQASaved={handleInterviewQASaved}
			/>
		</div>
	);
};

export default ApplicantDetailsPage;