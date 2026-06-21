/**
 * authApi.ts — API functions for authentication and service connection.
 */

import type { ServiceStatus, TokenResponse } from '../types/auth'
import apiClient from './client'

/** Register a new user and return a JWT. */
export async function signup(email: string, password: string): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>('/auth/signup', { email, password })
  return data
}

/** Login with email/password and return a JWT. */
export async function login(email: string, password: string): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>('/auth/login', { email, password })
  return data
}

/** Logout — the server endpoint is stateless; this just notifies it. */
export async function logout(): Promise<void> {
  await apiClient.post('/auth/logout')
}

/** Return connection status for Gmail, GCal, and Notion. */
export async function getServiceStatus(): Promise<ServiceStatus> {
  const { data } = await apiClient.get<ServiceStatus>('/api/settings/services')
  return data
}

/**
 * Redirect the browser to the Google OAuth consent screen.
 * The backend will build the URL and return a redirect response.
 * We use window.location here because this is a full-page redirect,
 * not an API call.
 */
export function startGoogleOAuth(): void {
  // TODO: include a CSRF state token in the request if the backend requires it
  window.location.href = '/auth/google/start'
}

/** Save a Notion integration token and database ID. */
export async function saveNotionToken(
  token: string,
  databaseId: string,
): Promise<void> {
  await apiClient.post('/api/settings/notion-token', {
    access_token: token,
    database_id: databaseId,
  })
}
