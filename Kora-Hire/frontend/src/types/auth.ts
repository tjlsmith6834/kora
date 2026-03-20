export interface UserAuthResponse {
	token?: string;
	message: string;
}

export interface User {
	organization_id: string
	uid: string
	email: string
}