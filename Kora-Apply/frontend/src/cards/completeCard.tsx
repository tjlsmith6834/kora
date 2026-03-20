import React from "react";
import Card from "../components/card/card"
import {useSelector} from "react-redux";
import {RootState} from "../redux/store";

interface CompleteCardProps {
}

const CompleteCard: React.FC<CompleteCardProps> = ({
}) => {

    const applicationId = useSelector((state: RootState) => state.application.applicationId);
    const email = useSelector((state: RootState) => state.application.email)

    return (
	    <Card>
		    <h1>You're all done!</h1>
		    <h2>We're excited to get to know you!</h2>
		    <p>At this point, you don't need to do anything else. We'll review your application as soon as possible. If there are next steps we'll reach out at {email}. Your application record is {applicationId}</p>
	    </Card>
    );
};

export default CompleteCard;