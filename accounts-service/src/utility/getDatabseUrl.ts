import {
  SSMClient,
  GetParameterCommand,
  GetParameterCommandInput,
  GetParameterCommandOutput,
} from "@aws-sdk/client-ssm";

export const getDatabaseUrl = async (): Promise<string> => {
  if (process.env.NODE_ENV === "development" && process.env.DATABASE_URL) {
    return process.env.DATABASE_URL;
  }

  const ssm = new SSMClient({ region: "us-east-2" });

  const input: GetParameterCommandInput = {
    Name: "/kora/accounts/prod/db_url",
    WithDecryption: true,
  };

  const command = new GetParameterCommand(input);
  const response: GetParameterCommandOutput = await ssm.send(command);

  const dbUrl = response.Parameter?.Value;

  if (!dbUrl) {
    throw new Error("DATABASE_URL not found in Parameter Store");
  }

  return dbUrl;
};