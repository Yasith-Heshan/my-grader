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

// Test Case types (re-exported from API for convenience)
export interface SingleCellTestCase {
  _id: string;
  assignment_id: string;
  question_number: number;
  cell_id: string;
  testcase_name: string;
  testcase_function: string;
  description?: string;
  points: number;
  timeout: number;
  language: string;
  created_at: string;
  updated_at: string;
}

export interface CellEvaluationResult {
  score: number;
  total_points: number;
  feedback: string;
  execution_time_ms: number;
  testcase_results: Array<{
    testcase_name: string;
    points: number;
    earned_points: number;
    passed: boolean;
    message: string;
  }>;
}
