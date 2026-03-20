import { Client } from "pg";
import { ALBHandler } from "aws-lambda";
import {getDatabaseUrl} from "../utility/getDatabseUrl";

console.log("✅ getUser Lambda handler loaded");

export const handler: ALBHandler = async (event) => {
	console.log("✅ Lambda invoked with event:", event);
	try {
		console.log("Raw event:", JSON.stringify(event));
		console.log("Raw body:", event.body);

		const body = typeof event.body === "string" ? JSON.parse(event.body) : {};
		const uid: string | undefined = body.firebase_uid;

		if (!uid) {
			return formatResponse(400, { error: "Missing firebase_uid" });
		}

		const dbUrl = await getDatabaseUrl();

		const client = new Client({
			connectionString: dbUrl,
			ssl: { rejectUnauthorized: false },
		});
		await client.connect();

		const result = await client.query(
			`SELECT user_id, organization_id, role
			FROM kora_accounts.users
			WHERE firebase_uid = $1 AND closed = FALSE LIMIT 1`,
			[uid]
		);

		await client.end();

		if (result.rowCount === 0) {
			return formatResponse(404, { error: "User not found" });
	    }

		return formatResponse(200, { user: result.rows[0] });
	} catch (err: any) {
		console.error("Validation error:", err);
		return formatResponse(500, { error: err?.message || "Internal server error" });
	}
};

function formatResponse(statusCode: number, bodyObj: Record<string, any>) {
	return {
		statusCode,
		statusDescription: `${statusCode} ${statusText(statusCode)}`,
		body: JSON.stringify(bodyObj),
		isBase64Encoded: false,
	};
}

function statusText(code: number): string {
	switch (code) {
		case 200: return "OK";
		case 400: return "Bad Request";
		case 500: return "Internal Server Error";
		default: return "";
	}
}