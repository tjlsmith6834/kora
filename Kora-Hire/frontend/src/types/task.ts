export interface Task <R = any> {
    task_id: string;
    state: string;
    result: R | null;
}