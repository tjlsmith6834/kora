import { Client } from "pg";
import { Handler } from "aws-lambda";
import {getDatabaseUrl} from "../utility/getDatabseUrl";

export const handler: Handler = async (event) => {
  try {
    console.log("Raw event:", JSON.stringify(event));

    const parsedEvent = typeof event === "string" ? JSON.parse(event) : event;

    console.log(`parsedEvent: "${parsedEvent}`)
    const orgId: string | undefined = parsedEvent.organization_id;
	const publicKey: string | undefined = parsedEvent.public_key;

    console.log(`orgId: "${orgId}"`);
    console.log(`publicKey: "${publicKey}"`);

    if (!orgId || !publicKey) {
      return formatResponse(400, { error: "Missing organization_id or public_key" });
    }

    const dbUrl = await getDatabaseUrl();

		const client = new Client({
			connectionString: dbUrl,
			ssl: { rejectUnauthorized: false },
		});
    await client.connect();

    const result = await client.query(
      "SELECT 1 FROM kora_accounts.public_keys WHERE organization_id=$1 AND key = $2 LIMIT 1",
      [orgId.trim(), publicKey.trim()]
    );

    await client.end();

    console.log("DB result:", result.rows);

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