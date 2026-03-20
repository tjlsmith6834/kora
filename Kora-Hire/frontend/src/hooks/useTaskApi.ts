import axios, { AxiosError } from "axios";
import { Task } from "../types/task";

const API_BASE_URL = `${process.env.REACT_APP_BFF_BASE_URL}/tasks`;


export async function handlePollTask<R>(
    taskId: string,
    maxRetries = 100,
    delayMs = 3000
): Promise<Task<R>> {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            const response = await axios.get<Task>(
                `${API_BASE_URL}/${taskId}`,
                {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
                    },
                }
            );

            if (![200, 202].includes(response.status)) {
                throw new Error(`Unexpected status ${response.status}`);
            }

            const task = response.data;

            console.log(`Attempt ${attempt}: task.state = ${task.state}`);

            if (task.state === "SUCCESS") {
                return task;
            } else if (task.state === "FAILURE") {
                throw new Error("Task failed");  // terminal error
            }

        } catch (err: unknown) {
            if (axios.isAxiosError(err)) {
                const status = err.response?.status;
                const msg = err.response?.data ?? err.message;
                throw new Error(`Request failed${status ? ` (${status})` : ""}: ${msg}`);
            }
            // rethrow anything else (including our own `throw new Error("Task failed")`)
            throw err;
        }
        await new Promise((resolve) => setTimeout(resolve, delayMs));
    }
    throw new Error("Task did not complete in time");
}