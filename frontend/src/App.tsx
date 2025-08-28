import React, { useState, useEffect } from "react";
import styled from "styled-components";
import ProblemList from "./components/ProblemList";
import ProblemDescription from "./components/ProblemDescription";
import CodeEditor from "./components/CodeEditor";
import ControlBar from "./components/ControlBar";
import ResultsPanel from "./components/ResultsPanel";
import ConnectionStatus from "./components/ConnectionStatus";
import { Problem, RunResult } from "./types";
import {
  apiClient,
  ApiError,
  NetworkError,
  TimeoutError,
} from "./services/api";

const AppContainer = styled.div`
  display: flex;
  height: 100vh;
  background-color: #0f0f0f;
  color: #e8e8e8;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen",
    "Ubuntu", "Cantarell", sans-serif;
`;

const LeftPanel = styled.div`
  width: 420px;
  border-right: 1px solid #404040;
  display: flex;
  flex-direction: column;
  background-color: #0f0f0f;
  padding: 4px;
`;

const RightPanel = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #0f0f0f;
  padding: 4px;
`;

const EditorContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #1a1a1a;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`;

const ResultsContainer = styled.div`
  height: 320px;
  margin-top: 8px;
  background-color: #1a1a1a;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`;

function App() {
  const [problems, setProblems] = useState<Problem[]>([]);
  const [selectedProblem, setSelectedProblem] = useState<Problem | null>(null);
  const [currentLanguage, setCurrentLanguage] = useState<string>("py");
  const [code, setCode] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [results, setResults] = useState<RunResult | null>(null);

  // Load problems on mount
  useEffect(() => {
    loadProblems();
  }, []);

  // Load solution when problem or language changes
  useEffect(() => {
    if (selectedProblem) {
      loadSolution(selectedProblem.slug, currentLanguage);
    }
  }, [selectedProblem, currentLanguage]);

  const loadProblems = async () => {
    try {
      const problemList = await apiClient.getProblems();
      setProblems(problemList);
      if (problemList.length > 0 && !selectedProblem) {
        setSelectedProblem(problemList[0]);
      }
    } catch (error) {
      console.error("Failed to load problems:", error);

      // Show user-friendly error message
      if (error instanceof NetworkError) {
        console.warn("Working offline - problems may be limited");
      } else if (error instanceof ApiError) {
        console.error(`API Error: ${error.message}`);
      }
    }
  };

  const loadSolution = async (slug: string, lang: string) => {
    try {
      const solution = await apiClient.getSolution(slug, lang);
      setCode(solution.code);
    } catch (error) {
      console.error("Failed to load solution:", error);

      // Try to load from local storage first
      const localSolution = apiClient.loadSolutionLocally(slug, lang);
      if (localSolution) {
        setCode(localSolution);
        console.log("Loaded solution from local storage");
      } else {
        // Set template code if solution loading fails
        setCode(getTemplateCode(lang));
      }
    }
  };

  const getTemplateCode = (lang: string): string => {
    const templates = {
      py: `def solve(input_str: str) -> str:
    # Your solution here
    return ""

if __name__ == "__main__":
    import sys
    result = solve(sys.stdin.read())
    print(result, end="")`,
      cpp: `#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    
    // Your solution here
    
    return 0;
}`,
      c: `#include <stdio.h>
#include <stdlib.h>

int main() {
    // Your solution here
    return 0;
}`,
      js: `function solve(input) {
    // Your solution here
    return "";
}

const input = require('fs').readFileSync(0, 'utf8');
const output = solve(input);
process.stdout.write(output);`,
      java: `import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        
        // Your solution here
        
        System.out.print("");
    }
}`,
    };
    return templates[lang as keyof typeof templates] || templates.py;
  };

  const handleProblemSelect = (problem: Problem) => {
    setSelectedProblem(problem);
    setResults(null); // Clear previous results
  };

  const handleLanguageChange = (lang: string) => {
    setCurrentLanguage(lang);
    setResults(null); // Clear previous results
  };

  const handleCodeChange = (newCode: string) => {
    setCode(newCode);

    // Auto-save solution locally
    if (selectedProblem) {
      apiClient.saveSolutionLocally(
        selectedProblem.slug,
        currentLanguage,
        newCode
      );
    }
  };

  const handleRun = async () => {
    if (!selectedProblem) return;

    setIsLoading(true);
    setResults(null);

    try {
      const result = await apiClient.runCode({
        action: "run",
        problem: selectedProblem.slug,
        lang: currentLanguage,
        code: code,
        tests: "sample",
      });
      setResults(result);
    } catch (error) {
      console.error("Failed to run code:", error);

      let errorMessage = "Failed to execute code";

      if (error instanceof NetworkError) {
        errorMessage =
          "No connection to server. Code execution requires an active connection.";
      } else if (error instanceof TimeoutError) {
        errorMessage =
          "Code execution timed out. Your code may be taking too long to run.";
      } else if (error instanceof ApiError) {
        errorMessage = error.message;
      }

      setResults({
        status: "ERROR",
        summary: null,
        cases: null,
        logs: { compile: "", stderr: errorMessage },
        explanation: null,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDebug = async () => {
    // TODO: Implement debug functionality
    console.log("Debug functionality not implemented yet");
  };

  const handleExplain = async () => {
    if (!selectedProblem) return;

    try {
      const result = await apiClient.runCode({
        action: "explain",
        problem: selectedProblem.slug,
        lang: currentLanguage,
        code: code,
      });

      if (result.explanation) {
        // TODO: Show explanation in a modal or panel
        alert(result.explanation);
      }
    } catch (error) {
      console.error("Failed to get explanation:", error);

      if (error instanceof NetworkError) {
        alert(
          "Explanation feature requires an active connection to the server."
        );
      } else if (error instanceof ApiError) {
        alert(`Failed to get explanation: ${error.message}`);
      } else {
        alert("Failed to get explanation. Please try again.");
      }
    }
  };

  const handleConnectionRetry = () => {
    // Retry loading problems when connection is restored
    loadProblems();
  };

  return (
    <AppContainer>
      <ConnectionStatus onRetry={handleConnectionRetry} />

      <LeftPanel>
        <ProblemList
          problems={problems}
          selectedProblem={selectedProblem}
          onProblemSelect={handleProblemSelect}
        />
        {selectedProblem && <ProblemDescription problem={selectedProblem} />}
      </LeftPanel>

      <RightPanel>
        <EditorContainer>
          <ControlBar
            currentLanguage={currentLanguage}
            onLanguageChange={handleLanguageChange}
            onRun={handleRun}
            onDebug={handleDebug}
            onExplain={handleExplain}
            isLoading={isLoading}
          />
          <CodeEditor
            language={currentLanguage}
            value={code}
            onChange={handleCodeChange}
          />
        </EditorContainer>

        <ResultsContainer>
          <ResultsPanel results={results} isLoading={isLoading} />
        </ResultsContainer>
      </RightPanel>
    </AppContainer>
  );
}

export default App;
