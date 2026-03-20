import axios from "axios";
import { FormQuestionsOut, LinkConfig } from "../types/job";

const API_BASE_URL = `${process.env.REACT_APP_API_BASE_URL}/jobs`;

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
		console.log("Calling getFormQuestions:", `${API_BASE_URL}/${jobId}/form_questions`)
		console.log("Raw response data:", response.data);
		return response.data.questions;
	} catch (error) {
		console.error("Failed to get form questions:", error);
		return null;
	}
};

export const getLinkConfig = async (
	jobId: string
): Promise<LinkConfig | null> => {
	try {
		const response = await axios.get<LinkConfig>(
			`${API_BASE_URL}/${jobId}/link_config`,
			{
				headers: {
					"Content-Type": "application/json", // use application/json unless your backend expects multipart
					Authorization: `Bearer ${localStorage.getItem("access_token")}`,
				},
			}
		);
		console.log("Calling getLinkConfig:", `${API_BASE_URL}/${jobId}/link_config`)
		console.log("Raw response data:", response.data);
		return response.data
	} catch (error) {
		console.error("Failed to get form questions:", error);
		return null;
	}
};