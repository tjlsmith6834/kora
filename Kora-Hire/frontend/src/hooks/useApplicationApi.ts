import axios from "axios";

import { ProfileSummary, ProfileRubric, QAResponse } from "../types/applicantProfile";
import { Profile} from "../types/profiles";

const API_BASE_URL = `${process.env.REACT_APP_BFF_BASE_URL}/applications`;

export const getApplicantsForJob = async (jobId: string): Promise<Profile[]> => {
	const response = await axios.get<Profile[]>(
		`${API_BASE_URL}/profiles/?job_id=${jobId}`,
		{
			headers: {
				Authorization: `Bearer ${localStorage.getItem("access_token")}`,
			},
		}
	);
	return response.data;
};

export const getApplicationById = async (applicationId: string): Promise<Profile> => {
	const response = await axios.get<Profile>(
		`${API_BASE_URL}/${applicationId}/profile/`,
		{
			headers: {
				Authorization: `Bearer ${localStorage.getItem("access_token")}`,
			},
		}
	);
	return response.data;
};

export async function putHideApplication(applicationId: string): Promise<void> {
	const response = await axios.put(
		`${API_BASE_URL}/${applicationId}/hide/`,
		{
			headers: {
				Authorization: `Bearer ${localStorage.getItem("access_token")}`,
			},
		}
	);
	return
}

export const getApplicationFormQuestionAnswers = async (applicationId: string): Promise<QAResponse[]> => {
	const response = await axios.get<QAResponse[]>(
		`${API_BASE_URL}/${applicationId}/form_question_answers`,
		{
			headers: {
				Authorization: `Bearer ${localStorage.getItem("access_token")}`,
			},
		}
	);

	return response.data;
};

export const getApplicationRubric = async (applicationId: string): Promise<ProfileRubric> => {
	const response = await axios.get<ProfileRubric>(
		`${API_BASE_URL}/${applicationId}/rubric`,
		{
			headers: {
				Authorization: `Bearer ${localStorage.getItem("access_token")}`,
			},
		}
	);

	return response.data;
};

export const getApplicationInterviewQuestionAnswers = async (applicationId: string): Promise<QAResponse[]> => {
	const response = await axios.get<QAResponse[]>(
		`${API_BASE_URL}/${applicationId}/interview_question_answers`,
		{
			headers: {
				Authorization: `Bearer ${localStorage.getItem("access_token")}`,
			},
		}
	);

	return response.data;
};

export const postApplicationInterviewQuestionAnswer = async (
	applicationId: string,
	qa: QAResponse
	): Promise<{ message: string; qa_id: string }> => {
	const response = await axios.post(
		`${API_BASE_URL}/${applicationId}/interview_question_answers`,
		qa,
			{
			headers: {
				Authorization: `Bearer ${localStorage.getItem("access_token")}`,
			},
		}
	);
	return response.data;
};



