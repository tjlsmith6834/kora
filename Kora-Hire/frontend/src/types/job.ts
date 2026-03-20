export interface JobFrame {
    title: string;
}

export interface Job {
    job_id: string;
    title: string;
}

export interface JobList {
    jobs: [Job];
}

export interface RubricCategory {
    category_id: string;
    category: string;
    criteria: string[];
    weight: number;
    focus: string;
}

export interface Rubric {
    categories: RubricCategory[];
}

export interface FormQuestionsOut {
  job_id: string;
  questions: { id: string; question: string }[];
}