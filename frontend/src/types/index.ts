// Shared types used across the application

export type UserRole = 'teacher' | 'student';

export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface ApiError {
  message: string;
  statusCode: number;
  errors?: Record<string, string[]>;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
}

export interface DateRange {
  start: Date;
  end: Date;
}

// Form types
export type FormMode = 'create' | 'edit' | 'view';

// UI State types
export interface LoadingState {
  isLoading: boolean;
  error: string | null;
}

// Filter and sort types
export interface FilterState {
  search?: string;
  role?: UserRole;
  status?: 'graded' | 'pending' | 'all';
  dateRange?: DateRange;
}

export interface SortState {
  field: string;
  order: 'asc' | 'desc';
}
