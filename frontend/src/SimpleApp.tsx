import React, { useState } from "react";
import styled from "styled-components";
import { Problem } from "./types";

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
  padding: 16px;
`;

const RightPanel = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #0f0f0f;
  padding: 16px;
`;

const Title = styled.h1`
  color: #ffa116;
  margin-bottom: 20px;
`;

const ProblemItem = styled.div<{ selected: boolean }>`
  padding: 12px;
  margin-bottom: 8px;
  background-color: ${(props) => (props.selected ? "#ffa11620" : "#1a1a1a")};
  border-radius: 8px;
  cursor: pointer;
  border: 1px solid ${(props) => (props.selected ? "#ffa116" : "transparent")};

  &:hover {
    background-color: #2a2a2a;
  }
`;

const ProblemTitle = styled.div`
  font-weight: 600;
  margin-bottom: 4px;
`;

const ProblemDifficulty = styled.span<{ difficulty: string }>`
  color: ${(props) =>
    props.difficulty === "Easy"
      ? "#4caf50"
      : props.difficulty === "Medium"
      ? "#ff9800"
      : "#f44336"};
  font-size: 12px;
`;

const CodeArea = styled.textarea`
  flex: 1;
  background-color: #1a1a1a;
  color: #e8e8e8;
  border: 1px solid #404040;
  border-radius: 8px;
  padding: 16px;
  font-family: "Consolas", "Monaco", "Courier New", monospace;
  font-size: 14px;
  resize: none;
  outline: none;

  &:focus {
    border-color: #ffa116;
  }
`;

const Button = styled.button`
  background-color: #0e639c;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  margin: 8px 8px 8px 0;

  &:hover {
    background-color: #1177bb;
  }
`;

const ProblemDescription = styled.div`
  background-color: #1a1a1a;
  padding: 16px;
  border-radius: 8px;
  margin-top: 16px;
  max-height: 300px;
  overflow-y: auto;
`;

function SimpleApp() {
  const defaultProblems: Problem[] = [
    {
      slug: "two-sum",
      title: "Two Sum",
      difficulty: "Easy",
      tags: ["Array", "Hash Table"],
      statement_md:
        "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
      examples: [{ in: "nums = [2,7,11,15], target = 9", out: "[0,1]" }],
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
      slug: "valid-parentheses",
      title: "Valid Parentheses",
      difficulty: "Easy",
      tags: ["String", "Stack"],
      statement_md:
        "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.",
      examples: [{ in: 's = "()"', out: "true" }],
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
      slug: "longest-substring",
      title: "Longest Substring Without Repeating Characters",
      difficulty: "Medium",
      tags: ["Hash Table", "String", "Sliding Window"],
      statement_md:
        "Given a string s, find the length of the longest substring without repeating characters.",
      examples: [{ in: 's = "abcabcbb"', out: "3" }],
      constraints: [
        {
          name: "String length",
          min: 0,
          max: 50000,
          desc: "0 ≤ s.length ≤ 5 * 10^4",
        },
      ],
    },
  ];

  const [problems] = useState<Problem[]>(defaultProblems);
  const [selectedProblem, setSelectedProblem] = useState<Problem>(
    defaultProblems[0]
  );
  const [code, setCode] = useState<string>(`def solve(nums, target):
    # Your solution here
    return []

# Test
nums = [2, 7, 11, 15]
target = 9
print(solve(nums, target))`);

  const handleRun = () => {
    alert(
      "Code execution would happen here!\n\nIn the full version, this would:\n1. Send code to backend\n2. Run tests\n3. Show results"
    );
  };

  return (
    <AppContainer>
      <LeftPanel>
        <Title>Problems</Title>
        {problems.map((problem) => (
          <ProblemItem
            key={problem.slug}
            selected={selectedProblem.slug === problem.slug}
            onClick={() => setSelectedProblem(problem)}
          >
            <ProblemTitle>{problem.title}</ProblemTitle>
            <ProblemDifficulty difficulty={problem.difficulty}>
              {problem.difficulty}
            </ProblemDifficulty>
          </ProblemItem>
        ))}

        <ProblemDescription>
          <h3>{selectedProblem.title}</h3>
          <p>{selectedProblem.statement_md}</p>
          <h4>Example:</h4>
          <div
            style={{
              fontFamily: "monospace",
              backgroundColor: "#2a2a2a",
              padding: "8px",
              borderRadius: "4px",
            }}
          >
            <div>Input: {selectedProblem.examples[0].in}</div>
            <div>Output: {selectedProblem.examples[0].out}</div>
          </div>
        </ProblemDescription>
      </LeftPanel>

      <RightPanel>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            marginBottom: "16px",
          }}
        >
          <Title style={{ margin: 0, marginRight: "16px" }}>Code Editor</Title>
          <Button onClick={handleRun}>Run Code</Button>
          <Button style={{ backgroundColor: "#28a745" }}>Submit</Button>
        </div>

        <CodeArea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="Write your solution here..."
        />

        <div
          style={{
            marginTop: "16px",
            padding: "16px",
            backgroundColor: "#1a1a1a",
            borderRadius: "8px",
            minHeight: "100px",
          }}
        >
          <h4>Results</h4>
          <p style={{ color: "#888" }}>
            Run your code to see test results here. The full version includes:
          </p>
          <ul style={{ color: "#888", fontSize: "14px" }}>
            <li>Test case execution</li>
            <li>Performance metrics</li>
            <li>Error messages</li>
            <li>Code explanations</li>
          </ul>
        </div>
      </RightPanel>
    </AppContainer>
  );
}

export default SimpleApp;
