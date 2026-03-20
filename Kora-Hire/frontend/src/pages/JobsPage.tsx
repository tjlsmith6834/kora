import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useJobModal } from "../context/JobModalContext";

import { Job } from "../types/job";

import { getJobsForOrganization } from "../hooks/useJobsApi";
import { getPublicKey } from "../hooks/useUserAuthApi"

import Header from "../components/header/header";
import Loader from "../components/loader/loader"
import DisplayList from "../components/displayList/displayList";
import JobCard from "../components/jobCard/jobCard";
import JobModal from "../modals/jobModal/JobModal"
import Card from "../components/card/card";
import ActionButton from "../components/actionButton/actionButton";

const JobsPage: React.FC = () => {
    const navigate = useNavigate();
    const { state, dispatch } = useJobModal();

    const [jobs, setJobs] = useState<Job[]>([]);
    const [jobsLoading, setJobsLoading] = useState<boolean>(true);
    const [keyLoading, setKeyLoading] = useState<boolean>(true)
    const [error, setError] = useState<boolean>(false);
    const [keyError, setKeyError] = useState<boolean>(false);

    const [publicKey, setPublicKey] = useState<string | null>(null)

    const [activeTab, setActiveTab] = useState("roles");

    useEffect(() => {
        const fetchJobs = async () => {
            try {
                const data: Job[] = await getJobsForOrganization();
                setJobs(data);
            } catch (err) {
                console.error("Failed to load jobs", err);
                setError(true);
            } finally {
                setJobsLoading(false);
            }
        };
        const fetchPublicKey = async () =>{
            try {
                const key: string | null = await getPublicKey();
                setPublicKey(key);
            } catch (err) {
                console.error("Failed to load public key", err);
                setKeyError(true);
            } finally {
                setKeyLoading(false);
            }
        }
        fetchJobs();
        fetchPublicKey()
    }, []);

    const handleJobClick = (id: string, title: string) => {
        navigate(`/jobs/${id}/applicants/`, {
            state: {
                jobTitle: title
            },
        })
    };

    const handleNewJobClick =  async(): Promise<void> => {
        dispatch({ type:"OPEN_MODAL", payload:"JOB_BASICS"})
    }

    const handleNewJobSave = async(newJob: Job) : Promise<void> => {
          setJobs(prevJobs => [
            ...prevJobs,
            newJob
          ]);
    }

    const jobCards = jobs?.map((job) => (
        <JobCard
            key={job.job_id}
            id={job.job_id}
            title={job.title}
            isClickable={true}
            onClick={() => handleJobClick(job.job_id, job.title)}
        />
    ));

    const tabsConfig = [
        { id: "roles", label: "Open Roles" },
        { id: "org", label: "My Organization" },
    ];

    return (
        <div
            style={{
                height: "100%",
                maxWidth: "920px",
                margin: "0 auto",
            }}
        >
            <Header
                title={"Kora"}
                tabs={tabsConfig}
                onTabChange={(tabId) => setActiveTab(tabId)}
                activeTab={activeTab}
            />
            {activeTab === "roles" && (
                <section>
                    <ActionButton
                        onClick={handleNewJobClick}
                        text="Add New Role"
                        variant="primary"
                    />
                    <Loader
                        loading={jobsLoading}
                        error={error}
                        errorText="Oops! Failed to load jobs. Try refreshing or coming back another time."
                    >
                        <DisplayList>
                            {jobCards}
                        </DisplayList>
                    </Loader>
                </section>
            )}
            {activeTab === "org" && (
                <section>
                    <div>
                        <h2>Your Public Key</h2>
                        <Loader
                            loading={keyLoading}
                            error={keyError}
                            errorText="Oops! Failed to load your public key. Try refreshing or coming back another time."
                        >
                            <Card isClickable={false}>
                                {
                                    publicKey ? (<p>{publicKey}</p>)
                                    : "No public key found"
                                }
                            </Card>
                        </Loader>
                    </div>
                </section>
            )}
            <JobModal
                isOpen={state.isModalOpen}
                saveNewJob={handleNewJobSave}
            />
        </div>
    );
};

export default JobsPage;