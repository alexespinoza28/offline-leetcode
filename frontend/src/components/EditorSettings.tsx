import React, { useState } from "react";
import styled from "styled-components";

const SettingsOverlay = styled.div<{ isOpen: boolean }>`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: ${(props) => (props.isOpen ? "flex" : "none")};
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const SettingsPanel = styled.div`
  background-color: #1a1a1a;
  border-radius: 12px;
  padding: 24px;
  width: 400px;
  max-width: 90vw;
  border: 1px solid #404040;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
`;

const SettingsHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
`;

const SettingsTitle = styled.h3`
  color: #e8e8e8;
  font-size: 18px;
  font-weight: 600;
  margin: 0;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: #9ca3af;
  font-size: 20px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;

  &:hover {
    color: #e8e8e8;
    background-color: rgba(255, 255, 255, 0.05);
  }
`;

const SettingGroup = styled.div`
  margin-bottom: 20px;
`;

const SettingLabel = styled.label`
  display: block;
  color: #e8e8e8;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
`;

const SettingDescription = styled.p`
  color: #9ca3af;
  font-size: 12px;
  margin: 4px 0 8px 0;
`;

const Select = styled.select`
  width: 100%;
  padding: 8px 12px;
  background-color: #0f0f0f;
  border: 1px solid #404040;
  border-radius: 6px;
  color: #e8e8e8;
  font-size: 13px;
  cursor: pointer;

  &:focus {
    outline: none;
    border-color: #ffa116;
    box-shadow: 0 0 0 2px rgba(255, 161, 22, 0.1);
  }
`;

const Checkbox = styled.input.attrs({ type: "checkbox" })`
  margin-right: 8px;
  accent-color: #ffa116;
`;

const CheckboxLabel = styled.label`
  display: flex;
  align-items: center;
  color: #e8e8e8;
  font-size: 14px;
  cursor: pointer;
  margin-bottom: 8px;

  &:hover {
    color: #ffa116;
  }
`;

const Slider = styled.input.attrs({ type: "range" })`
  width: 100%;
  height: 4px;
  background: #404040;
  border-radius: 2px;
  outline: none;

  &::-webkit-slider-thumb {
    appearance: none;
    width: 16px;
    height: 16px;
    background: #ffa116;
    border-radius: 50%;
    cursor: pointer;
  }

  &::-moz-range-thumb {
    width: 16px;
    height: 16px;
    background: #ffa116;
    border-radius: 50%;
    cursor: pointer;
    border: none;
  }
`;

const SliderValue = styled.span`
  color: #9ca3af;
  font-size: 12px;
  float: right;
`;

export interface EditorSettings {
  fontSize: number;
  fontFamily: string;
  theme: string;
  tabSize: number;
  insertSpaces: boolean;
  wordWrap: boolean;
  minimap: boolean;
  lineNumbers: boolean;
  folding: boolean;
  bracketPairColorization: boolean;
  renderWhitespace: boolean;
  smoothScrolling: boolean;
  cursorBlinking: string;
  autoSave: boolean;
  formatOnSave: boolean;
  vimMode: boolean;
}

interface EditorSettingsProps {
  isOpen: boolean;
  onClose: () => void;
  settings: EditorSettings;
  onSettingsChange: (settings: EditorSettings) => void;
}

