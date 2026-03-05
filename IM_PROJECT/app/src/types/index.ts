/**
 * Type definitions for DMMMSU-SLUC Disaster Monitoring System
 */

// User Types
export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: 'admin' | 'staff';
  phone?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  user: User;
}

// Incident Types
export interface Incident {
  id: number;
  incident_id: string;
  date: string;
  time: string;
  location: string;
  cause: string;
  description: string;
  supporting_file?: string;
  pdf_file?: string;
  status: 'Pending' | 'In Progress' | 'Solved';
  reported_by: number;
  reporter_name?: string;
  created_at: string;
  updated_at: string;
}

export interface IncidentFormData {
  date: string;
  time: string;
  location: string;
  cause: string;
  description: string;
  supporting_file?: File | null;
}

export interface IncidentFilters {
  status?: string;
  location?: string;
  category?: string;
  date_from?: string;
  date_to?: string;
  search?: string;
}

// Analytics Types
export interface DashboardAnalytics {
  total_incidents: number;
  pending_count: number;
  in_progress_count: number;
  solved_count: number;
  weekly_data: WeeklyDataPoint[];
  monthly_data: MonthlyDataPoint[];
  recent_incidents: Incident[];
}

export interface WeeklyDataPoint {
  day: string;
  date: string;
  count: number;
}

export interface MonthlyDataPoint {
  month: string;
  count: number;
}

// Notification Types
export interface Notification {
  id: number;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'success' | 'error';
  created_at: string;
  read: boolean;
}

// API Response Types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  pages: number;
  current_page: number;
  per_page: number;
}

// Chart Types
export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string;
    borderWidth?: number;
  }[];
}
