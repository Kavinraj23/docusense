const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://study-snap-backend.onrender.com';

export async function login(email: string, password: string) {
  // Create form data for OAuth2 compatibility
  const formData = new URLSearchParams();
  formData.append('username', email); // Backend expects 'username' field
  formData.append('password', password);

  const response = await fetch(`${API_BASE_URL}/auth/token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Login failed');
  }
  return response.json();
}

export async function signup(email: string, password: string) {
  // Create form data for the register endpoint
  const formData = new URLSearchParams();
  formData.append('email', email);
  formData.append('password', password);

  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Signup failed');
  }
  return response.json();
} 