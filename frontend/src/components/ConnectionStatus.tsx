import React from "react";
import { ConnectionStatus as ConnectionStatusType } from "../types";

interface ConnectionStatusProps {
  status: ConnectionStatusType;
  onReconnect: () => void;
}

const ConnectionStatus: React.FC<ConnectionStatusProps> = ({
  status,
  onReconnect,
}) => {
  const getStatusColor = () => {
    return status.connected ? "#10b981" : "#ef4444";
  };

  const getStatusText = () => {
    if (status.connected) {
      return `Connected${status.latency ? ` (${status.latency}ms)` : ""}`;
    }
    return status.error || "Disconnected";
  };

  const containerStyles: React.CSSProperties = {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    padding: "6px 12px",
    borderRadius: "6px",
    backgroundColor: status.connected ? "#d1fae5" : "#fee2e2",
    border: `1px solid ${getStatusColor()}`,
    fontSize: "12px",
    fontWeight: "500",
  };

  const indicatorStyles: React.CSSProperties = {
    width: "8px",
    height: "8px",
    borderRadius: "50%",
    backgroundColor: getStatusColor(),
    animation: status.connected ? "none" : "pulse 2s infinite",
  };

  const textStyles: React.CSSProperties = {
    color: getStatusColor(),
  };

  const buttonStyles: React.CSSProperties = {
    background: "none",
    border: "none",
    color: getStatusColor(),
    cursor: "pointer",
    fontSize: "12px",
    textDecoration: "underline",
    padding: "0",
    marginLeft: "4px",
  };

  return (
    <>
      <style>
        {`
          @keyframes pulse {
            0%, 100% {
              opacity: 1;
            }
            50% {
              opacity: 0.5;
            }
          }
        `}
      </style>
      <div style={containerStyles}>
        <div style={indicatorStyles}></div>
        <span style={textStyles}>{getStatusText()}</span>
        {!status.connected && onReconnect && (
          <button
            style={buttonStyles}
            onClick={onReconnect}
            onMouseEnter={(e) => {
              e.currentTarget.style.opacity = "0.8";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.opacity = "1";
            }}
          >
            Reconnect
          </button>
        )}
        {status.lastPing && (
          <span style={{ ...textStyles, opacity: 0.7, fontSize: "11px" }}>
            Last: {status.lastPing.toLocaleTimeString()}
          </span>
        )}
      </div>
    </>
  );
};

export default ConnectionStatus;
