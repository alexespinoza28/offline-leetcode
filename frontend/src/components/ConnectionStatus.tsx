import React, { useState, useEffect } from "react";
import styled from "styled-components";
import { apiClient } from "../services/api";

const StatusBar = styled.div<{ status: "online" | "offline" | "error" }>`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 500;
  text-align: center;
  transition: all 0.3s ease;
  transform: ${(props) =>
    props.status === "online" ? "translateY(-100%)" : "translateY(0)"};

  ${(props) => {
    switch (props.status) {
      case "offline":
        return `
          background-color: #dc2626;
          color: white;
        `;
      case "error":
        return `
          background-color: #f59e0b;
          color: white;
        `;
      default:
        return `
          background-color: #10b981;
          color: white;
        `;
    }
  }}
`;

const StatusIcon = styled.span`
  margin-right: 8px;
`;

const RetryButton = styled.button`
  background: none;
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  margin-left: 12px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }
`;

interface ConnectionStatusProps {
  onRetry?: () => void;
}

const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ onRetry }) => {
  const [status, setStatus] = useState<"online" | "offline" | "error">(
    "online"
  );
  const [message, setMessage] = useState("");
  const [isChecking, setIsChecking] = useState(false);

  const checkConnection = async () => {
    if (isChecking) return;

    setIsChecking(true);
    try {
      const isAvailable = await apiClient.isApiAvailable();
      if (isAvailable) {
        setStatus("online");
        setMessage("Connected to server");
      } else {
        setStatus("error");
        setMessage("Server unavailable - working offline");
      }
    } catch (error) {
      if (!navigator.onLine) {
        setStatus("offline");
        setMessage("No internet connection - working offline");
      } else {
        setStatus("error");
        setMessage("Server connection failed - working offline");
      }
    } finally {
      setIsChecking(false);
    }
  };

  const handleRetry = () => {
    checkConnection();
    onRetry?.();
  };

  useEffect(() => {
    // Initial check
    checkConnection();

    // Listen for online/offline events
    const handleOnline = () => {
      setStatus("online");
      setMessage("Connection restored");
      checkConnection();
    };

    const handleOffline = () => {
      setStatus("offline");
      setMessage("No internet connection - working offline");
    };

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    // Periodic health checks
    const interval = setInterval(checkConnection, 30000); // Check every 30 seconds

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
      clearInterval(interval);
    };
  }, []);

  const getStatusIcon = () => {
    switch (status) {
      case "online":
        return "🟢";
      case "offline":
        return "🔴";
      case "error":
        return "🟡";
      default:
        return "⚪";
    }
  };

  return (
    <StatusBar status={status}>
      <StatusIcon>{getStatusIcon()}</StatusIcon>
      {message}
      {status !== "online" && (
        <RetryButton onClick={handleRetry} disabled={isChecking}>
          {isChecking ? "Checking..." : "Retry"}
        </RetryButton>
      )}
    </StatusBar>
  );
};

export default ConnectionStatus;
