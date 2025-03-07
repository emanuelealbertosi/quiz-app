// Configuration file for the application

// API URLs
// In the browser environment we need to use the host URL, not the Docker service name
const API_BASE_URL = 'http://localhost:9999';

// API Endpoints
const ENDPOINTS = {
  // Auth endpoints
  LOGIN: `${API_BASE_URL}/api/v1/login`,
  REGISTER: `${API_BASE_URL}/api/v1/auth/register`,
  ME: `${API_BASE_URL}/api/v1/users/me`,
  
  // Student endpoints
  QUIZZES: `${API_BASE_URL}/api/v1/quizzes`,
  QUIZ_DETAIL: (quizId) => `${API_BASE_URL}/api/v1/quizzes/${quizId}`,
  SUBMIT_QUIZ: (quizId) => `${API_BASE_URL}/api/v1/quizzes/${quizId}/submit`,
  PATHS: `${API_BASE_URL}/api/v1/paths`,
  PATH_DETAIL: (pathId) => `${API_BASE_URL}/api/v1/paths/${pathId}`,
  STUDENT_PROGRESS: `${API_BASE_URL}/api/v1/student/progress`,
  COMPLETED_QUIZZES: `${API_BASE_URL}/api/v1/quizzes/completed-quizzes/`,
  
  // Admin endpoints
  ADMIN: {
    DIFFICULTY_LEVELS: `${API_BASE_URL}/api/v1/admin/difficulty-levels`,
    PATHS: `${API_BASE_URL}/api/v1/admin/paths`,
    STATS: `${API_BASE_URL}/api/v1/admin/stats`,
    USERS: `${API_BASE_URL}/api/v1/admin/users`,
    USERS_STATS: `${API_BASE_URL}/api/v1/admin/users-stats`,
    QUIZ_CATEGORIES_STATS: `${API_BASE_URL}/api/v1/admin/quiz-categories-stats`,
    IMPORT_QUIZZES: `${API_BASE_URL}/api/v1/admin/import-quizzes`,
    USER_DETAIL: (userId) => `${API_BASE_URL}/api/v1/admin/users/${userId}`,
    TOGGLE_USER_ACTIVE: (userId) => `${API_BASE_URL}/api/v1/admin/users/${userId}/toggle-active`,
    UPDATE_STUDENT_POINTS: (userId) => `${API_BASE_URL}/api/v1/admin/users/${userId}/student-points`,
    STUDENT_QUIZZES: (userId) => `${API_BASE_URL}/api/v1/admin/users/${userId}/quizzes`,
    CHILDREN_PROGRESS: (userId) => `${API_BASE_URL}/api/v1/admin/users/${userId}/children-progress`,
    QUIZZES_MANAGEMENT: `${API_BASE_URL}/api/v1/quizzes`,
  }
};

export { API_BASE_URL, ENDPOINTS };
