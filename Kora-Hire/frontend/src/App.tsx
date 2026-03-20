import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Layout from "./components/layout/layout";
import JobApplicantsPage from "./pages/JobApplicantsPage";
import ApplicantDetailsPage from "./pages/ApplicantDetailsPage";
import LoginPage from "./pages/LoginPage";
import JobsPage from "./pages/JobsPage";
import { RequireAuth } from "./components/requireAuth/requireAuth";
import { Toaster } from "react-hot-toast";

// Define App component with TypeScript
const App: React.FC = () => {
	return (
		<Router>
			<Toaster
				position="top-center"
				toastOptions={{
					style: {
						background: 'var(--color-tertiary-base)',
						color: 'var(--color-tertiary-text)',
						border: 'var(--card-border)',
					},
					success: {
						style: {
							background: 'var(--color-postive-base)',
							color: 'var(--color-postive-text)',
						},
					},
					error: {
						style: {
							background: 'var(--color-negative-base)',
							color: 'var(--color-negative-text)',
						},
					},
				}}
			/>
			<Routes>
				{/* Root Route */}
				<Route path="/" element={<LoginPage />} />

				<Route element={<RequireAuth />}>
					<Route
						path="/jobs"
						element={
							<Layout>
								<JobsPage />
							</Layout>
						}
					/>

					<Route
						path="/jobs/:jobId/applicants"
						element={
							<Layout>
								<JobApplicantsPage/>
							</Layout>
						}
					/>

					<Route
						path="/jobs/:jobId/applicants/:applicationId"
						element={
							<Layout>
								<ApplicantDetailsPage />
							</Layout>}
					/>
				</Route>
			</Routes>
		</Router>
	);
};

export default App;