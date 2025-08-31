import React, { useState, useEffect } from "react";
import styled from "styled-components";
import ProblemList from "./components/ProblemList";
import ProblemDescription from "./components/ProblemDescription";
import CodeEditor from "./components/CodeEditor";
import ControlBar from "./components/ControlBar";
import ResultsPanel from "./components/ResultsPanel";
import ConnectionStatus from "./components/ConnectionStatus";
import {
  Problem,
  RunResult,
  ConnectionStatus as ConnectionStatusType,
} from "./types";
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
`;

const RightPanel = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #0f0f0f;
`;

const VerticalResizer = styled.div`
  width: 6px;
  cursor: col-resize;
  background-color: #1a1a1a;
  border-left: 1px solid #202020;
  border-right: 1px solid #202020;
  &:hover {
    background-color: #222;
  }
`;

const EditorSection = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
`;

const EditorContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #1a1a1a;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin: 4px;
  gap: 8px; /* add breathing room between control bar and editor */
  min-height: 0; /* allow children to size correctly in flex */
`;

const ResultsContainer = styled.div`
  height: 320px;
  margin-top: 8px;
  background-color: #1a1a1a;
  border-radius: 12px;
  overflow: auto;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin: 8px 4px 4px 4px;
  min-height: 120px;
  max-height: 80vh;
`;

const HorizontalResizer = styled.div`
  height: 6px;
  cursor: row-resize;
  margin: 0 4px;
  background-color: #1a1a1a;
  border-top: 1px solid #202020;
  border-bottom: 1px solid #202020;
  border-radius: 6px;
  &:hover {
    background-color: #222;
  }
`;

