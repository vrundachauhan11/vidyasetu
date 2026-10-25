import {
  DashboardData,
  Institution,
  StudentRecord,
  IntakeBatch,
  IntegritySignalItem,
  RuleDefinition,
  AuditLogItem,
  UserProfile,
  LoginResponse,
  DemoRoleInfo,
} from '../types';

const API_BASE = '/api';
const TOKEN_STORAGE_KEY = 'vidyasetu_auth_token';

export function getStoredToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function setStoredToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(TOKEN_STORAGE_KEY, token);
  }
}

export function clearStoredToken(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
  }
}

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const token = getStoredToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options?.headers as Record<string, string>),
  };

  const res = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let msg = `HTTP error ${res.status}`;
    try {
      const errObj = await res.json();
      if (errObj.detail) msg = errObj.detail;
      else if (errObj.error?.message) msg = errObj.error.message;
    } catch {
      // ignore
    }
    throw new Error(msg);
  }

  return res.json();
}

export const api = {
  // Auth Token Utilities
  getToken: getStoredToken,
  setToken: setStoredToken,
  clearToken: clearStoredToken,

  // System Health & Version
  async getHealth() {
    return fetchJSON<{ status: string; database: { connected: boolean; dialect: string }; version: string }>('/health');
  },

  async getVersion() {
    return fetchJSON<{ service: string; version: string; product_positioning: string }>('/version');
  },

  // Auth & RBAC
  async login(payload: { email?: string; password?: string; role?: string }): Promise<LoginResponse> {
    const data = await fetchJSON<LoginResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    if (data.token) {
      setStoredToken(data.token);
    }
    return data;
  },

  async logout(): Promise<void> {
    try {
      await fetchJSON('/auth/logout', { method: 'POST' });
    } catch (err) {
      console.warn('Logout endpoint call failed:', err);
    } finally {
      clearStoredToken();
    }
  },

  async getCurrentUser(): Promise<UserProfile> {
    return fetchJSON<UserProfile>('/auth/me');
  },

  async getRoles(): Promise<DemoRoleInfo[]> {
    return fetchJSON<DemoRoleInfo[]>('/auth/roles');
  },

  async switchRole(role: string): Promise<UserProfile> {
    const res = await fetchJSON<{ success: boolean; token: string; user: UserProfile }>('/auth/switch-role', {
      method: 'POST',
      body: JSON.stringify({ role }),
    });
    if (res.token) {
      setStoredToken(res.token);
    }
    return res.user;
  },

  // Dashboard Overview
  async getDashboardOverview(): Promise<DashboardData> {
    return fetchJSON<DashboardData>('/dashboard/overview');
  },

  // Institutions
  async getInstitutions(): Promise<{ data: Institution[] }> {
    return fetchJSON<{ data: Institution[] }>('/institutions');
  },

  // Students
  async getStudents(params?: { apaar_status?: string; integrity_status?: string; search?: string }): Promise<{ data: StudentRecord[] }> {
    const query = new URLSearchParams();
    if (params?.apaar_status) query.set('apaar_status', params.apaar_status);
    if (params?.integrity_status) query.set('integrity_status', params.integrity_status);
    if (params?.search) query.set('search', params.search);
    const qs = query.toString() ? `?${query.toString()}` : '';
    return fetchJSON<{ data: StudentRecord[] }>(`/students${qs}`);
  },

  // Data Intake
  async getBatches(): Promise<{ data: IntakeBatch[] }> {
    return fetchJSON<{ data: IntakeBatch[] }>('/intake/batches');
  },

  async getSampleCSV(): Promise<string> {
    const res = await fetch(`${API_BASE}/intake/sample-csv`);
    return res.text();
  },

  async uploadCSV(file: File): Promise<any> {
    const token = getStoredToken();
    const formData = new FormData();
    formData.append('file', file);

    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const res = await fetch(`${API_BASE}/intake/upload`, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!res.ok) {
      let errorMsg = `Upload failed (HTTP ${res.status})`;
      try {
        const err = await res.json();
        if (typeof err.detail === 'string') {
          errorMsg = err.detail;
        } else if (Array.isArray(err.detail)) {
          errorMsg = err.detail.map((d: any) => d.msg || JSON.stringify(d)).join('; ');
        } else if (err.error?.message) {
          errorMsg = err.error.message;
        } else if (err.message) {
          errorMsg = err.message;
        }
      } catch {
        // use fallback errorMsg
      }
      throw new Error(errorMsg);
    }
    return res.json();
  },

  // APAAR Validation
  async getApaarStatus(): Promise<any> {
    return fetchJSON('/apaar/status');
  },

  async getApaarRecords(): Promise<{ data: any[] }> {
    return fetchJSON<{ data: any[] }>('/apaar/records');
  },

  async lookupApaar(apaar_id: string, student_name: string): Promise<any> {
    return fetchJSON('/apaar/lookup', {
      method: 'POST',
      body: JSON.stringify({ apaar_id, student_name }),
    });
  },

  // Rules & Signals
  async getRules(): Promise<{ data: RuleDefinition[] }> {
    return fetchJSON<{ data: RuleDefinition[] }>('/rules');
  },

  async getSignals(): Promise<{ data: IntegritySignalItem[] }> {
    return fetchJSON<{ data: IntegritySignalItem[] }>('/rules/signals');
  },

  // Review Queue
  async getReviewQueue(): Promise<{ data: IntegritySignalItem[] }> {
    return fetchJSON<{ data: IntegritySignalItem[] }>('/review/queue');
  },

  async submitReviewDecision(signalId: string, decision: string, notes: string): Promise<any> {
    return fetchJSON(`/review/${signalId}/decision`, {
      method: 'POST',
      body: JSON.stringify({
        decision,
        reviewer_notes: notes,
      }),
    });
  },

  // Credentials Verification
  async verifyCredential(queryKey: string): Promise<any> {
    return fetchJSON(`/credentials/verify/${encodeURIComponent(queryKey)}`);
  },

  // Reports
  async getReportsSummary(): Promise<any> {
    return fetchJSON('/reports/summary');
  },

  // Audit Logs
  async getAuditLogs(): Promise<{ data: AuditLogItem[] }> {
    return fetchJSON<{ data: AuditLogItem[] }>('/audit/logs');
  },

  // Consent Policies
  async getConsentPolicies(): Promise<any> {
    return fetchJSON('/consent/policies');
  },
};
