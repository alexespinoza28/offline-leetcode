import React from "react";
import { SettingsPanelProps } from "../types";

const EditorSettings: React.FC<SettingsPanelProps> = ({
  settings,
  onSettingsChange,
  languages,
  currentLanguage,
  onLanguageChange,
}) => {
  const containerStyles: React.CSSProperties = {
    padding: "0",
  };

  const sectionStyles: React.CSSProperties = {
    marginBottom: "24px",
  };

  const titleStyles: React.CSSProperties = {
    fontSize: "18px",
    fontWeight: "600",
    color: "#111827",
    marginBottom: "16px",
  };

  const fieldStyles: React.CSSProperties = {
    marginBottom: "16px",
  };

  const labelStyles: React.CSSProperties = {
    display: "block",
    fontSize: "14px",
    fontWeight: "500",
    color: "#374151",
    marginBottom: "4px",
  };

  const inputStyles: React.CSSProperties = {
    width: "100%",
    padding: "8px 12px",
    border: "1px solid #d1d5db",
    borderRadius: "6px",
    fontSize: "14px",
    backgroundColor: "#ffffff",
  };

  const selectStyles: React.CSSProperties = {
    ...inputStyles,
    cursor: "pointer",
  };

  const checkboxContainerStyles: React.CSSProperties = {
    display: "flex",
    alignItems: "center",
    gap: "8px",
  };

  const checkboxStyles: React.CSSProperties = {
    width: "16px",
    height: "16px",
    cursor: "pointer",
  };

  return (
    <div style={containerStyles}>
      <div style={sectionStyles}>
        <h3 style={titleStyles}>Language Settings</h3>

        <div style={fieldStyles}>
          <label style={labelStyles}>Programming Language</label>
          <select
            style={selectStyles}
            value={currentLanguage}
            onChange={(e) => onLanguageChange(e.target.value)}
          >
            {languages.map((lang) => (
              <option key={lang.id} value={lang.id}>
                {lang.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div style={sectionStyles}>
        <h3 style={titleStyles}>Editor Settings</h3>

        <div style={fieldStyles}>
          <label style={labelStyles}>Theme</label>
          <select
            style={selectStyles}
            value={settings.theme}
            onChange={(e) =>
              onSettingsChange({ theme: e.target.value as "light" | "dark" })
            }
          >
            <option value="dark">Dark</option>
            <option value="light">Light</option>
          </select>
        </div>

        <div style={fieldStyles}>
          <label style={labelStyles}>Font Size</label>
          <input
            type="number"
            style={inputStyles}
            value={settings.fontSize}
            onChange={(e) =>
              onSettingsChange({ fontSize: parseInt(e.target.value) || 14 })
            }
            min="10"
            max="24"
          />
        </div>

        <div style={fieldStyles}>
          <label style={labelStyles}>Tab Size</label>
          <input
            type="number"
            style={inputStyles}
            value={settings.tabSize}
            onChange={(e) =>
              onSettingsChange({ tabSize: parseInt(e.target.value) || 2 })
            }
            min="1"
            max="8"
          />
        </div>

        <div style={fieldStyles}>
          <div style={checkboxContainerStyles}>
            <input
              type="checkbox"
              style={checkboxStyles}
              checked={settings.wordWrap}
              onChange={(e) => onSettingsChange({ wordWrap: e.target.checked })}
            />
            <label style={labelStyles}>Word Wrap</label>
          </div>
        </div>

        <div style={fieldStyles}>
          <div style={checkboxContainerStyles}>
            <input
              type="checkbox"
              style={checkboxStyles}
              checked={settings.showLineNumbers}
              onChange={(e) =>
                onSettingsChange({ showLineNumbers: e.target.checked })
              }
            />
            <label style={labelStyles}>Show Line Numbers</label>
          </div>
        </div>

        <div style={fieldStyles}>
          <div style={checkboxContainerStyles}>
            <input
              type="checkbox"
              style={checkboxStyles}
              checked={settings.autoComplete}
              onChange={(e) =>
                onSettingsChange({ autoComplete: e.target.checked })
              }
            />
            <label style={labelStyles}>Auto Complete</label>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EditorSettings;