const EditorSettingsComponent: React.FC<EditorSettingsProps> = ({
  isOpen,
  onClose,
  settings,
  onSettingsChange,
}) => {
  const [localSettings, setLocalSettings] = useState<EditorSettings>(settings);

  const handleSettingChange = (key: keyof EditorSettings, value: any) => {
    const newSettings = { ...localSettings, [key]: value };
    setLocalSettings(newSettings);
    onSettingsChange(newSettings);
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <SettingsOverlay isOpen={isOpen} onClick={handleOverlayClick}>
      <SettingsPanel>
        <SettingsHeader>
          <SettingsTitle>Editor Settings</SettingsTitle>
          <CloseButton onClick={onClose}>×</CloseButton>
        </SettingsHeader>

        <SettingGroup>
          <SettingLabel>Font Size</SettingLabel>
          <SettingDescription>Adjust the editor font size</SettingDescription>
          <Slider
            min="10"
            max="24"
            value={localSettings.fontSize}
            onChange={(e) =>
              handleSettingChange("fontSize", parseInt(e.target.value))
            }
          />
          <SliderValue>{localSettings.fontSize}px</SliderValue>
        </SettingGroup>

        <SettingGroup>
          <SettingLabel>Font Family</SettingLabel>
          <SettingDescription>Choose your preferred font</SettingDescription>
          <Select
            value={localSettings.fontFamily}
            onChange={(e) => handleSettingChange("fontFamily", e.target.value)}
          >
            <option value="'JetBrains Mono', 'Fira Code', 'SF Mono', 'Consolas', 'Monaco', monospace">
              JetBrains Mono
            </option>
            <option value="'Fira Code', 'SF Mono', 'Consolas', 'Monaco', monospace">
              Fira Code
            </option>
            <option value="'SF Mono', 'Consolas', 'Monaco', monospace">
              SF Mono
            </option>
            <option value="'Consolas', 'Monaco', monospace">Consolas</option>
            <option value="'Monaco', monospace">Monaco</option>
            <option value="monospace">System Monospace</option>
          </Select>
        </SettingGroup>

        <SettingGroup>
          <SettingLabel>Theme</SettingLabel>
          <SettingDescription>Choose editor color theme</SettingDescription>
          <Select
            value={localSettings.theme}
            onChange={(e) => handleSettingChange("theme", e.target.value)}
          >
            <option value="leetcode-dark">LeetCode Dark</option>
            <option value="vs-dark">VS Code Dark</option>
            <option value="vs">VS Code Light</option>
            <option value="hc-black">High Contrast</option>
          </Select>
        </SettingGroup>

        <SettingGroup>
          <SettingLabel>Tab Size</SettingLabel>
          <SettingDescription>Number of spaces per tab</SettingDescription>
          <Select
            value={localSettings.tabSize}
            onChange={(e) =>
              handleSettingChange("tabSize", parseInt(e.target.value))
            }
          >
            <option value="2">2 spaces</option>
            <option value="4">4 spaces</option>
            <option value="8">8 spaces</option>
          </Select>
        </SettingGroup>

        <SettingGroup>
          <CheckboxLabel>
            <Checkbox
              checked={localSettings.insertSpaces}
              onChange={(e) =>
                handleSettingChange("insertSpaces", e.target.checked)
              }
            />
            Insert spaces instead of tabs
          </CheckboxLabel>

          <CheckboxLabel>
            <Checkbox
              checked={localSettings.wordWrap}
              onChange={(e) =>
                handleSettingChange("wordWrap", e.target.checked)
              }
            />
            Word wrap
          </CheckboxLabel>

          <CheckboxLabel>
            <Checkbox
              checked={localSettings.minimap}
              onChange={(e) => handleSettingChange("minimap", e.target.checked)}
            />
            Show minimap
          </CheckboxLabel>

          <CheckboxLabel>
            <Checkbox
              checked={localSettings.lineNumbers}
              onChange={(e) =>
                handleSettingChange("lineNumbers", e.target.checked)
              }
            />
            Show line numbers
          </CheckboxLabel>

          <CheckboxLabel>
            <Checkbox
              checked={localSettings.folding}
              onChange={(e) => handleSettingChange("folding", e.target.checked)}
            />
            Code folding
          </CheckboxLabel>

          <CheckboxLabel>
            <Checkbox
              checked={localSettings.bracketPairColorization}
              onChange={(e) =>
                handleSettingChange("bracketPairColorization", e.target.checked)
              }
            />
            Bracket pair colorization
          </CheckboxLabel>

          <CheckboxLabel>
            <Checkbox
              checked={localSettings.renderWhitespace}
              onChange={(e) =>
                handleSettingChange("renderWhitespace", e.target.checked)
              }
            />
            Show whitespace
          </CheckboxLabel>

          <CheckboxLabel>
            <Checkbox
              checked={localSettings.smoothScrolling}
              onChange={(e) =>
                handleSettingChange("smoothScrolling", e.target.checked)
              }
            />
            Smooth scrolling
          </CheckboxLabel>

          <CheckboxLabel>
            <Checkbox
              checked={localSettings.autoSave}
              onChange={(e) =>
                handleSettingChange("autoSave", e.target.checked)
              }
            />
            Auto-save changes
          </CheckboxLabel>

          <CheckboxLabel>
            <Checkbox
              checked={localSettings.formatOnSave}
              onChange={(e) =>
                handleSettingChange("formatOnSave", e.target.checked)
              }
            />
            Format on save
          </CheckboxLabel>

          <CheckboxLabel>
            <Checkbox
              checked={localSettings.vimMode}
              onChange={(e) => handleSettingChange("vimMode", e.target.checked)}
            />
            Vim keybindings (experimental)
          </CheckboxLabel>
        </SettingGroup>
      </SettingsPanel>
    </SettingsOverlay>
  );
};

export default EditorSettingsComponent;
