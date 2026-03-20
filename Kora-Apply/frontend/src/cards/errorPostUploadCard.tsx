import React from "react";
import Card from "../components/card/card"
import {useSelector} from "react-redux";
import {RootState} from "../redux/store";

interface ErrorPostUploadCardProps {
}

const ErrorPostUploadCard: React.FC<ErrorPostUploadCardProps> = ({
}) => {

    const applicationId = useSelector((state: RootState) => state.application.applicationId);
    const email = useSelector((state: RootState) => state.application.email)

    return (
	    <Card>
		    <h1>Oops...</h1>
		    <h2>Something went wrong.</h2>
		    <h3>Don't worry, your application has still been submitted.</h3>
		    <p>At this point, you don't need to do anything else. We'll review your application as soon as possible. If there are next steps we'll reach out at {email}. Your application record is {applicationId}.</p>
	    </Card>
    );
};

export default ErrorPostUploadCard;