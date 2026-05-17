export type UserRole = 'admin' | 'dekan' | 'teacher' | 'student';

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface Faculty {
  id: number;
  name: string;
  code: string;
  description?: string;
  created_at: string;
}

export interface Student {
  id: number;
  student_id: string;
  full_name: string;
  gender: 'M' | 'F';
  birth_date: string;
  phone?: string;
  email?: string;
  group_id: number;
  education_form: string;
  status: string;
  enrollment_year: number;
  created_at: string;
}

export interface Teacher {
  id: number;
  teacher_id: string;
  full_name: string;
  academic_degree?: string;
  position?: string;
  department?: string;
  phone?: string;
  email?: string;
  created_at: string;
}

export interface Subject {
  id: number;
  code: string;
  name: string;
  department?: string;
  credit_hours: number;
  subject_type: string;
  semester: number;
  description?: string;
}

export interface Grade {
  id: number;
  student_id: number;
  subject_id: number;
  teacher_id: number;
  assessment_type_id: number;
  grade_value: number;
  attendance_percentage: number;
  is_passed: boolean;
  semester: string;
  academic_year: string;
  grade_date: string;
}

// OLAP types
export interface OLAPDimension {
  name: string;
  label: string;
  table: string;
  attributes: string[];
  hierarchies: { name: string; levels: string[] }[];
}

export interface OLAPMeasure {
  name: string;
  label: string;
  aggregation: string;
  format: string;
}

export interface OLAPResult {
  rows: Record<string, any>[];
  row_count: number;
  sql?: string;
}
