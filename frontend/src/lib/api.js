const API_BASE = '/api';

function getToken() {
  return localStorage.getItem('token');
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function apiRequest(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders(),
      ...options.headers,
    },
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || `请求失败 (${res.status})`);
  }

  return res.json();
}

export async function register(email, username, password) {
  const data = await apiRequest('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, username, password }),
  });
  localStorage.setItem('token', data.access_token);
  return data;
}

export async function login(email, password) {
  const data = await apiRequest('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  localStorage.setItem('token', data.access_token);
  return data;
}

export async function getMe() {
  return apiRequest('/auth/me');
}

export async function getBalance() {
  return apiRequest('/credits/balance');
}

export async function getCreditHistory() {
  return apiRequest('/credits/history');
}

export async function getCourses() {
  return apiRequest('/courses');
}

export async function createCourse(name) {
  return apiRequest('/courses', {
    method: 'POST',
    body: JSON.stringify({ name }),
  });
}

export async function getMessages(courseId) {
  return apiRequest(`/courses/${courseId}/messages`);
}

export async function sendMessage(courseId, message, onChunk) {
  const res = await fetch(`${API_BASE}/chat/send`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders(),
    },
    body: JSON.stringify({ course_id: courseId, message }),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || `请求失败 (${res.status})`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6));
          if (data.content) onChunk(data.content);
          if (data.error) throw new Error(data.error);
        } catch (e) {
          if (!(e instanceof SyntaxError)) throw e;
        }
      }
    }
  }
}

export function logout() {
  localStorage.removeItem('token');
}
