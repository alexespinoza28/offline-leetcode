import React, { useState } from "react";
import styled from "styled-components";
// import SyntaxHighlighter from "react-syntax-highlighter";
// import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
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

const FilterBar = styled.div`
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
`;

const FilterButton = styled.button<{ active: boolean }>`
  background-color: ${(props) => (props.active ? "#ffa116" : "#1e1e1e")};
  border: 1px solid ${(props) => (props.active ? "#ffa116" : "#404040")};
  border-radius: 6px;
  color: ${(props) => (props.active ? "#000" : "#9ca3af")};
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  padding: 6px 12px;
  transition: all 0.2s ease;

  &:hover {
    color: ${(props) => (props.active ? "#000" : "#e8e8e8")};
    background-color: ${(props) =>
      props.active ? "#ffb84d" : "rgba(255, 255, 255, 0.05)"};
  }
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
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
`;

const TestCase = styled.div<{ status: string }>`
  background-color: #1e1e1e;
  border-radius: 8px;
  border-left: 4px solid
    ${(props) =>
      STATUS_COLORS[props.status as keyof typeof STATUS_COLORS] || "#404040"};
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background-color: #2a2a2a;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  }
`;

const TestCaseHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
`;

const TestCaseTitle = styled.div`
  font-size: 13px;
  font-weight: 600;
  color: #d4d4d4;
`;

const TestCaseDetails = styled.div`
  font-size: 12px;
  color: #888;
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
  white-space: pre-wrap;
  word-wrap: break-word;
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
  const [statusFilter, setStatusFilter] = useState<string>("all");

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
              <>
                <FilterBar>
                  <FilterButton
                    active={statusFilter === "all"}
                    onClick={() => setStatusFilter("all")}
                  >
                    All
                  </FilterButton>
                  <FilterButton
                    active={statusFilter === "OK"}
                    onClick={() => setStatusFilter("OK")}
                  >
                    Passed
                  </FilterButton>
                  <FilterButton
                    active={statusFilter === "WA"}
                    onClick={() => setStatusFilter("WA")}
                  >
                    Failed
                  </FilterButton>
                  <FilterButton
                    active={statusFilter === "TLE"}
                    onClick={() => setStatusFilter("TLE")}
                  >
                    Time Limit Exceeded
                  </FilterButton>
                  <FilterButton
                    active={statusFilter === "MLE"}
                    onClick={() => setStatusFilter("MLE")}
                  >
                    Memory Limit Exceeded
                  </FilterButton>
                </FilterBar>
                <TestCaseList>
                  {results.cases
                    .filter(
                      (testCase) =>
                        statusFilter === "all" ||
                        testCase.status === statusFilter
                    )
                    .map((testCase) => (
                      <TestCase key={testCase.id} status={testCase.status}>
                        <TestCaseHeader>
                          <TestCaseTitle>Test Case {testCase.id}</TestCaseTitle>
                          <StatusBadge status={testCase.status}>
                            {STATUS_LABELS[
                              testCase.status as keyof typeof STATUS_LABELS
                            ] || testCase.status}
                          </StatusBadge>
                        </TestCaseHeader>
                        <TestCaseDetails>
                          {testCase.time_ms && (
                            <span>{testCase.time_ms}ms</span>
                          )}
                          {testCase.memory_mb && (
                            <span>, {testCase.memory_mb}MB</span>
                          )}
                        </TestCaseDetails>
                      </TestCase>
                    ))}
                </TestCaseList>
              </>
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
