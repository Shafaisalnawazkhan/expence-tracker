import axios from 'axios';

const developmentApi = `${window.location.protocol}//${window.location.hostname}:8000/api`;
const deployedApi = '/api';
const baseURL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? developmentApi : deployedApi);
const api = axios.create({ baseURL });
let refreshRequest = null;

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('finance_access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const request = error.config;
    const refreshToken = localStorage.getItem('finance_refresh_token');
    const isAuthRequest = request?.url?.includes('/auth/');
    if (error.response?.status !== 401 || request?._retried || isAuthRequest) {
      return Promise.reject(error);
    }
    if (!refreshToken) {
      localStorage.removeItem('finance_access_token');
      localStorage.removeItem('finance_user');
      window.location.assign('/');
      return Promise.reject(error);
    }
    request._retried = true;
    try {
      refreshRequest ||= axios.post(`${baseURL}/auth/refresh`, { refresh_token: refreshToken }).finally(() => { refreshRequest = null; });
      const { data } = await refreshRequest;
      localStorage.setItem('finance_access_token', data.access_token);
      localStorage.setItem('finance_refresh_token', data.refresh_token);
      request.headers.Authorization = `Bearer ${data.access_token}`;
      return api(request);
    } catch (refreshError) {
      localStorage.removeItem('finance_access_token');
      localStorage.removeItem('finance_refresh_token');
      localStorage.removeItem('finance_user');
      window.location.assign('/');
      return Promise.reject(refreshError);
    }
  }
);
export default api;
