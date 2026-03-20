import React from "react";
import Card from "../components/card/card"

interface ErrorPreUploadProps {
}

const ErrorPreUploadCard: React.FC<ErrorPreUploadProps> = ({
}) => {

    return (
	    <Card>
		    <h1>Oops...</h1>
		    <h2>Something went wrong with your submission.</h2>
		    <h3>Your application has not been submitted with us.</h3>
		    <p>We understand that this is frustrating. If you'd still like to apply with us, please come back at another time and try again. (We hope you will)!</p>
	    </Card>
    );
};

export default ErrorPreUploadCard;