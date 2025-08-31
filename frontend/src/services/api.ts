// API client for communicating with the backend orchestrator

import axios, { AxiosInstance, AxiosError } from "axios";
import { Problem, RunRequest, RunResult, SolutionResponse } from "../types";

// Custom error types
export class ApiError extends Error {
  constructor(message: string, public status?: number, public code?: string) {
    super(message);
    this.name = "ApiError";
  }
}

export class NetworkError extends Error {
  constructor(message: string = "Network connection failed") {
    super(message);
    this.name = "NetworkError";
  }
}

export class TimeoutError extends Error {
  constructor(message: string = "Request timed out") {
    super(message);
    this.name = "TimeoutError";
  }
}

// Cache interface
interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

class ApiClient {
  private client: AxiosInstance;
  private cache = new Map<string, CacheEntry<any>>();
  private readonly CACHE_TTL = 5 * 60 * 1000; // 5 minutes
  private isOnline = navigator.onLine;

  constructor() {
    this.client = axios.create({
      baseURL: "http://localhost:8001",
      timeout: 30000, // 30 second timeout for code execution
      headers: {
        "Content-Type": "application/json",
      },
    });

    this.setupInterceptors();
    this.setupNetworkListeners();
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        console.log(
          `🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`
        );
        return config;
      },
      (error) => {
        console.error("❌ API Request Error:", error);
        return Promise.reject(this.handleError(error));
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        console.log(
          `✅ API Response: ${response.status} ${response.config.url}`
        );
        return response;
      },
      (error) => {
        console.error(
          "❌ API Response Error:",
          error.response?.data || error.message
        );
        return Promise.reject(this.handleError(error));
      }
    );
  }

  private setupNetworkListeners() {
    window.addEventListener("online", () => {
      this.isOnline = true;
      console.log("🌐 Network connection restored");
    });

    window.addEventListener("offline", () => {
      this.isOnline = false;
      console.log("📡 Network connection lost");
    });
  }

  private handleError(error: any): Error {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;

      if (axiosError.code === "ECONNABORTED") {
        return new TimeoutError("Request timed out. Please try again.");
      }

      if (!axiosError.response) {
        return new NetworkError(
          "Unable to connect to server. Please check your connection."
        );
      }

      const status = axiosError.response.status;
      const message = axiosError.response.data?.message || axiosError.message;

      switch (status) {
        case 400:
          return new ApiError(
            "Invalid request. Please check your input.",
            status,
            "BAD_REQUEST"
          );
        case 401:
          return new ApiError(
            "Authentication required.",
            status,
            "UNAUTHORIZED"
          );
        case 403:
          return new ApiError("Access denied.", status, "FORBIDDEN");
        case 404:
          return new ApiError("Resource not found.", status, "NOT_FOUND");
        case 429:
          return new ApiError(
            "Too many requests. Please wait and try again.",
            status,
            "RATE_LIMITED"
          );
        case 500:
          return new ApiError(
            "Server error. Please try again later.",
            status,
            "SERVER_ERROR"
          );
        default:
          return new ApiError(
            message || "An unexpected error occurred.",
            status
          );
      }
    }

    return error instanceof Error ? error : new Error("Unknown error occurred");
  }

  private getCacheKey(method: string, url: string, params?: any): string {
    return `${method}:${url}:${JSON.stringify(params || {})}`;
  }

  private getFromCache<T>(key: string): T | null {
    const entry = this.cache.get(key);
    if (!entry) return null;

    const now = Date.now();
    if (now - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return null;
    }

    console.log(`💾 Cache hit: ${key}`);
    return entry.data;
  }

  private setCache<T>(
    key: string,
    data: T,
    ttl: number = this.CACHE_TTL
  ): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    });
  }

  private async retryRequest<T>(
    requestFn: () => Promise<T>,
    maxRetries: number = 3,
    delay: number = 1000
  ): Promise<T> {
    let lastError: Error;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await requestFn();
      } catch (error) {
        lastError = error as Error;

        // Don't retry on client errors (4xx) except 429
        if (
          error instanceof ApiError &&
          error.status &&
          error.status >= 400 &&
          error.status < 500 &&
          error.status !== 429
        ) {
          throw error;
        }

        if (attempt === maxRetries) {
          console.error(
            `❌ Request failed after ${maxRetries} attempts:`,
            lastError
          );
          throw lastError;
        }

        console.warn(
          `⚠️ Request attempt ${attempt} failed, retrying in ${delay}ms...`
        );
        await new Promise((resolve) => setTimeout(resolve, delay * attempt));
      }
    }

    throw lastError!;
  }

  async healthCheck(): Promise<{ status: string; service: string }> {
    return this.retryRequest(async () => {
      const response = await this.client.get("/health");
      return response.data;
    });
  }

  async getProblems(): Promise<Problem[]> {
    const cacheKey = this.getCacheKey("GET", "/problems");

    // Try cache first
    const cached = this.getFromCache<Problem[]>(cacheKey);
    if (cached) return cached;

    return this.retryRequest(async () => {
      const response = await this.client.get("/problems");
      const data = response.data;

      // Cache the result
      this.setCache(cacheKey, data, this.CACHE_TTL);
      return data;
    });
  }

  async getProblem(slug: string): Promise<Problem> {
    const cacheKey = this.getCacheKey("GET", `/problems/${slug}`);

    // Try cache first
    const cached = this.getFromCache<Problem>(cacheKey);
    if (cached) return cached;

    return this.retryRequest(async () => {
      const response = await this.client.get(`/problems/${slug}`);
      const data = response.data;

      // Cache the result
      this.setCache(cacheKey, data, this.CACHE_TTL);
      return data;
    });
  }

  async getSolution(slug: string, lang: string): Promise<SolutionResponse> {
    const cacheKey = this.getCacheKey(
      "GET",
      `/problems/${slug}/solution/${lang}`
    );

    // Try cache first
    const cached = this.getFromCache<SolutionResponse>(cacheKey);
    if (cached) return cached;

    return this.retryRequest(async () => {
      const response = await this.client.get(
        `/problems/${slug}/solution/${lang}`
      );
      const data = response.data;

      // Cache the result for shorter time since solutions might change
      this.setCache(cacheKey, data, 2 * 60 * 1000); // 2 minutes
      return data;
    });
  }

  async runCode(request: RunRequest): Promise<RunResult> {
    // Don't cache run requests as they should always be fresh
    return this.retryRequest(async () => {
      const response = await this.client.post("/run", request);
      return response.data;
    }, 2); // Only retry twice for code execution
  }

  // Utility methods
  async isApiAvailable(): Promise<boolean> {
    try {
      await this.healthCheck();
      return true;
    } catch (error) {
      return false;
    }
  }

  isOnlineMode(): boolean {
    return this.isOnline;
  }

  clearCache(): void {
    this.cache.clear();
    console.log("🗑️ API cache cleared");
  }

  getCacheStats(): { size: number; keys: string[] } {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys()),
    };
  }

  // Save solution locally (for offline support)
  saveSolutionLocally(slug: string, lang: string, code: string): void {
    try {
      const key = `solution_${slug}_${lang}`;
      localStorage.setItem(
        key,
        JSON.stringify({
          code,
          timestamp: Date.now(),
        })
      );
      console.log(`💾 Solution saved locally: ${key}`);
    } catch (error) {
      console.warn("Failed to save solution locally:", error);
    }
  }

  // Load solution from local storage
  loadSolutionLocally(slug: string, lang: string): string | null {
    try {
      const key = `solution_${slug}_${lang}`;
      const stored = localStorage.getItem(key);
      if (stored) {
        const { code } = JSON.parse(stored);
        console.log(`📁 Solution loaded locally: ${key}`);
        return code;
      }
    } catch (error) {
      console.warn("Failed to load solution locally:", error);
    }
    return null;
  }

  // Get all locally saved solutions
  getLocalSolutions(): Array<{
    slug: string;
    lang: string;
    code: string;
    timestamp: number;
  }> {
    const solutions: Array<{
      slug: string;
      lang: string;
      code: string;
      timestamp: number;
    }> = [];

    try {
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key?.startsWith("solution_")) {
          const parts = key.split("_");
          if (parts.length >= 3) {
            const slug = parts[1];
            const lang = parts[2];
            const stored = localStorage.getItem(key);
            if (stored) {
              const { code, timestamp } = JSON.parse(stored);
              solutions.push({ slug, lang, code, timestamp });
            }
          }
        }
      }
    } catch (error) {
      console.warn("Failed to get local solutions:", error);
    }

    return solutions.sort((a, b) => b.timestamp - a.timestamp);
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export class for testing
export { ApiClient };
