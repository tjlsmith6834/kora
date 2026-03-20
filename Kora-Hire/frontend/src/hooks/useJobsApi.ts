import axios from "axios";
import { Job, JobFrame, JobList, Rubric, FormQuestionsOut } from "../types/job";

const API_BASE_URL = `${process.env.REACT_APP_BFF_BASE_URL}/jobs`;

// Job-Related API Calls
export const getJobsForOrganization = async (): Promise<Job[]> => {
	const response = await axios.get<JobList>(
		`${API_BASE_URL}/`,
		{
			headers: {
				Authorization: `Bearer ${localStorage.getItem("access_token")}`,
			},
		}
	);
	return response.data.jobs;
};

export const postJobForOrganization = async (newJob: JobFrame): Promise<Job> => {
	const response = await axios.post<Job>(
		`${API_BASE_URL}/`,
		newJob,
		{
			headers: {
				Authorization: `Bearer ${localStorage.getItem("access_token")}`,
			}
		}
	);
	return response.data
}

export const getJobDetails = async (jobId: string): Promise<Job> => {
	const response = await axios.get<Job>(
		`${API_BASE_URL}/${jobId}`,
		{
			headers: {
				Authorization: `Bearer ${localStorage.getItem("access_token")}`,
			},
		}
	);
	return response.data;
};

export const postJobRubric = async (jobId: string, newRubric: Rubric): Promise<Rubric> => {
	const response = await axios.post(
		`${API_BASE_URL}/${jobId}/rubric`,
		newRubric,
		{
			headers: {
				"Content-Type": "application/json" ,
				Authorization: `Bearer ${localStorage.getItem("access_token")}`
			}
		}
	);
	return response.data;
};

export const getJobRubric = async (jobId: string): Promise<Rubric | null> => {
	const response = await axios.get(
		`${API_BASE_URL}/${jobId}/rubric`,
		{
			headers: {
				Authorization: `Bearer ${localStorage.getItem("access_token")}`,
			},
		}
	);
	return response.data;
};

export const postJobDescription = async (jobId: string, jobDescription: File): Promise<{ file_url: string; file_name: string }> => {
	const formData = new FormData();
	formData.append("description", jobDescription)
	const response = await axios.post(
		`${API_BASE_URL}/${jobId}/description`,
		formData,
		{
			headers: {
				"Content-Type": "multipart/form-data",
				Authorization: `Bearer ${localStorage.getItem("access_token")}`,
			},
		}
	);
	return response.data
}

export const getJobDescriptionFileName = async (jobId: string): Promise<string | null> => {
	const response = await axios.get(
		`${API_BASE_URL}/${jobId}/description/file_name`,
		{
			headers: {
				"Content-Type": "multipart/form-data",
				Authorization: `Bearer ${localStorage.getItem("access_token")}`,
			},
		}
	)
	return response.data.content
}

export const postFormQuestions = async (
	jobId: string,
	questions: string[]
): Promise<string[] | null> => {
	try {
		const response = await axios.post<FormQuestionsOut>(
			`${API_BASE_URL}/${jobId}/form_questions`,
			{ questions },
			{
				headers: {
					"Content-Type": "application/json",
					Authorization: `Bearer ${localStorage.getItem("access_token")}`,
				},
			}
		);

		return response.data.questions.map((q) => q.question);

	} catch (error) {
		console.error("Failed to post form questions:", error);
		return null;
	}
};

export const getFormQuestions = async (
	jobId: string,
): Promise<string[] | null> => {
	try {
		const response = await axios.get<FormQuestionsOut>(
			`${API_BASE_URL}/${jobId}/form_questions`,
			{
				headers: {
					"Content-Type": "application/json", // use application/json unless your backend expects multipart
					Authorization: `Bearer ${localStorage.getItem("access_token")}`,
				},
			}
		);
		return response.data.questions.map((q) => q.question);
	} catch (error) {
		console.error("Failed to get form questions:", error);
		return null;
	}
};