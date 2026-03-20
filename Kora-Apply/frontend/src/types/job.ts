export interface FormQuestionsOut {
  job_id: string;
  questions: string[];
}

export interface LinkConfig {
  require_linkedin: boolean;
  require_portfolio: boolean;
  require_github: boolean;
}