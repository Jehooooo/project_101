/**
 * API Service for DMMMSU-SLUC Disaster Monitoring System
 */

import type { 
  User, 
  Incident, 
  IncidentFilters,
  DashboardAnalytics,
  Notification
} from '@/types';

const API_URL = 'http://localhost:5000/api';

// Helper function to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token');
  return {
    'Authorization': `Bearer ${token}`
  };
};

// Helper function to handle API responses
const handleResponse = async (response: Response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new Error(error.error || `HTTP error! status: ${response.status}`);
  }
  return response.json();
};

// ==================== AUTH API ====================

export const authApi = {
  login: async (email: string, password: string) => {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    return handleResponse(response);
  },

  getCurrentUser: async () => {
    const response = await fetch(`${API_URL}/auth/me`, {
      headers: getAuthHeaders()
    });
    return handleResponse(response);
  }
};

// ==================== USERS API ====================

export const usersApi = {
  getAll: async (): Promise<{ users: User[] }> => {
    const response = await fetch(`${API_URL}/users`, {
      headers: getAuthHeaders()
    });
    return handleResponse(response);
  },

  create: async (userData: Partial<User>) => {
    const response = await fetch(`${API_URL}/users`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      body: JSON.stringify(userData)
    });
    return handleResponse(response);
  },

  update: async (id: number, userData: Partial<User>) => {
    const response = await fetch(`${API_URL}/users/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      body: JSON.stringify(userData)
    });
    return handleResponse(response);
  },

  delete: async (id: number) => {
    const response = await fetch(`${API_URL}/users/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    return handleResponse(response);
  }
};

// ==================== INCIDENTS API ====================

export const incidentsApi = {
  getAll: async (filters?: IncidentFilters & { page?: number; per_page?: number }): Promise<{
    incidents: Incident[];
    total: number;
    pages: number;
    current_page: number;
    per_page: number;
  }> => {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== '') {
          params.append(key, String(value));
        }
      });
    }
    const response = await fetch(`${API_URL}/incidents?${params}`, {
      headers: getAuthHeaders()
    });
    return handleResponse(response);
  },

  getById: async (id: number): Promise<{ incident: Incident }> => {
    const response = await fetch(`${API_URL}/incidents/${id}`, {
      headers: getAuthHeaders()
    });
    return handleResponse(response);
  },

  create: async (formData: FormData) => {
    const response = await fetch(`${API_URL}/incidents`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: formData
    });
    return handleResponse(response);
  },

  updateStatus: async (id: number, status: string) => {
    const response = await fetch(`${API_URL}/incidents/${id}/status`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      body: JSON.stringify({ status })
    });
    return handleResponse(response);
  },

  downloadPdf: async (id: number) => {
    const response = await fetch(`${API_URL}/incidents/${id}/pdf`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      throw new Error('Failed to download PDF');
    }
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `incident_${id}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }
};

// ==================== ANALYTICS API ====================

export const analyticsApi = {
  getDashboard: async (): Promise<DashboardAnalytics> => {
    const response = await fetch(`${API_URL}/analytics/dashboard`, {
      headers: getAuthHeaders()
    });
    const data = await handleResponse(response);
    return data;
  },

  generateFullReport: async (filters?: { date_from?: string; date_to?: string; status?: string }) => {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== '') {
          params.append(key, String(value));
        }
      });
    }
    const response = await fetch(`${API_URL}/reports/full?${params}`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      throw new Error('Failed to generate report');
    }
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `full_report_${new Date().toISOString().split('T')[0]}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }
};

// ==================== NOTIFICATIONS API ====================

export const notificationsApi = {
  getAll: async (): Promise<{ notifications: Notification[] }> => {
    const response = await fetch(`${API_URL}/notifications`, {
      headers: getAuthHeaders()
    });
    return handleResponse(response);
  }
};
