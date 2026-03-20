import React from "react";
import "./cardContent.css";

interface ContentCardProps {
    title?: string;
    subtitle?: string;
    content?: string;
    loading?: boolean;
}

const CardContent: React.FC<ContentCardProps> = ({ title, subtitle, content, loading = false}) => {
    return (
        <div className="card-content">
            {title && <h2>{title}</h2>}
            {subtitle && <h3>{subtitle}</h3>}
            {content && <p>{content}</p>}
            {loading && (
                <div className="loading-container">
                    <div className="spinner"></div>
                </div>
            )}
        </div>
    );
};

export default CardContent;