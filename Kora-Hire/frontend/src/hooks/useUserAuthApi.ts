import axios from "axios";
import { createUserWithEmailAndPassword, signInWithEmailAndPassword } from "firebase/auth";
import { auth } from "../firebase";
import { UserAuthResponse } from "../types/auth";

const API_BASE_URL = `${process.env.REACT_APP_BFF_BASE_URL}/accounts`;

// Authentication API Calls

export const registerUser = async (
	email: string,
	password: string,
	organizationId: string
): Promise<UserAuthResponse> => {
	try{
		const validateRes = await axios.get<{valid: boolean}>(
			`${API_BASE_URL}/${organizationId}/validate`);

		console.log("validation complete")
		console.log(validateRes)
		console.log(validateRes.data.valid)

		if (!validateRes.data.valid) {
			console.log("fail")
			return {
				message: "Incorrect or invalid Organization ID. Please try again or contact your admin.",
		    };
		}

		const userCredential = await createUserWithEmailAndPassword(auth, email, password);
		const user = userCredential.user;
		const token = await user.getIdToken();

		const user_response = await axios.post(
	        `${API_BASE_URL}/${organizationId}/user`,
				{
					firebase_uid: user.uid

				},
				{ headers:
					{
						"Content-Type": "application/json",
						Authorization: `Bearer ${token}`
					}
				}
			);

		return {
			token: token,
			message: "User registered successfully!"
		};
	} catch (error: any) {
	  if (axios.isAxiosError(error)) {
	    const status = error.response?.status;
	    // for validate/user API failures
	    return { message: status === 422 ? "Invalid Organization ID format." : "Server error. Please try again." };
	  }

	  // firebase errors
	  return { message: friendlyAuthMessage(error?.message) };
	}
};

export const loginUser = async (
	email: string,
	password: string
): Promise<UserAuthResponse> => {
	try{
		const userCredential = await signInWithEmailAndPassword(auth, email, password);
		const user = userCredential.user;
		const token = await user.getIdToken();

		return {
			token: token,
			message: "User logged in successfully!"
		};
	}catch (error: any) {
		console.error(error.message);
		console.log(error.message);
		const firebaseMessage = error?.message || "Login failed."
		console.log(firebaseMessage)
		const errorMessage = friendlyAuthMessage(firebaseMessage)
		return {
			message: errorMessage,
	    };
	}
};

export const getPublicKey = async (
): Promise<string | null> => {
	try{
		const keyResponse = await axios.get<string>(
			`${API_BASE_URL}/public_key`,
			{
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("access_token")}`,
                },
            }
		);

		if (!keyResponse.data) {
			throw new Error("Invalid response")
		}
		console.log(`Key ${keyResponse.data}`)
		return keyResponse.data
	}catch (error: any) {
		console.error(error.message);
		return null
	}
}

//Error helpers
function extractAuthCode(input?: string): string | undefined {
  if (!input) return undefined;

  // If you pass the actual Firebase error object’s `code`, just return it.
  if (input.startsWith("auth/")) return input;

  // Matches: "Firebase: Error (auth/invalid-credential)."
  const parenMatch = input.match(/\((auth\/[^)]+)\)/);
  if (parenMatch?.[1]) return parenMatch[1];

  // Fallback: find any "auth/..." substring
  const inlineMatch = input.match(/auth\/[a-z0-9-]+/i);
  return inlineMatch?.[0];
}

export function friendlyAuthMessage(raw?: string) {
  const code = extractAuthCode(raw);

  switch (code) {
    case "auth/invalid-credential":
      return "Invalid email or password.";
    case "auth/user-disabled":
      return "This account is disabled.";
    case "auth/too-many-requests":
      return "Too many attempts. Please try again later.";
    case "auth/network-request-failed":
      return "Network error. Check your connection and try again.";
    case "auth/popup-closed-by-user":
      return "Sign-in was cancelled.";
    case "auth/popup-blocked":
      return "Your browser blocked the sign-in popup. Allow popups and try again.";
    case "auth/cancelled-popup-request":
      return "Another sign-in attempt is in progress. Please try again.";
    case "auth/unauthorized-domain":
      return "Sign-in isn’t available from this domain.";
    case "auth/account-exists-with-different-credential":
      return "An account already exists with a different sign-in method.";
    default:
      return "Couldn’t sign you in. Please try again.";
  }
}