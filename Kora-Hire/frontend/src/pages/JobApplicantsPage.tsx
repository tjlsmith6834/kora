import React, { useEffect, useState, FormEvent, useRef} from "react";
import Modal from "react-modal";
import {useParams, useNavigate, useLocation, Navigate} from "react-router-dom";
import toast from "react-hot-toast";

import { useJobModal } from "../context/JobModalContext";

import { getJobDetails, getJobRubric, getJobDescriptionFileName, getFormQuestions } from "../hooks/useJobsApi"
import { getApplicantsForJob, putHideApplication } from "../hooks/useApplicationApi";
import { getPublicKey } from "../hooks/useUserAuthApi"

import { Profile} from "../types/profiles";
import { Rubric } from "../types/job"

import Card from "../components/card/card"
import Header from "../components/header/header";
import SmallButton from "../components/smallButton/smallButton"
import DisplayList from "../components/displayList/displayList";
import ApplicantSummary from "../components/applicantSummary/applicantSummary";
import ApplicantBulletDisplay from "../components/applicantBulletDisplay/applicantBulletDisplay";
import RubricTable from "../components/rubricTable/rubricTable";
import FileUploader from "../components/fileUploader/fileUploader";
import ActionButtonContainer from "../components/actionButtonContainer/actionButtonContainer";
import JobModal from "../modals/jobModal/JobModal";
import CardContent from "../components/cardContent/cardContent";
import HorizontalDisplay from "../components/horizontalDisplay/horizontalDisplay";
import VerticalDisplay from "../components/verticalDisplay/verticalDisplay";
import ActionButton from "../components/actionButton/actionButton";
import Loader from "../components/loader/loader";

Modal.setAppElement("#root");

const APPLICANTS_CACHE: Map<string, Profile[]> = new Map();

function loadCachedApplicants(jobId: string): Profile[] | null {
  const mem = APPLICANTS_CACHE.get(jobId);
  if (mem && Array.isArray(mem)) return mem;

  try {
    const raw = sessionStorage.getItem(`applicants:${jobId}`);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (Array.isArray(parsed)) {
      APPLICANTS_CACHE.set(jobId, parsed);
      return parsed;
    }
  } catch {}
  return null;
}

function saveCachedApplicants(jobId: string, data: Profile[]) {
  APPLICANTS_CACHE.set(jobId, data);
  try {
    sessionStorage.setItem(`applicants:${jobId}`, JSON.stringify(data));
  } catch {}
}

