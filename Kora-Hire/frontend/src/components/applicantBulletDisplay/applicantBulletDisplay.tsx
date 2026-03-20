import React from "react";
import HorizontalDisplay from "../horizontalDisplay/horizontalDisplay";
import "./applicantBulletDisplay.css";

interface ApplicantBulletDisplayProps {
    strengthBullets: string[];
    weaknessBullets: string[];
}

const ApplicantBulletDisplay: React.FC<ApplicantBulletDisplayProps> = ({
    strengthBullets,
    weaknessBullets
}) => {
  return (
    <HorizontalDisplay
        justify={"center"}
        align={"start"}
    >
        <div className="bullet-column">
            <h3>What we like:</h3>
            <ul>
                {strengthBullets.map((bullet, index) => (
                    <li key={`strength-${index}`}>{bullet}</li>
                ))}
            </ul>
        </div>
        <div className="bullet-column">
            <h3>What to check on:</h3>
            <ul>
                {weaknessBullets.map((bullet, index) => (
                    <li key={`weakness-${index}`}>{bullet}</li>
                ))}
            </ul>
        </div>
    </HorizontalDisplay>
  );
};

export default ApplicantBulletDisplay;