import React, { useState } from "react";
import Card from "../components/card/card"
import Spinner from "../components/spinner/spinner";

interface BuildingSurveyCardProps {
}

const BuildingSurveyCard: React.FC<BuildingSurveyCardProps> = ({
}) => {

    const [firstName, setFirstName] = useState('');

    return (
	    <Card>
		    <h1>Thanks for sticking with us!</h1>
		    <h2>Analyzing your application...</h2>
		    <p>Give us a moment while we come up with some questions to get to know you better. This can take a minute or two.
			</p>
		    <Spinner/>
	    </Card>
    );
};

export default BuildingSurveyCard;