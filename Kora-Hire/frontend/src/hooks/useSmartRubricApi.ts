import axios from "axios";
import type { AxiosError } from "axios";
import { Task } from "../types/task";

const API_BASE_URL = `${process.env.REACT_APP_BFF_BASE_URL}/smart_rubrics`;

export async function handlePostRequestSmartRubric(
    jobId: string
): Promise<Task> {
    try {
        const response = await axios.post<Task>(
            `${API_BASE_URL}/${jobId}`,
            {},
            {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("access_token")}`,
                }
            }

        );

        if (response.status !== 202 && response.status !== 200) {
            throw new Error(`Unexpected status ${response.status}`);
        }

        const task: Task = response.data;

        if ( !task.task_id) {
            throw new Error("Invalid Task payload or missing task_id");
        }

        return task;

    } catch (err: unknown) {
        if (axios.isAxiosError(err)) {
            const axiosErr = err as AxiosError;
            const status = axiosErr.response?.status;
            const msg = axiosErr.response?.data ?? axiosErr.message;
            throw new Error(`Request failed${status ? ` (${status})` : ""}: ${msg}`);
        }
        // rethrow other errors
        throw err instanceof Error
        ? err
        : new Error(String(err));
    }
}