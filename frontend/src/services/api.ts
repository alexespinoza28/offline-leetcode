// API client for communicating with the backend orchestrator

import axios, { AxiosInstance } from "axios";
import { Problem, RunRequest, RunResult, SolutionResponse } from "../types";

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: "/api",
      timeout: 30000, // 30 second timeout for code execution
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Add request interceptor for logging
    this.client.interceptors.request.use(
      (config) => {
        console.log(
          `API Request: ${config.method?.toUpperCase()} ${config.url}`
        );
        return config;
      },
      (error) => {
        console.error("API Request Error:", error);
        return Promise.reject(error);
      }
    );

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => {
        console.log(`API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        console.error(
          "API Response Error:",
          error.response?.data || error.message
        );
        return Promise.reject(error);
      }
    );
  }

  async healthCheck(): Promise<{ status: string; service: string }> {
    const response = await this.client.get("/health");
    return response.data;
  }

  async getProblems(): Promise<Problem[]> {
    const response = await this.client.get("/problems");
    return response.data;
  }

  async getProblem(slug: string): Promise<Problem> {
    const response = await this.client.get(`/problems/${slug}`);
    return response.data;
  }

  async getSolution(slug: string, lang: string): Promise<SolutionResponse> {
    const response = await this.client.get(
      `/problems/${slug}/solution/${lang}`
    );
    return response.data;
  }

  async runCode(request: RunRequest): Promise<RunResult> {
    const response = await this.client.post("/run", request);
    return response.data;
  }

  // Utility method to check if API is available
  async isApiAvailable(): Promise<boolean> {
    try {
      await this.healthCheck();
      return true;
    } catch (error) {
      return false;
    }
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export class for testing
export { ApiClient };
