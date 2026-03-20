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

    const dbUrl = await getDatabaseUrl();

		const client = new Client({
			connectionString: dbUrl,
			ssl: { rejectUnauthorized: false },
		});
    await client.connect();

    const result = await client.query(
      "SELECT 1 FROM kora_accounts.organizations WHERE organization_id = $1 LIMIT 1",
      [orgId]
    );

    await client.end();

    const count = result.rowCount ?? 0;
    return formatResponse(200, { valid: count > 0 });
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