export type AgentState = 'unknown' | 'idle' | 'working' | 'done' | 'needs_input' | 'errored'
export type AttentionKind = 'finished' | 'question' | 'errored' | 'approval'
export type Role = 'viewer' | 'operator' | 'admin'

export interface Session {
  id: number
  name: string
  space: string
  created_at: string
  updated_at: string
  window_count: number
}

export interface SessionListResponse {
  items: Session[]
  total: number
  page: number
  page_size: number
}

export interface SessionCreate {
  name: string
  space?: string
}

export interface SessionUpdate {
  name?: string
  space?: string
}

export interface Window {
  id: number
  session_id: number
  workspace: number
  index: number
  title: string | null
  command: string | null
  cwd: string | null
  agent_state: AgentState
  completion_seq: number
  quiet: boolean
  created_at: string
  updated_at: string
}

export interface WindowListResponse {
  items: Window[]
  total: number
  page: number
  page_size: number
}

export interface WindowCreate {
  session_id: number
  workspace?: number
  index?: number
  title?: string
  command?: string
  cwd?: string
}

export interface WindowUpdate {
  title?: string
  command?: string
  cwd?: string
  agent_state?: AgentState
  quiet?: boolean
}

export interface AttentionItem {
  id: number
  window_id: number
  window_title: string | null
  session_name: string
  kind: AttentionKind
  title: string
  message: string | null
  human_nonce: string | null
  dismissed_at: string | null
  created_at: string
}

export interface AttentionListResponse {
  items: AttentionItem[]
  total: number
  page: number
  page_size: number
}

export interface DismissRequest {
  human_nonce: string
}

export interface AttentionSummary {
  total: number
  by_kind: Record<AttentionKind, number>
}

export interface User {
  id: number
  email: string
  username: string | null
  full_name: string | null
  role: Role
  is_active: boolean
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
}

export interface LoginRequest {
  email: string
  password: string
}

export interface HealthResponse {
  status: string
  version: string
  environment: string
}
