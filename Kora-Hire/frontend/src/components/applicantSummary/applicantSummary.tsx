import React from "react";
import "./applicantSummary.css";
import {ProfileCareerPath, RecentRole} from "../../types/profiles"

interface ApplicantSummaryProps {
    name?: string;
    summary?: string;
    score?: number;
    applicant_career?: ProfileCareerPath
    applicant_roles?: RecentRole[]
}

const ApplicantSummary: React.FC<ApplicantSummaryProps> = ({
    name,
    summary,
    score,
    applicant_career,
    applicant_roles
}) => {
  const sortedRoles = applicant_roles
    ? [...applicant_roles].sort((a, b) => a.recency - b.recency)
    : [];

  return (
    <div className="summary-wrapper">
          <div className="score-container">
                <h2>{score}</h2>
                <h3>Overall Score</h3>
          </div>
          <div className="applicant-details">
                {name && <h2>{name}</h2>}
                <p>{summary}</p>
              {applicant_roles && (applicant_roles.length > 0) &&(
                  <div className="recent-roles">
                      <h4>Recent Roles:</h4>
                      <ul>
                          {sortedRoles.map((role) => (
                              <li key={role.id}>
                                  <div><strong>{role.title}</strong></div>
                                  <div>{role.organization}</div>
                                  <div><em>{role.start_date} to {role.end_date}</em></div>
                              </li>
                          ))}
                      </ul>
                  </div>
              )}
          </div>
    </div>
  );
};

export default ApplicantSummary;