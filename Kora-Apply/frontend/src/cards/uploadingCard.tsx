import React, { useState } from "react";
import Card from "../components/card/card"
import Spinner from "../components/spinner/spinner";

interface UploadingCardProps {
}

const UploadingCard: React.FC<UploadingCardProps> = ({
}) => {

    const [firstName, setFirstName] = useState('');

    return (
	    <Card>
		    <h1>Uploading application...</h1>
		    <h2>We're excited you chose to apply with us!</h2>
		    <p>Give us a moment while we save your application.</p>
		    <Spinner/>
	    </Card>
    );
};

export default UploadingCard;