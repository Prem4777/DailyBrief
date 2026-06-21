/** Authenticated user details returned by the API. */
export interface User {
  id: string
  email: string
  created_at: string // ISO 8601 datetime string
}

/** Response from POST /auth/login and POST /auth/signup. */
export interface TokenResponse {
  access_token: string
  token_type: string
}

/** Connection status for each integrated service. */
export interface ServiceStatus {
  gmail: boolean
  gcal: boolean
  notion: boolean
}
