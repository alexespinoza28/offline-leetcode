import React, { useState } from "react";
import styled from "styled-components";
import { RunResult, STATUS_COLORS, STATUS_LABELS } from "../types";

const Container = styled.div`
  height: 100%;
  background-color: #1a1a1a;
  display: flex;
  flex-direction: column;
  border-radius: 12px;
  overflow: hidden;
`;

const TabBar = styled.div`
  display: flex;
  background-color: #1e1e1e;
  border-bottom: 1px solid #404040;
  border-radius: 12px 12px 0 0;
`;

const Tab = styled.button<{ active: boolean }>`
  padding: 12px 20px;
  background: none;
  border: none;
  color: ${(props) => (props.active ? "#e8e8e8" : "#9ca3af")};
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  border-bottom: 3px solid
    ${(props) => (props.active ? "#ffa116" : "transparent")};
  transition: all 0.2s ease;
  border-radius: 4px 4px 0 0;

  &:hover {
    color: #e8e8e8;
    background-color: rgba(255, 255, 255, 0.05);
  }
`;

const Content = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 16px;
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #888;
  font-size: 14px;
  text-align: center;
`;

const LoadingState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #888;
  font-size: 14px;
`;

const LoadingSpinner = styled.div`
  width: 32px;
  height: 32px;
  border: 3px solid #3e3e3e;
  border-top: 3px solid #007acc;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
`;

const StatusHeader = styled.div<{ status: string }>`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding: 16px;
  background-color: #1a1a1a;
  border-radius: 12px;
  border: 1px solid
    ${(props) =>
      STATUS_COLORS[props.status as keyof typeof STATUS_COLORS] || "#404040"};
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const StatusBadge = styled.span<{ status: string }>`
  color: ${(props) =>
    STATUS_COLORS[props.status as keyof typeof STATUS_COLORS] || "#888"};
  font-weight: 600;
  font-size: 14px;
`;

const SummaryGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
`;

const SummaryItem = styled.div`
  background-color: #1a1a1a;
  padding: 16px;
  border-radius: 12px;
  text-align: center;
  border: 1px solid #404040;
  transition: all 0.2s ease;

  &:hover {
    border-color: #525252;
    background-color: #1e1e1e;
  }
`;

const SummaryLabel = styled.div`
  font-size: 12px;
  color: #888;
  margin-bottom: 4px;
`;

const SummaryValue = styled.div`
  font-size: 16px;
  font-weight: 600;
  color: #d4d4d4;
`;

const TestCaseList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const TestCase = styled.div<{ status: string }>`
  background-color: #1a1a1a;
  border-radius: 12px;
  border: 1px solid
    ${(props) =>
      STATUS_COLORS[props.status as keyof typeof STATUS_COLORS] || "#404040"};
  transition: all 0.2s ease;

  &:hover {
    border-color: ${(props) => {
      const color =
        STATUS_COLORS[props.status as keyof typeof STATUS_COLORS] || "#404040";
      return color;
    }};
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  overflow: hidden;
`;

const TestCaseHeader = styled.div`
  padding: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;

  &:hover {
    background-color: #333;
  }
`;

const TestCaseTitle = styled.div`
  font-weight: 500;
  color: #d4d4d4;
`;

const TestCaseMeta = styled.div`
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #888;
`;

const TestCaseDetails = styled.div`
  padding: 0 12px 12px;
  border-top: 1px solid #3e3e3e;
`;

const CodeBlock = styled.pre`
  background-color: #1e1e1e;
  padding: 8px;
  border-radius: 3px;
  font-size: 12px;
  font-family: "Fira Code", "Consolas", monospace;
  overflow-x: auto;
  margin: 8px 0;
  color: #d4d4d4;
`;

const LogSection = styled.div`
  margin-bottom: 16px;
`;

const LogTitle = styled.h4`
  color: #d4d4d4;
  margin-bottom: 8px;
  font-size: 14px;
`;

interface ResultsPanelProps {
  results: RunResult | null;
  isLoading: boolean;
}