const JobApplicantsPage: React.FC =() => {

	const navigate = useNavigate();
	const location = useLocation()

	const { state, dispatch } = useJobModal();

	const formRef = useRef<HTMLFormElement>(null);

	const { jobId } = useParams<string>();
	const [jobTitle, setJobTitle] = useState(location.state?.jobTitle ?? null);

	const [loadingApplicants, setLoadingApplicants] = useState<boolean>(true)
	const [errorApplicants, setErrorApplicants] = useState<boolean>(false)
	const [applicants, setApplicants] = useState<Profile[]>([]);
	type ExpandedSection = { id: string; type: "bullets" | "links" } | null;
	const [expandedSection, setExpandedSection] = useState<ExpandedSection>(null);
	const toggleSection = (id: string, type: "bullets" | "links") => {
		setExpandedSection(prev =>
			prev?.id === id && prev.type === type
				? null
				: { id, type }
		);
	};

	const [jobDescriptionFileName, setJobDescriptionFileName] = useState<string | null>(null)
	const [jobDescriptionFileNameError, setJobDescriptionFileNameError] = useState<string | null>(null)

	const [formQuestions, setFormQuestions] = useState<string[]>([]);

	const [jobRubric, setJobRubric] = useState<Rubric | null>(null);
	const [rubricLoading, setRubricLoading] = useState(true);
	const [rubricError, setRubricError] = useState("");

	const [activeTab, setActiveTab] = useState("applicants");


	useEffect(() => {
  if (!jobId) return;
  dispatch({ type: "SET_JOB_ID", payload: jobId });

  // --- hydrate from cache (no DB) ---
  const cached = loadCachedApplicants(jobId);
  if (cached) {
    setApplicants(cached);
    setLoadingApplicants(false);
  }

  // Fetch details that aren't heavy / or not cached yet
  const fetchJobDetails = async () => {
    try {
      if (!jobTitle) {
        const jobData = await getJobDetails(jobId);
        setJobTitle(jobData.title);
      }
    } catch (error) {
      console.error("Failed to fetch job details", error);
    }
  };

  const fetchJobApplicants = async () => {
    // only hit DB if we do NOT already have cached applicants
    if (cached) return;

    try {
      setLoadingApplicants(true);
      const data: Profile[] = await getApplicantsForJob(jobId);
      setApplicants(data);
      saveCachedApplicants(jobId, data); // <-- cache it
    } catch (error) {
      console.error("Failed to fetch applicants", error);
    } finally {
      setLoadingApplicants(false);
    }
  };

  const fetchJobDescriptionFileName = async () => {
    try {
      const fileName: string | null = await getJobDescriptionFileName(jobId);
      setJobDescriptionFileName(fileName);
    } catch (error) {
      console.error("Failed to fetch job description file name", error);
      setJobDescriptionFileNameError("Error: Failed to retrieve your job description");
    }
  };

  const fetchJobRubric = async () => {
    try {
      const retrievedRubric: Rubric | null = await getJobRubric(jobId);
      setJobRubric(retrievedRubric);
      if (retrievedRubric) {
        dispatch({ type: "SET_EDITOR_RUBRIC", payload: retrievedRubric });
      }
    } catch (error) {
      setRubricError("Failed to fetch rubric data.");
    } finally {
      setRubricLoading(false);
    }
  };

  const fetchFormQuestions = async () => {
    try {
      const data: string[] | null = await getFormQuestions(jobId);
      const list = data ?? [];
      setFormQuestions(list);
      dispatch({ type: "SET_FORM_QUESTIONS", payload: list });
    } catch (error) {
      console.error("Failed to fetch form questions", error);
    }
  };

  fetchJobApplicants();
  fetchJobDetails();
  fetchJobRubric();
  fetchJobDescriptionFileName();
  fetchFormQuestions();
}, [jobId, dispatch]);

	if (!jobId) {
		return <Navigate to="/jobs" replace />;
	}

	const viewResume = (applicationId: string) => {
		const resumeUrl = `${process.env.REACT_APP_BFF_BASE_URL}/applications/${applicationId}/resume/`;
		window.open(resumeUrl, "_blank");
	};

	const handleApplicantClick = (applicant: Profile) => {
		navigate(`/jobs/${jobId}/applicants/${applicant.application_id}`, {
			state: {
				jobId,
				jobTitle,
				applicant,
				jobRubric,
			},
		});
	};

	const handleHideApplicant = async (applicationId: string) => {
	  const toastId = toast.loading("Hiding applicant...");

	  const removedApplicant = applicants.find(app => app.application_id === applicationId);
	  const next = applicants.filter(app => app.application_id !== applicationId);
	  setApplicants(next);
	  if (jobId) saveCachedApplicants(jobId, next); // <-- keep cache fresh

	  try {
	    await putHideApplication(applicationId);
	    console.info(`Application ${applicationId} successfully hidden.`);
	    toast.success("Applicant successfully hidden.", { id: toastId });
	  } catch (error) {
	    console.error("Failed to hide application", error);
	    toast.error("Failed to hide applicant.", { id: toastId });

	    // rollback
	    if (removedApplicant) {
	      const restored = [removedApplicant, ...next];
	      setApplicants(restored);
	      if (jobId) saveCachedApplicants(jobId, restored);
	    }
	  }
	};

	const handleEditJobDescriptionClick = () => {
		dispatch({ type:"OPEN_MODAL", payload:"EDIT_JD"})
	}

	const handleEditFormQuestionsClick = () => {
		dispatch({type:"OPEN_MODAL", payload:"EDIT_FORM_QUESTIONS"})
	}


	const handleEditRubricClick = () => {
		if (jobRubric) {
			dispatch({ type: "SET_EDITOR_RUBRIC", payload: jobRubric });
		}
		dispatch({ type: "OPEN_MODAL", payload: "EDIT_RUBRIC" });
	};


	const breadcrumbs = [
		{ label: "Open Roles", path: "/jobs", isActive: false },
		{ label: jobTitle || "Loading...", path: "", isActive: true },
	];

	const tabsConfig = [
		{ id: "applicants", label: "Applicants" },
		{ id: "role", label: "This Role" },
	];

	const applicantCards = loadingApplicants
	  ? [] // Avoid rendering anything during load
	  : applicants
	      .sort(
	        (a, b) =>
	          (b.profile_score?.profile_score ?? 0) -
	          (a.profile_score?.profile_score ?? 0)
	      )
	      .map((applicant) => {
	        const isBulletsOpen =
	          expandedSection?.id === applicant.application_id &&
	          expandedSection.type === "bullets";
	        const isLinksOpen =
	          expandedSection?.id === applicant.application_id &&
	          expandedSection.type === "links";

	        const strengthBullets = applicant.profile_bullets.liked_bullets
	          .slice()
	          .sort((a, b) => b.order - a.order)
	          .map((bullet) => bullet.detail);

	        const weaknessBullets = applicant.profile_bullets.disliked_bullets
	          .slice()
	          .sort((a, b) => b.order - a.order)
	          .map((bullet) => bullet.detail);

	        const linkedin = applicant.linkedin_url;
	        const portfolio = applicant.portfolio_url;
	        const github = applicant.github_url;

	        return (
	          <React.Fragment key={applicant.application_id}>
	            <HorizontalDisplay align="center">
	              <Card isClickable onClick={() => handleApplicantClick(applicant)}>
	                <ApplicantSummary
	                  name={applicant.applicant_name || "Unknown"}
	                  summary={applicant.profile_score.headline || ""}
	                  score={applicant.profile_score.profile_score || 0}
	                  applicant_career={applicant.applicant_career || null}
	                  applicant_roles={applicant.recent_roles}
	                />
	              </Card>
	              <VerticalDisplay
	                style={{
	                  width: "auto",
	                  flex: "0 0 auto",
	                  alignItems: "center",
	                }}
	              >
	                <SmallButton
	                  onClick={() =>
	                    toggleSection(applicant.application_id, "bullets")
	                  }
	                  symbol={true}
	                  noBorder={false}
	                >
	                  ?
	                </SmallButton>
	                <SmallButton
	                  onClick={() =>
	                    toggleSection(applicant.application_id, "links")
	                  }
	                  symbol={true}
	                  noBorder={false}
	                >
	                  ↗
	                </SmallButton>
	                <SmallButton
	                  onClick={() => handleHideApplicant(applicant.application_id)}
	                  symbol={true}
	                  noBorder={false}
	                >
	                  x
	                </SmallButton>
	                <SmallButton
	                  onClick={() =>
	                    window.open(`mailto:${applicant.applicant_email}`)
	                  }
	                  symbol={true}
	                  noBorder={false}
	                >
	                  @
	                </SmallButton>
	              </VerticalDisplay>
	            </HorizontalDisplay>

	            {isBulletsOpen && (
	              <ApplicantBulletDisplay
	                strengthBullets={strengthBullets}
	                weaknessBullets={weaknessBullets}
	              />
	            )}
	            {isLinksOpen && (
	              <ul
	                style={{
	                  paddingLeft: "1rem",
	                  paddingTop: "1rem",
	                  margin: 0,
	                }}
	              >
	                <li>
	                  <button
	                    type="button"
	                    onClick={() => viewResume(applicant.application_id)}
	                    className="link-button"
	                  >
	                    Resume →
	                  </button>
	                </li>
	                {linkedin && (
	                  <li>
	                    <a
	                      href={linkedin}
	                      target="_blank"
	                      rel="noopener noreferrer"
	                    >
	                      LinkedIn →
	                    </a>
	                  </li>
	                )}
	                {portfolio && (
	                  <li>
	                    <a
	                      href={portfolio}
	                      target="_blank"
	                      rel="noopener noreferrer"
	                    >
	                      Portfolio →
	                    </a>
	                  </li>
	                )}
	                {github && (
	                  <li>
	                    <a
	                      href={github}
	                      target="_blank"
	                      rel="noopener noreferrer"
	                    >
	                      GitHub →
	                    </a>
	                  </li>
	                )}
	              </ul>
	            )}
	          </React.Fragment>
	        );
	      });

	return (
		<>
			<Header
				title={jobTitle || "Loading..."}
				crumbs={breadcrumbs}
				tabs={tabsConfig}
				onTabChange={(tabId) => setActiveTab(tabId)}
				activeTab={activeTab}
			/>
			{activeTab === "applicants" && (
				<section>
					<Loader
						loading={loadingApplicants}
						error={errorApplicants}
						errorText="Oops! Error loading applicants. Try refreshing or coming back another time."
					>
						<DisplayList emptyText="No applicants to this role yet!">
							{applicantCards}
						</DisplayList>
					</Loader>
				</section>
			)}
			{activeTab === "role" && (
				<section>
					<h2>Application Preview</h2>
					<ActionButton
						onClick={async () => {
							const key = await getPublicKey();
							if (!key) {
								console.error("Failed to get public key");
								return;
							}

							const environment = process.env.REACT_APP_ENVIRONMENT;
							const isDev = environment === "development";

							const baseUrl = isDev
							? "http://localhost:3000"
							: "https://my.hirekora.com";

							const devParam = isDev ? "&dev=1" : "";

							const previewUrl = `${baseUrl}/sdk-preview.html?jobID=${encodeURIComponent(
								jobId
							)}&key=${encodeURIComponent(key)}${devParam}`;

							console.log("baseURL: ", baseUrl)
							console.log("previewURL: ", previewUrl)

							window.open(previewUrl, "_blank");
						}}
						text="Preview"
						variant="primary"
					/>

					<h2>Job Description</h2>
					<Card isClickable={false}>
						<FileUploader
							isEditable={false}
							placeholderText={
								jobDescriptionFileName ? jobDescriptionFileName
									: (!jobDescriptionFileName && jobDescriptionFileNameError) ? jobDescriptionFileNameError
										: "We don't have a job description for you. Click below to get started!"
							}
						/>
						<HorizontalDisplay>
							<ActionButton
								onClick={handleEditJobDescriptionClick}
								text="Edit"
								variant="primary"
							/>
						</HorizontalDisplay>
					</Card>
					<h2>Form Questions</h2>
					<Card isClickable={false}>
						<ul>
							{formQuestions.length > 0 ? (
								formQuestions.map((q, idx) => (
									<li key={idx}>
										{q}
									</li>
								))
							) : (
								<li>No form questions added yet.</li>
							)}
						</ul>
						<ActionButton
							onClick={handleEditFormQuestionsClick}
							text= "Edit"
							variant="primary"
						/>
					</Card>
					<h2>Rubric</h2>
					{
						jobRubric ? (
								<Card>
									<RubricTable rubric={jobRubric} />
									<ActionButtonContainer
										centerButton={{
											onClick: () => handleEditRubricClick(),
											text: "Edit",
											variant: "primary",
											disabled: !jobDescriptionFileName
										}}
									/>
								</Card>
							)
							: rubricLoading ? (<p>Loading rubric...</p>)
								: rubricError ? (<p>{rubricError}</p>)
									: (!rubricLoading && !rubricError && !jobRubric) ? (
											<Card>
												<CardContent
													subtitle={"We don't have a rubric for this role. Click below to get started!"}
												/>
												<ActionButtonContainer
													centerButton={{
														onClick: () => handleEditRubricClick(),
														text: "Edit",
														variant: "primary",
														disabled: false
													}}
												/>
											</Card>
										)
										: ( <p>Oops! Something unexpected went wrong.</p>)
					}
				</section>
			)}
			<JobModal
				isOpen={state.isModalOpen}
				saveDescriptionTitle={setJobDescriptionFileName}
				saveRubric={setJobRubric}
				saveFormQuestions={setFormQuestions}
			/>
		</>
	);
};

export default JobApplicantsPage;