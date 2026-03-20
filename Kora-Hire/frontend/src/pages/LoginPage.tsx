import React, { FormEvent, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import Loader from "../components/loader/loader";
import Card from "../components/card/card";
import type {UserAuthResponse} from "../types/auth";
import {loginUser, registerUser} from "../hooks/useUserAuthApi";
import {useAuth} from "../context/AuthContext";
import VerticalDisplay from "../components/verticalDisplay/verticalDisplay";
import FormField from "../components/formField/formField";
import ActionButton from "../components/actionButton/actionButton";

const LoginPage = () => {
	const auth = useAuth();
	const navigate = useNavigate();

	const formRef = useRef<HTMLFormElement>(null);

	const [loginState, setLoginState] = useState("login");

	const [loginEmail, setLoginEmail] = useState<string>("");
	const [loginPassword, setLoginPassword] = useState<string>("");

	const [signUpEmail, setSignUpEmail] = useState<string>("");
	const [signUpPassword, setSignUpPassword] = useState<string>("");
	const [signUpOrganizationId, setSignUpOrganizationId] = useState<string>("");

	const [signUpPasswordConfirm, setSignUpPasswordConfirm] = useState<string>("");

	const [pwTouched, setPwTouched] = useState(false);
	const [pwConfirmTouched, setPwConfirmTouched] = useState(false);

	const hasUpper = /[A-Z]/.test(signUpPassword);
	const hasNumber = /\d/.test(signUpPassword);
	const hasSpecial = /[^A-Za-z0-9]/.test(signUpPassword);

	const passwordMeetsRules = hasUpper && hasNumber && hasSpecial;
	const passwordsMatch = signUpPasswordConfirm.length > 0 && signUpPassword === signUpPasswordConfirm;

	const canSubmitSignup =
		signUpEmail &&
		signUpOrganizationId &&
		signUpPassword &&
		signUpPasswordConfirm &&
		passwordMeetsRules &&
		passwordsMatch;

	const [message, setMessage] = useState<string>("");

	const [loading, setLoading] = useState<boolean>(false);

	const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault();
		try {
			setLoading(true)
			const authResponse: UserAuthResponse = await loginUser(loginEmail, loginPassword);
			if (authResponse.token) {
				localStorage.setItem("access_token", authResponse.token);
				auth.login(authResponse.token);
				navigate("/jobs");
			} else {
				setMessage(authResponse.message || "Login failed.");
				return
			}
		} catch (error: any) {
			setMessage("An unexpected error occurred during login.");
			return
		} finally {
			setLoading(false)
		}
	};

	const handleRegister = async (e: FormEvent<HTMLFormElement>) => {
		e.preventDefault();

		if (!passwordMeetsRules) {
			setMessage("Password must include an uppercase letter, a number, and a special character.");
			return;
		}
		if (!passwordsMatch) {
			setMessage("Passwords do not match.");
			return;
		}

		try {
			setLoading(true)
			const response: UserAuthResponse = await registerUser(signUpEmail, signUpPassword, signUpOrganizationId);

			if (response.token) {
				// Auto-login if registration returns token
				localStorage.setItem("access_token", response.token);
				auth.login(response.token);
				navigate("/jobs");
			} else {
				setMessage(response.message || "Registration failed.");
				return
			}
		} catch (error: any) {
			const errMsg = error?.response?.data?.error || "An error occurred during registration.";
			setMessage(errMsg);
			return
		} finally {
			setLoading(false)
		}
	};

	return (
		<div className="login-page"
		     style={{
			     height: "100%",
			     maxWidth: "60ch",
			     margin: "5% auto",
		     }}
		>
			<Card isClickable={false}>

				<form
					ref={formRef}
					onSubmit={loginState === "login" ? handleLogin : handleRegister}
				>
					{loginState === "login" && (
						<VerticalDisplay>
							<div style={{textAlign: "center"}}>
								<h3 style={{margin: 0, marginTop: 8, textAlign: "center"}}>Log in to</h3>
								<h2 style={{margin: 0, textAlign: "center"}}>Kora</h2>

							</div>
							<VerticalDisplay gap="0">
								<FormField
									id="email"
									label="Email"
									required
									type="email"
									value={loginEmail}
									onChange={(e) => setLoginEmail(e.target.value)}
								/>
								<FormField
									id="password"
									label="Password"
									required
									type="password"
									value={loginPassword}
									onChange={(e) => setLoginPassword(e.target.value)}
								/>
							</VerticalDisplay>
						</VerticalDisplay>
					)}

					{loginState === "signup" && (
						<VerticalDisplay>
							<h2>Create account:</h2>
							<VerticalDisplay gap="0">
								<FormField
									id="email"
									label="Email"
									required
									type="email"
									value={signUpEmail}
									onChange={(e) => setSignUpEmail(e.target.value)}
								/>
								<FormField
									id="password"
									label="Password"
									required
									type="password"
									value={signUpPassword}
									onChange={(e) => setSignUpPassword(e.target.value)}
								/>
								<FormField
									id="signupPasswordConfirm"
									label="Confirm password"
									required
									type="password"
									value={signUpPasswordConfirm}
									onChange={(e) => {
										setSignUpPasswordConfirm(e.target.value);
										setPwConfirmTouched(true);
										setMessage("");
									}}
								/>
								{pwConfirmTouched && signUpPasswordConfirm.length > 0 && !passwordsMatch && (
									<p style={{ marginTop: 6, color: "#b00020" }}>
										Passwords don’t match.
									</p>
								)}

								<FormField
									id="organizationId"
									label="Organization ID"
									required
									type="text"
									value={signUpOrganizationId}
									onChange={(e) => setSignUpOrganizationId(e.target.value)}
								/>
							</VerticalDisplay>
						</VerticalDisplay>
					)}
					{message && <p>{message}</p>}
					{!message &&
						<div
							style={{
								height: "20px",
							}}
						></div>
					}
					<Loader loading={loading} error={false}>
						<VerticalDisplay>
							<ActionButton
								onClick={() => {
									formRef.current?.requestSubmit();
								}}
								text={loginState === "signup" ? "Sign up" : "Log in"}
								variant="primary"
							/>
							<ActionButton
								onClick={() => {
									setLoginState(loginState === "signup" ? "login" : "signup");
									setMessage("");
									setLoginPassword("");
									setLoginPassword("");
									setSignUpEmail("");
									setSignUpOrganizationId("");
									setSignUpPassword("");
								}}
								text={loginState === "signup" ? "Back to login" : "Create an account"}
								variant={loginState === "signup" ? "secondary" : "tertiary"}
							/>
						</VerticalDisplay>
					</Loader>
				</form>
			</Card>
		</div>
	);
};

export default LoginPage;