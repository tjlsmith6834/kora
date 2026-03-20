export interface ProfileCategoryScore {
  category_id: string;
  category?: string;
  category_score: number;
  category_score_reason: string;
}

export interface ProfileRubric {
  category_scores: ProfileCategoryScore[];
}

export interface ApplicantProfile {
  profile_id: string;
  application_id: string;
  applicant_name?: string;
  applicant_email?: string;
  applicant_score?: number;
  applicant_score_interpretation?: string;
  category_analyses?: ProfileCategoryScore[];
}

export interface ProfileSummaryBullet{
  order: number;
  detail: string;
}

export interface ProfileSummary {
  profile_id: string;
  application_id: string;
  applicant_name: string;
  applicant_email: string;
  applicant_score: number;
  applicant_score_interpretation: string;
  strength_bullets: ProfileSummaryBullet[];
  weakness_bullets: ProfileSummaryBullet[];
}

export interface QAResponse {
  question: string;
  answer: string;
}