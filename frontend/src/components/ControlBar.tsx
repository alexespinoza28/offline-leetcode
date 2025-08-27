import React from "react";
import styled from "styled-components";
import { LANGUAGES } from "../types";

const Container = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background-color: #1e1e1e;
  border-bottom: 1px solid #404040;
  border-radius: 12px 12px 0 0;
  margin: 8px 8px 0 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const LeftSection = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const RightSection = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const LanguageSelect = styled.select`
  padding: 8px 14px;
  background-color: #1a1a1a;
  border: 1px solid #404040;
  border-radius: 8px;
  color: #e8e8e8;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  min-width: 130px;
  transition: all 0.2s ease;

  &:focus {
    outline: none;
    border-color: #ffa116;
    box-shadow: 0 0 0 2px rgba(255, 161, 22, 0.1);
  }

  &:hover {
    border-color: #525252;
    background-color: #1e1e1e;
  }
`;

const Button = styled.button<{ variant?: "primary" | "secondary" }>`
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;

  ${(props) =>
    props.variant === "primary"
      ? `
    background: linear-gradient(135deg, #ffa116 0%, #ff8c00 100%);
    color: white;
    box-shadow: 0 2px 4px rgba(255, 161, 22, 0.2);
    
    &:hover:not(:disabled) {
      background: linear-gradient(135deg, #ff8c00 0%, #ff7700 100%);
      box-shadow: 0 4px 8px rgba(255, 161, 22, 0.3);
      transform: translateY(-1px);
    }
  `
      : `
    background-color: #1a1a1a;
    color: #e8e8e8;
    border: 1px solid #404040;
    
    &:hover:not(:disabled) {
      background-color: #1e1e1e;
      border-color: #525252;
      transform: translateY(-1px);
    }
  `}

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none !important;
    box-shadow: none !important;
  }

  &:active:not(:disabled) {
    transform: translateY(0px);
  }
`;

const LoadingSpinner = styled.div`
  width: 16px;
  height: 16px;
  border: 2px solid #3e3e3e;
  border-top: 2px solid #007acc;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 8px;

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
`;

const StatusText = styled.span`
  font-size: 12px;
  color: #888;
  margin-left: 12px;
`;

interface ControlBarProps {
  currentLanguage: string;
  onLanguageChange: (language: string) => void;
  onRun: () => void;
  onDebug: () => void;
  onExplain: () => void;
  isLoading: boolean;
}

const ControlBar: React.FC<ControlBarProps> = ({
  currentLanguage,
  onLanguageChange,
  onRun,
  onDebug,
  onExplain,
  isLoading,
}) => {
  return (
    <Container>
      <LeftSection>
        <LanguageSelect
          value={currentLanguage}
          onChange={(e) => onLanguageChange(e.target.value)}
          disabled={isLoading}
        >
          {LANGUAGES.map((lang) => (
            <option key={lang.id} value={lang.id}>
              {lang.name}
            </option>
          ))}
        </LanguageSelect>
        {isLoading && <StatusText>Running...</StatusText>}
      </LeftSection>

      <RightSection>
        <Button onClick={onExplain} disabled={isLoading}>
          Explain
        </Button>
        <Button onClick={onDebug} disabled={isLoading}>
          Debug
        </Button>
        <Button variant="primary" onClick={onRun} disabled={isLoading}>
          {isLoading ? (
            <>
              <LoadingSpinner />
              Running
            </>
          ) : (
            "Run"
          )}
        </Button>
      </RightSection>
    </Container>
  );
};

export default ControlBar;
