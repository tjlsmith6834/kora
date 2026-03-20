import { Client } from "pg";
import { ALBHandler } from "aws-lambda";
import {getDatabaseUrl} from "../utility/getDatabseUrl";

export const handler: ALBHandler = async (event) => {
	try {
	    console.log("Raw event:", JSON.stringify(event));
	    console.log("Raw body:", event.body);

	    const body = typeof event.body === "string" ? JSON.parse(event.body) : {};
	    const orgId: string | undefined = body.organization_id;

	    if (!orgId) {
			return formatResponse(400, { error: "Missing organization_id" });
	    }

		console.log(`orgId: "${orgId}"`);

		const dbUrl = await getDatabaseUrl();

		const client = new Client({
			connectionString: dbUrl,
			ssl: { rejectUnauthorized: false },
		});
		await client.connect();

	    const result = await client.query(
			`SELECT key FROM kora_accounts.public_keys
			WHERE organization_id=$1 AND revoked=FALSE 
			LIMIT 1`,
			[orgId.trim()]
	    );
		console.log("Query result:", result.rows);
		await client.end()

		if (result.rowCount === 0) {
			return formatResponse(404, { error: "Public key not found" });
		}

		return formatResponse(200, { public_key: result.rows[0].key });
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