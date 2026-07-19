// src/api/client.js
import axios from "axios";

const client = axios.create({
  baseURL: "http://localhost:8000/api/v1",
  timeout: 30000,
});

// Attach JWT to every request automatically
client.interceptors.request.use((config) => {
  const token = localStorage.getItem("preppath_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// On 401, clear token and bounce to login
client.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("preppath_token");
      if (window.location.pathname !== "/login" && window.location.pathname !== "/register") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(err);
  }
);

export default client;