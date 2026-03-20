import { Client } from "pg";
import { ALBHandler } from "aws-lambda";
import { v4 as uuidv4 } from "uuid";

import {getDatabaseUrl} from "../utility/getDatabseUrl";

export const handler: ALBHandler = async (event) => {
	try {
		console.log("Raw event:", JSON.stringify(event));

		const body = JSON.parse(event.body || "{}");
		const { organization_id, firebase_uid } = body;

		if (!organization_id || !firebase_uid) {
			return {
				statusCode: 400,
				statusDescription: "400 Bad Request",
				body: JSON.stringify({ error: "Missing organization_id or firebase_uid" }),
				isBase64Encoded: false,
			};
		}

		const dbUrl = await getDatabaseUrl();

		const client = new Client({
			connectionString: dbUrl,
			ssl: { rejectUnauthorized: false },
		});

		await client.connect();

		const userId = uuidv4();

		await client.query(
			`INSERT INTO kora_accounts.users (user_id, organization_id, firebase_uid, created_at, role, closed)
             VALUES ($1, $2, $3, NOW(), 'user', false)`,
			[userId, organization_id, firebase_uid]
		);

		await client.end();

		return {
			statusCode: 201,
			statusDescription: "201 Created",
			body: JSON.stringify({ message: "User created", user_id: userId }),
			isBase64Encoded: false,
		};
	} catch (err: any) {
		console.error("User creation error:", err);
		return {
			statusCode: 500,
			statusDescription: "500 Internal Server Error",
			body: JSON.stringify({ error: err.message || "Internal server error" }),
			isBase64Encoded: false,
		};
	}
};