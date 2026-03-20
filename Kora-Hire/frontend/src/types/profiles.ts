// ProfileSummaryBullet.ts
export interface ProfileSummaryBullet {
  order: number;
  detail: string;
}

// ProfileBullets.ts
export interface ProfileBullets {
  liked_bullets: ProfileSummaryBullet[];
  disliked_bullets: ProfileSummaryBullet[];
}

// ProfileOverallScore.ts
export interface ProfileOverallScore {
  profile_score: number;
  headline: string;
}

// ProfileCategoryScore.ts
export interface ProfileCategoryScore {
  category_id: string; // UUID as string
  category?: string;
  category_score: number;
  category_score_reason: string;
}

// ProfileRubric.ts
export interface ProfileRubric {
  category_scores: ProfileCategoryScore[];
}

// RoleSummary.ts
export interface RoleSummary {
  title: string;
  company: string;
  tenure: number;
}

// ProfileCareerPath.ts
export interface ProfileCareerPath {
  years_of_experience: number;
  most_recent_role: RoleSummary;
  longest_tenured_role: RoleSummary;
  average_tenure: number;
  number_promotions: number;
}

// RecentRole.ts
export interface RecentRole {
  id: string;
  application_id: string;
  title: string;
  organization: string;
  recency: number;
  start_date: string;     // e.g. "January 2024"
  end_date: string;       // e.g. "Current" or "November 2023"
}

// Profile.ts
export interface Profile {
  profile_id: string; // UUID
  application_id: string; // UUID
  applicant_name: string;
  applicant_email: string;
  linkedin_url?: string;
  portfolio_url?: string;
  github_url?: string;
  applicant_career: ProfileCareerPath;
  profile_score: ProfileOverallScore;
  profile_bullets: ProfileBullets;
  profile_rubric: ProfileRubric;
  recent_roles?: RecentRole[];
}