const ResultsPanel: React.FC<ResultsPanelProps> = ({ results, isLoading }) => {
  const [activeTab, setActiveTab] = useState<"results" | "logs">("results");
  const [expandedTestCase, setExpandedTestCase] = useState<string | null>(null);

  if (isLoading) {
    return (
      <Container>
        <LoadingState>
          <LoadingSpinner />
          <div>Running your code...</div>
        </LoadingState>
      </Container>
    );
  }

  if (!results) {
    return (
      <Container>
        <EmptyState>
          <div>🚀</div>
          <div style={{ marginTop: "8px" }}>
            Run your code to see results here
          </div>
        </EmptyState>
      </Container>
    );
  }

  return (
    <Container>
      <TabBar>
        <Tab
          active={activeTab === "results"}
          onClick={() => setActiveTab("results")}
        >
          Test Results
        </Tab>
        <Tab active={activeTab === "logs"} onClick={() => setActiveTab("logs")}>
          Logs
        </Tab>
      </TabBar>

      <Content>
        {activeTab === "results" ? (
          <>
            <StatusHeader status={results.status}>
              <StatusBadge status={results.status}>
                {STATUS_LABELS[results.status as keyof typeof STATUS_LABELS] ||
                  results.status}
              </StatusBadge>
              {results.summary && (
                <div style={{ fontSize: "13px", color: "#888" }}>
                  {results.summary.passed}/{results.summary.total} test cases
                  passed
                </div>
              )}
            </StatusHeader>

            {results.summary && (
              <SummaryGrid>
                <SummaryItem>
                  <SummaryLabel>Passed</SummaryLabel>
                  <SummaryValue style={{ color: STATUS_COLORS.OK }}>
                    {results.summary.passed}
                  </SummaryValue>
                </SummaryItem>
                <SummaryItem>
                  <SummaryLabel>Failed</SummaryLabel>
                  <SummaryValue style={{ color: STATUS_COLORS.WA }}>
                    {results.summary.failed}
                  </SummaryValue>
                </SummaryItem>
                <SummaryItem>
                  <SummaryLabel>Time</SummaryLabel>
                  <SummaryValue>{results.summary.time_ms}ms</SummaryValue>
                </SummaryItem>
                <SummaryItem>
                  <SummaryLabel>Memory</SummaryLabel>
                  <SummaryValue>{results.summary.memory_mb}MB</SummaryValue>
                </SummaryItem>
              </SummaryGrid>
            )}

            {results.cases && results.cases.length > 0 && (
              <TestCaseList>
                {results.cases.map((testCase) => (
                  <TestCase key={testCase.id} status={testCase.status}>
                    <TestCaseHeader
                      onClick={() =>
                        setExpandedTestCase(
                          expandedTestCase === testCase.id ? null : testCase.id
                        )
                      }
                    >
                      <TestCaseTitle>
                        Test Case {testCase.id} -{" "}
                        {
                          STATUS_LABELS[
                            testCase.status as keyof typeof STATUS_LABELS
                          ]
                        }
                      </TestCaseTitle>
                      <TestCaseMeta>
                        {testCase.time_ms && <span>{testCase.time_ms}ms</span>}
                        {testCase.memory_mb && (
                          <span>{testCase.memory_mb}MB</span>
                        )}
                      </TestCaseMeta>
                    </TestCaseHeader>

                    {expandedTestCase === testCase.id && (
                      <TestCaseDetails>
                        {testCase.input && (
                          <div>
                            <strong>Input:</strong>
                            <CodeBlock>{testCase.input}</CodeBlock>
                          </div>
                        )}
                        {testCase.expected && (
                          <div>
                            <strong>Expected:</strong>
                            <CodeBlock>{testCase.expected}</CodeBlock>
                          </div>
                        )}
                        {testCase.actual && (
                          <div>
                            <strong>Actual:</strong>
                            <CodeBlock>{testCase.actual}</CodeBlock>
                          </div>
                        )}
                        {testCase.diff && (
                          <div>
                            <strong>Diff:</strong>
                            <CodeBlock>{testCase.diff}</CodeBlock>
                          </div>
                        )}
                      </TestCaseDetails>
                    )}
                  </TestCase>
                ))}
              </TestCaseList>
            )}
          </>
        ) : (
          <>
            {results.logs?.compile && (
              <LogSection>
                <LogTitle>Compilation Output</LogTitle>
                <CodeBlock>{results.logs.compile}</CodeBlock>
              </LogSection>
            )}
            {results.logs?.stderr && (
              <LogSection>
                <LogTitle>Runtime Errors</LogTitle>
                <CodeBlock>{results.logs.stderr}</CodeBlock>
              </LogSection>
            )}
            {!results.logs?.compile && !results.logs?.stderr && (
              <EmptyState>
                <div>No logs available</div>
              </EmptyState>
            )}
          </>
        )}
      </Content>
    </Container>
  );
};

export default ResultsPanel;