function App() {
  console.log("App component rendering...");

  // Default problems to show immediately
  const defaultProblems: Problem[] = [
    {
      slug: "two-sum",
      title: "Two Sum",
      difficulty: "Easy",
      tags: ["Array", "Hash Table"],
      statement_md: `Given an array of integers \`nums\` and an integer \`target\`, return indices of the two numbers such that they add up to \`target\`.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order.`,
      examples: [
        {
          in: "nums = [2,7,11,15], target = 9",
          out: "[0,1]",
        },
        {
          in: "nums = [3,2,4], target = 6",
          out: "[1,2]",
        },
      ],
      constraints: [
        {
          name: "Array length",
          min: 2,
          max: 10000,
          desc: "2 ≤ nums.length ≤ 10^4",
        },
      ],
    },
    {
      slug: "add-two-numbers",
      title: "Add Two Numbers",
      difficulty: "Medium",
      tags: ["Linked List", "Math", "Recursion"],
      statement_md: `You are given two non-empty linked lists representing two non-negative integers. The digits are stored in reverse order, and each of their nodes contains a single digit. Add the two numbers and return the sum as a linked list.

You may assume the two numbers do not contain any leading zero, except the number 0 itself.`,
      examples: [
        {
          in: "l1 = [2,4,3], l2 = [5,6,4]",
          out: "[7,0,8]",
        },
      ],
      constraints: [
        {
          name: "List length",
          min: 1,
          max: 100,
          desc: "The number of nodes in each linked list is in the range [1, 100]",
        },
      ],
    },
    {
      slug: "longest-substring",
      title: "Longest Substring Without Repeating Characters",
      difficulty: "Medium",
      tags: ["Hash Table", "String", "Sliding Window"],
      statement_md: `Given a string \`s\`, find the length of the longest substring without repeating characters.`,
      examples: [
        {
          in: 's = "abcabcbb"',
          out: "3",
        },
        {
          in: 's = "bbbbb"',
          out: "1",
        },
      ],
      constraints: [
        {
          name: "String length",
          min: 0,
          max: 50000,
          desc: "0 ≤ s.length ≤ 5 * 10^4",
        },
      ],
    },
    {
      slug: "valid-parentheses",
      title: "Valid Parentheses",
      difficulty: "Easy",
      tags: ["String", "Stack"],
      statement_md: `Given a string \`s\` containing just the characters \`'('\`, \`')'\`, \`'{'\`, \`'}'\`, \`'['\` and \`']'\`, determine if the input string is valid.

An input string is valid if:
1. Open brackets must be closed by the same type of brackets.
2. Open brackets must be closed in the correct order.`,
      examples: [
        {
          in: 's = "()"',
          out: "true",
        },
        {
          in: 's = "()[]{}"',
          out: "true",
        },
        {
          in: 's = "(]"',
          out: "false",
        },
      ],
      constraints: [
        {
          name: "String length",
          min: 1,
          max: 10000,
          desc: "1 ≤ s.length ≤ 10^4",
        },
      ],
    },
    {
      slug: "median-sorted-arrays",
      title: "Median of Two Sorted Arrays",
      difficulty: "Hard",
      tags: ["Array", "Binary Search", "Divide and Conquer"],
      statement_md: `Given two sorted arrays \`nums1\` and \`nums2\` of size \`m\` and \`n\` respectively, return the median of the two sorted arrays.

The overall run time complexity should be O(log (m+n)).`,
      examples: [
        {
          in: "nums1 = [1,3], nums2 = [2]",
          out: "2.00000",
        },
        {
          in: "nums1 = [1,2], nums2 = [3,4]",
          out: "2.50000",
        },
      ],
      constraints: [
        {
          name: "Array constraints",
          min: 0,
          max: 1000,
          desc: "nums1.length == m, nums2.length == n, 0 ≤ m ≤ 1000, 0 ≤ n ≤ 1000",
        },
      ],
    },
  ];

  const [problems, setProblems] = useState<Problem[]>(defaultProblems);
  const [selectedProblem, setSelectedProblem] = useState<Problem | null>(
    defaultProblems[0]
  );
  const [currentLanguage, setCurrentLanguage] = useState<string>("py");
  const [code, setCode] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [results, setResults] = useState<RunResult | null>(null);
  const [progress, setProgress] = useState<number>(0);
  const [showKeyboardShortcuts, setShowKeyboardShortcuts] =
    useState<boolean>(false);
  const [testMode, setTestMode] = useState<"sample" | "unit" | "all">("sample");
  const [showResults, setShowResults] = useState<boolean>(true);
  const [resultsHeight, setResultsHeight] = useState<number>(320);
  const [leftWidth, setLeftWidth] = useState<number>(420);
  const [dragging, setDragging] = useState<null | "vertical" | "horizontal">(null);
  const [connectionStatus, setConnectionStatus] =
    useState<ConnectionStatusType>({
      connected: false,
      latency: null,
      error: null,
      lastPing: null,
    });

  // Load problems on mount
  useEffect(() => {
    checkConnection();
    loadProblems();
  }, []);

  // Load solution when problem or language changes
  useEffect(() => {
    if (selectedProblem) {
      loadSolution(selectedProblem.slug, currentLanguage);
    }
  }, [selectedProblem, currentLanguage]);

  const checkConnection = async () => {
    try {
      const startTime = Date.now();
      await apiClient.healthCheck();
      const endTime = Date.now();
      setConnectionStatus({
        connected: true,
        latency: endTime - startTime,
        error: null,
        lastPing: new Date(),
      });
    } catch (error) {
      setConnectionStatus({
        connected: false,
        latency: null,
        error: "Failed to connect to the server.",
        lastPing: new Date(),
      });
    }
  };

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
        console.warn("Working offline - using default problems");
      } else if (error instanceof ApiError) {
        console.error(`API Error: ${error.message}`);
      }

      // Load default problems when API fails
      const defaultProblems: Problem[] = [
        {
          slug: "two-sum",
          title: "Two Sum",
          difficulty: "Easy",
          tags: ["Array", "Hash Table"],
          statement_md: `Given an array of integers \`nums\` and an integer \`target\`, return indices of the two numbers such that they add up to \`target\`.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order.`,
          examples: [
            {
              in: "nums = [2,7,11,15], target = 9",
              out: "[0,1]",
            },
            {
              in: "nums = [3,2,4], target = 6",
              out: "[1,2]",
            },
          ],
          constraints: [
            {
              name: "Array length",
              min: 2,
              max: 10000,
              desc: "2 ≤ nums.length ≤ 10^4",
            },
          ],
        },
        {
          slug: "add-two-numbers",
          title: "Add Two Numbers",
          difficulty: "Medium",
          tags: ["Linked List", "Math", "Recursion"],
          statement_md: `You are given two non-empty linked lists representing two non-negative integers. The digits are stored in reverse order, and each of their nodes contains a single digit. Add the two numbers and return the sum as a linked list.

You may assume the two numbers do not contain any leading zero, except the number 0 itself.`,
          examples: [
            {
              in: "l1 = [2,4,3], l2 = [5,6,4]",
              out: "[7,0,8]",
            },
          ],
          constraints: [
            {
              name: "List length",
              min: 1,
              max: 100,
              desc: "The number of nodes in each linked list is in the range [1, 100]",
            },
          ],
        },
        {
          slug: "longest-substring",
          title: "Longest Substring Without Repeating Characters",
          difficulty: "Medium",
          tags: ["Hash Table", "String", "Sliding Window"],
          statement_md: `Given a string \`s\`, find the length of the longest substring without repeating characters.`,
          examples: [
            {
              in: 's = "abcabcbb"',
              out: "3",
            },
            {
              in: 's = "bbbbb"',
              out: "1",
            },
          ],
          constraints: [
            {
              name: "String length",
              min: 0,
              max: 50000,
              desc: "0 ≤ s.length ≤ 5 * 10^4",
            },
          ],
        },
        {
          slug: "valid-parentheses",
          title: "Valid Parentheses",
          difficulty: "Easy",
          tags: ["String", "Stack"],
          statement_md: `Given a string \`s\` containing just the characters \`'('\`, \`')'\`, \`'{'\`, \`'}'\`, \`'['\` and \`']'\`, determine if the input string is valid.

An input string is valid if:
1. Open brackets must be closed by the same type of brackets.
2. Open brackets must be closed in the correct order.`,
          examples: [
            {
              in: 's = "()"',
              out: "true",
            },
            {
              in: 's = "()[]{}"',
              out: "true",
            },
            {
              in: 's = "(]"',
              out: "false",
            },
          ],
          constraints: [
            {
              name: "String length",
              min: 1,
              max: 10000,
              desc: "1 ≤ s.length ≤ 10^4",
            },
          ],
        },
        {
          slug: "median-sorted-arrays",
          title: "Median of Two Sorted Arrays",
          difficulty: "Hard",
          tags: ["Array", "Binary Search", "Divide and Conquer"],
          statement_md: `Given two sorted arrays \`nums1\` and \`nums2\` of size \`m\` and \`n\` respectively, return the median of the two sorted arrays.

The overall run time complexity should be O(log (m+n)).`,
          examples: [
            {
              in: "nums1 = [1,3], nums2 = [2]",
              out: "2.00000",
            },
            {
              in: "nums1 = [1,2], nums2 = [3,4]",
              out: "2.50000",
            },
          ],
          constraints: [
            {
              name: "Array constraints",
              min: 0,
              max: 1000,
              desc: "nums1.length == m, nums2.length == n, 0 ≤ m ≤ 1000, 0 ≤ n ≤ 1000",
            },
          ],
        },
      ];

      setProblems(defaultProblems);
      if (defaultProblems.length > 0 && !selectedProblem) {
        setSelectedProblem(defaultProblems[0]);
      }
    }
  };

  const loadSolution = async (slug: string, lang: string) => {
    try {
      const solution = await apiClient.getSolution(slug, lang);
      // Guard against mismatched content
      const content = solution.code;
      const valid = (() => {
        // reuse heuristic from handleLanguageChange
        const re = {
          py: /\bdef\b|\bimport\b|^#/,
          cpp: /#include|int\s+main\s*\(/,
          c: /#include|int\s+main\s*\(/,
          js: /function\s+|const\s+|let\s+|=>/,
          java: /class\s+\w+|public\s+static\s+void\s+main/,
        } as const;
        const badForPy = /#include|std::|int\s+main\s*\(/;
        if (lang === "py") return re.py.test(content) && !badForPy.test(content);
        return re[lang as keyof typeof re].test(content);
      })();
      setCode(valid ? content : getTemplateCode(lang));
    } catch (error) {
      console.error("Failed to load solution:", error);

      // Try to load from local storage first
      const localSolution = apiClient.loadSolutionLocally(slug, lang);
      if (localSolution) {
        // Only use if it looks like the selected language
        const useLocal = (() => {
          if (lang === "py") return /\bdef\b|\bimport\b|^#/.test(localSolution) && !/#include/.test(localSolution);
          if (lang === "cpp" || lang === "c") return /#include/.test(localSolution);
          if (lang === "js") return /function\s+|const\s+|let\s+/.test(localSolution);
          if (lang === "java") return /class\s+\w+/.test(localSolution);
          return false;
        })();
        setCode(useLocal ? localSolution : getTemplateCode(lang));
        console.log("Loaded solution from local storage");
      } else {
        // Set template code if solution loading fails
        setCode(getTemplateCode(lang));
      }
    }
  };

  const getTemplateCode = (lang: string): string => {
    const templates = {
      py: `def solveNums(nums, target):
    # Your solution here
    return []

# Test
nums = [2, 7, 11, 15]
target = 9
print(solveNums(nums, target))`,
      cpp: `#include <iostream>
#include <vector>
using namespace std;

vector<int> solveNums(vector<int>& nums, int target) {
    // Your solution here
    return {};
}

int main() {
    vector<int> nums = {2, 7, 11, 15};
    int target = 9;
    
    vector<int> result = solveNums(nums, target);
    for (int i : result) {
        cout << i << " ";
    }
    return 0;
}`,
      c: `#include <stdio.h>
#include <stdlib.h>

int* solveNums(int* nums, int numsSize, int target, int* returnSize) {
    // Your solution here
    *returnSize = 0;
    return NULL;
}

int main() {
    int nums[] = {2, 7, 11, 15};
    int target = 9;
    int returnSize;
    
    int* result = solveNums(nums, 4, target, &returnSize);
    
    return 0;
}`,
      js: `function solveNums(nums, target) {
    // Your solution here
    return [];
}

// Test
const nums = [2, 7, 11, 15];
const target = 9;
console.log(solveNums(nums, target));`,
      java: `import java.util.*;

public class Solution {
    public int[] solveNums(int[] nums, int target) {
        // Your solution here
        return new int[]{};
    }
    
    public static void main(String[] args) {
        Solution solution = new Solution();
        int[] nums = {2, 7, 11, 15};
        int target = 9;
        
        int[] result = solution.solveNums(nums, target);
        System.out.println(Arrays.toString(result));
    }
}`,
    };
    return templates[lang as keyof typeof templates] || templates.py;
  };

  const handleProblemSelect = (problem: Problem) => {
    setSelectedProblem(problem);
    setResults(null); // Clear previous results
  };

  const looksLikeLanguage = (content: string, lang: string) => {
    if (!content) return false;
    switch (lang) {
      case "py":
        return (/\bdef\b|\bimport\b|^#/.test(content) && !/#include|std::|int\s+main\s*\(/.test(content));
      case "cpp":
      case "c":
        return /#include|int\s+main\s*\(/.test(content);
      case "js":
        return /function\s+|const\s+|let\s+|=>/.test(content);
      case "java":
        return /class\s+\w+|public\s+static\s+void\s+main/.test(content);
      default:
        return false;
    }
  };

  const handleLanguageChange = (lang: string) => {
    setCurrentLanguage(lang);
    setResults(null);
    // Show immediate, correct code while async loading happens
    if (selectedProblem) {
      const local = apiClient.loadSolutionLocally(selectedProblem.slug, lang);
      if (local && looksLikeLanguage(local, lang)) {
        setCode(local);
      } else {
        setCode(getTemplateCode(lang));
      }
    } else {
      setCode(getTemplateCode(lang));
    }
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

  const handleCodeFormat = () => {
    console.log("Code formatted");
    // Additional formatting logic can be added here
  };

  const handleCodeSave = () => {
    if (selectedProblem) {
      apiClient.saveSolutionLocally(
        selectedProblem.slug,
        currentLanguage,
        code
      );
      console.log("Code saved locally");
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

  const handleSettings = () => {
    alert("Settings functionality not implemented yet");
  };

  const handleSubmit = async () => {
    if (!selectedProblem) return;

    setIsLoading(true);
    setResults(null);

    try {
      const result = await apiClient.runCode({
        action: "run",
        problem: selectedProblem.slug,
        lang: currentLanguage,
        code: code,
        tests: "all",
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

  const handleToggleResults = () => setShowResults((v) => !v);

  // Drag handlers for splitters
  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      if (dragging === "vertical") {
        const x = e.clientX;
        const min = 280;
        const max = 800;
        setLeftWidth(Math.min(max, Math.max(min, x)));
      } else if (dragging === "horizontal") {
        const y = e.clientY;
        const vh = document.documentElement.clientHeight;
        // Convert cursor Y into results panel height (from bottom section)
        const min = 120;
        const max = Math.floor(vh * 0.8);
        const newHeight = Math.min(max, Math.max(min, vh - y - 16));
        setResultsHeight(newHeight);
      }
    };
    const onUp = () => setDragging(null);
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };
  }, [dragging]);

  const handleTestModeChange = (mode: "sample" | "unit" | "all") => {
    setTestMode(mode);
  };

  const handleConnectionRetry = () => {
    checkConnection().then(() => {
      loadProblems();
    });
  };

  // Show loading state while problems are being loaded
  if (problems.length === 0) {
    return (
      <AppContainer>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            height: "100vh",
            flexDirection: "column",
            gap: "16px",
          }}
        >
          <div className="spinner"></div>
          <div>Loading Interview Coding Platform...</div>
        </div>
      </AppContainer>
    );
  }

  return (
    <AppContainer>
      <LeftPanel style={{ width: leftWidth }}>
        <ProblemList
          problems={problems}
          selectedProblem={selectedProblem}
          onProblemSelect={handleProblemSelect}
          connectionStatus={connectionStatus}
          onReconnect={handleConnectionRetry}
        />
        {selectedProblem && <ProblemDescription problem={selectedProblem} />}
      </LeftPanel>

      <VerticalResizer onMouseDown={() => setDragging("vertical")} />

      <RightPanel>
        <EditorSection>
          <EditorContainer>
            <ControlBar
              currentLanguage={currentLanguage}
              onLanguageChange={handleLanguageChange}
              onRun={handleRun}
              onDebug={handleDebug}
              onExplain={handleExplain}
              onSubmit={handleSubmit}
              onSettings={handleSettings}
              isLoading={isLoading}
              testMode={testMode}
              onTestModeChange={handleTestModeChange}
              progress={progress}
              showKeyboardShortcuts={showKeyboardShortcuts}
              resultsVisible={showResults}
              onToggleResults={handleToggleResults}
            />
            <CodeEditor
              language={currentLanguage}
              value={code}
              onChange={handleCodeChange}
              onFormat={handleCodeFormat}
              onSave={handleCodeSave}
            />
          </EditorContainer>

          {showResults && (
            <>
              <HorizontalResizer onMouseDown={() => setDragging("horizontal")} />
              <ResultsContainer style={{ height: resultsHeight }}>
                <ResultsPanel results={results} isLoading={isLoading} />
              </ResultsContainer>
            </>
          )}
        </EditorSection>
      </RightPanel>
    </AppContainer>
  );
}

export default App;
