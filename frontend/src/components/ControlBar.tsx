import React, { useState, useEffect } from "react";
import styled, { keyframes, css } from "styled-components";
import { LANGUAGES } from "../types";

const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
`;

const slideIn = keyframes`
  from { transform: translateY(-10px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
`;

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
  position: relative;
  overflow: hidden;
`;

const LeftSection = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const MiddleSection = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
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

const Button = styled.button<{
  variant?: "primary" | "secondary" | "success" | "warning" | "danger";
  size?: "small" | "medium" | "large";
  isActive?: boolean;
}>`
  padding: ${(props) => {
    switch (props.size) {
      case "small":
        return "6px 12px";
      case "large":
        return "10px 20px";
      default:
        return "8px 16px";
    }
  }};
  border: none;
  border-radius: 8px;
  font-size: ${(props) => {
    switch (props.size) {
      case "small":
        return "11px";
      case "large":
        return "14px";
      default:
        return "13px";
    }
  }};
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: ${(props) => (props.size === "small" ? "60px" : "80px")};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  position: relative;
  overflow: hidden;

  ${(props) => {
    switch (props.variant) {
      case "primary":
        return `
          background: linear-gradient(135deg, #ffa116 0%, #ff8c00 100%);
          color: white;
          box-shadow: 0 2px 4px rgba(255, 161, 22, 0.2);
          
          &:hover:not(:disabled) {
            background: linear-gradient(135deg, #ff8c00 0%, #ff7700 100%);
            box-shadow: 0 4px 8px rgba(255, 161, 22, 0.3);
            transform: translateY(-1px);
          }
        `;
      case "success":
        return `
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
          color: white;
          box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
          
          &:hover:not(:disabled) {
            background: linear-gradient(135deg, #059669 0%, #047857 100%);
            box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
            transform: translateY(-1px);
          }
        `;
      case "warning":
        return `
          background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
          color: white;
          box-shadow: 0 2px 4px rgba(245, 158, 11, 0.2);
          
          &:hover:not(:disabled) {
            background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
            box-shadow: 0 4px 8px rgba(245, 158, 11, 0.3);
            transform: translateY(-1px);
          }
        `;
      case "danger":
        return `
          background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
          color: white;
          box-shadow: 0 2px 4px rgba(239, 68, 68, 0.2);
          
          &:hover:not(:disabled) {
            background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
            box-shadow: 0 4px 8px rgba(239, 68, 68, 0.3);
            transform: translateY(-1px);
          }
        `;
      default:
        return `
          background-color: ${props.isActive ? "#2563eb" : "#1a1a1a"};
          color: #e8e8e8;
          border: 1px solid ${props.isActive ? "#2563eb" : "#404040"};
          
          &:hover:not(:disabled) {
            background-color: ${props.isActive ? "#1d4ed8" : "#1e1e1e"};
            border-color: ${props.isActive ? "#1d4ed8" : "#525252"};
            transform: translateY(-1px);
          }
        `;
    }
  }}

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none !important;
    box-shadow: none !important;
  }

  &:active:not(:disabled) {
    transform: translateY(0px);
  }

  ${(props) =>
    props.isActive &&
    css`
      &::after {
        content: "";
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 2px;
        background-color: #ffa116;
      }
    `}
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

const StatusIndicator = styled.div<{
  status: "idle" | "running" | "success" | "error";
}>`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: ${(props) => {
    switch (props.status) {
      case "running":
        return "#ffa116";
      case "success":
        return "#10b981";
      case "error":
        return "#ef4444";
      default:
        return "#6b7280";
    }
  }};
  margin-right: 8px;

  ${(props) =>
    props.status === "running" &&
    css`
      animation: ${pulse} 1.5s ease-in-out infinite;
    `}
`;

const TestModeSelector = styled.div`
  display: flex;
  align-items: center;
  gap: 2px;
  background-color: #1a1a1a;
  border: 1px solid #404040;
  border-radius: 6px;
  padding: 2px;
`;

const TestModeButton = styled.button<{ isActive: boolean }>`
  background-color: ${(props) => (props.isActive ? "#ffa116" : "transparent")};
  border: none;
  border-radius: 4px;
  color: ${(props) => (props.isActive ? "#000" : "#9ca3af")};
  cursor: pointer;
  font-size: 11px;
  font-weight: 500;
  padding: 4px 8px;
  transition: all 0.2s ease;

  &:hover {
    color: ${(props) => (props.isActive ? "#000" : "#e8e8e8")};
    background-color: ${(props) =>
      props.isActive ? "#ffb84d" : "rgba(255, 255, 255, 0.05)"};
  }
`;

const Separator = styled.div`
  width: 1px;
  height: 20px;
  background-color: #404040;
  margin: 0 8px;
`;

const ProgressBar = styled.div<{ progress: number; show: boolean }>`
  position: absolute;
  bottom: 0;
  left: 0;
  height: 2px;
  background-color: #ffa116;
  width: ${(props) => props.progress}%;
  transition: width 0.3s ease;
  opacity: ${(props) => (props.show ? 1 : 0)};
`;

const KeyboardShortcut = styled.span`
  font-size: 10px;
  color: #6b7280;
  margin-left: 4px;
`;

const Tooltip = styled.div<{ show: boolean }>`
  position: absolute;
  bottom: -35px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #000;
  color: #fff;
  padding: 6px 8px;
  border-radius: 4px;
  font-size: 11px;
  white-space: nowrap;
  opacity: ${(props) => (props.show ? 1 : 0)};
  visibility: ${(props) => (props.show ? "visible" : "hidden")};
  transition: all 0.2s ease;
  z-index: 1000;
  animation: ${slideIn} 0.2s ease;

  &::before {
    content: "";
    position: absolute;
    top: -4px;
    left: 50%;
    transform: translateX(-50%);
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 4px solid #000;
  }
`;

const ButtonWithTooltip = styled.div`
  position: relative;
  display: inline-block;
`;

interface ControlBarProps {
  currentLanguage: string;
  onLanguageChange: (language: string) => void;
  onRun: () => void;
  onDebug: () => void;
  onExplain: () => void;
  onSettings?: () => void;
  onValidate?: () => void;
  onSubmit?: () => void;
  isLoading: boolean;
  executionStatus?: "idle" | "running" | "success" | "error";
  testMode?: "sample" | "unit" | "all";
  onTestModeChange?: (mode: "sample" | "unit" | "all") => void;
  progress?: number;
  showKeyboardShortcuts?: boolean;
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
