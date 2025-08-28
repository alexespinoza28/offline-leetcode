import React, { useRef, useEffect, useState } from "react";
import * as monaco from "monaco-editor";
import styled from "styled-components";

const EditorContainer = styled.div`
  flex: 1;
  position: relative;
  background-color: #1a1a1a;
  border-radius: 0 0 12px 12px;
  overflow: hidden;
`;

const EditorToolbar = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  background-color: #1e1e1e;
  border-bottom: 1px solid #404040;
  font-size: 12px;
  color: #9ca3af;
`;

const ToolbarLeft = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const ToolbarRight = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ToolbarButton = styled.button`
  background: none;
  border: none;
  color: #9ca3af;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    color: #e8e8e8;
    background-color: rgba(255, 255, 255, 0.05);
  }

  &:active {
    background-color: rgba(255, 255, 255, 0.1);
  }
`;

const StatusIndicator = styled.span<{ active?: boolean }>`
  color: ${(props) => (props.active ? "#ffa116" : "#6b7280")};
  font-weight: ${(props) => (props.active ? "600" : "400")};
`;

interface CodeEditorProps {
  language: string;
  value: string;
  onChange: (value: string) => void;
  onFormat?: () => void;
  onSave?: () => void;
}

const CodeEditor: React.FC<CodeEditorProps> = ({
  language,
  value,
  onChange,
  onFormat,
  onSave,
}) => {
  const editorRef = useRef<HTMLDivElement>(null);
  const monacoEditorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(
    null
  );
  const [cursorPosition, setCursorPosition] = useState({ line: 1, column: 1 });
  const [isVimMode, setIsVimMode] = useState(false);
  const [wordWrap, setWordWrap] = useState(false);

  // Map our language IDs to Monaco language IDs
  const getMonacoLanguage = (lang: string): string => {
    const languageMap: { [key: string]: string } = {
      py: "python",
      cpp: "cpp",
      c: "c",
      js: "javascript",
      java: "java",
    };
    return languageMap[lang] || "python";
  };

  // Setup language-specific snippets and completions
  const setupLanguageFeatures = (lang: string) => {
    const monacoLang = getMonacoLanguage(lang);

    // Register completion provider for common patterns
    monaco.languages.registerCompletionItemProvider(monacoLang, {
      provideCompletionItems: (model, position) => {
        const suggestions: monaco.languages.CompletionItem[] = [];

        // Language-specific snippets
        if (lang === "py") {
          suggestions.push(
            {
              label: "def",
              kind: monaco.languages.CompletionItemKind.Snippet,
              insertText: "def ${1:function_name}(${2:args}):\n    ${3:pass}",
              insertTextRules:
                monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: "Function definition",
            },
            {
              label: "class",
              kind: monaco.languages.CompletionItemKind.Snippet,
              insertText:
                "class ${1:ClassName}:\n    def __init__(self${2:, args}):\n        ${3:pass}",
              insertTextRules:
                monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: "Class definition",
            },
            {
              label: "for",
              kind: monaco.languages.CompletionItemKind.Snippet,
              insertText: "for ${1:item} in ${2:iterable}:\n    ${3:pass}",
              insertTextRules:
                monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: "For loop",
            }
          );
        } else if (lang === "cpp" || lang === "c") {
          suggestions.push(
            {
              label: "for",
              kind: monaco.languages.CompletionItemKind.Snippet,
              insertText:
                "for (${1:int i = 0}; ${2:i < n}; ${3:i++}) {\n    ${4:// code}\n}",
              insertTextRules:
                monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: "For loop",
            },
            {
              label: "while",
              kind: monaco.languages.CompletionItemKind.Snippet,
              insertText: "while (${1:condition}) {\n    ${2:// code}\n}",
              insertTextRules:
                monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: "While loop",
            },
            {
              label: "if",
              kind: monaco.languages.CompletionItemKind.Snippet,
              insertText: "if (${1:condition}) {\n    ${2:// code}\n}",
              insertTextRules:
                monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: "If statement",
            }
          );
        } else if (lang === "js") {
          suggestions.push(
            {
              label: "function",
              kind: monaco.languages.CompletionItemKind.Snippet,
              insertText:
                "function ${1:name}(${2:params}) {\n    ${3:// code}\n}",
              insertTextRules:
                monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: "Function declaration",
            },
            {
              label: "arrow",
              kind: monaco.languages.CompletionItemKind.Snippet,
              insertText:
                "const ${1:name} = (${2:params}) => {\n    ${3:// code}\n};",
              insertTextRules:
                monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: "Arrow function",
            }
          );
        } else if (lang === "java") {
          suggestions.push(
            {
              label: "method",
              kind: monaco.languages.CompletionItemKind.Snippet,
              insertText:
                "public ${1:void} ${2:methodName}(${3:params}) {\n    ${4:// code}\n}",
              insertTextRules:
                monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: "Method declaration",
            },
            {
              label: "for",
              kind: monaco.languages.CompletionItemKind.Snippet,
              insertText:
                "for (${1:int i = 0}; ${2:i < length}; ${3:i++}) {\n    ${4:// code}\n}",
              insertTextRules:
                monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: "For loop",
            }
          );
        }

        return { suggestions };
      },
    });
  };

  // Format code
  const formatCode = async () => {
    if (monacoEditorRef.current) {
      await monacoEditorRef.current
        .getAction("editor.action.formatDocument")
        ?.run();
      onFormat?.();
    }
  };

  // Toggle word wrap
  const toggleWordWrap = () => {
    if (monacoEditorRef.current) {
      const newWrap = !wordWrap;
      setWordWrap(newWrap);
      monacoEditorRef.current.updateOptions({
        wordWrap: newWrap ? "on" : "off",
      });
    }
  };

  // Toggle vim mode (placeholder for future vim keybindings)
  const toggleVimMode = () => {
    setIsVimMode(!isVimMode);
    // TODO: Implement vim keybindings
    console.log("Vim mode:", !isVimMode ? "enabled" : "disabled");
  };

  useEffect(() => {
    if (editorRef.current && !monacoEditorRef.current) {
      // Configure Monaco Editor theme to match LeetCode
      monaco.editor.defineTheme("leetcode-dark", {
        base: "vs-dark",
        inherit: true,
        rules: [
          { token: "comment", foreground: "6a9955", fontStyle: "italic" },
          { token: "keyword", foreground: "569cd6", fontStyle: "bold" },
          { token: "string", foreground: "ce9178" },
          { token: "number", foreground: "b5cea8" },
          { token: "type", foreground: "4ec9b0" },
          { token: "function", foreground: "dcdcaa" },
        ],
        colors: {
          "editor.background": "#1a1a1a",
          "editor.foreground": "#e8e8e8",
          "editorLineNumber.foreground": "#6b7280",
          "editorLineNumber.activeForeground": "#ffa116",
          "editor.lineHighlightBackground": "#2a2a2a40",
          "editor.selectionBackground": "#ffa11640",
          "editor.inactiveSelectionBackground": "#3a3d4150",
          "editorCursor.foreground": "#ffa116",
          "editor.findMatchBackground": "#ffa11660",
          "editor.findMatchHighlightBackground": "#ffa11630",
          "editorBracketMatch.background": "#ffa11640",
          "editorBracketMatch.border": "#ffa116",
        },
      });

      // Create the editor with LeetCode-style configuration
      monacoEditorRef.current = monaco.editor.create(editorRef.current, {
        value: value,
        language: getMonacoLanguage(language),
        theme: "leetcode-dark",
        fontSize: 14,
        fontFamily:
          "'JetBrains Mono', 'Fira Code', 'SF Mono', 'Consolas', 'Monaco', monospace",
        lineNumbers: "on",
        lineNumbersMinChars: 3,
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        automaticLayout: true,
        tabSize: 4,
        insertSpaces: true,
        wordWrap: "off",
        bracketPairColorization: { enabled: true },
        cursorBlinking: "smooth",
        cursorSmoothCaretAnimation: "on",
        smoothScrolling: true,
        renderLineHighlight: "line",
        renderWhitespace: "selection",
        folding: true,
        foldingHighlight: true,
        showFoldingControls: "mouseover",
        suggest: {
          showKeywords: true,
          showSnippets: true,
          showFunctions: true,
          showConstructors: true,
          showFields: true,
          showVariables: true,
          showClasses: true,
          showStructs: true,
          showInterfaces: true,
          showModules: true,
          showProperties: true,
          showEvents: true,
          showOperators: true,
          showUnits: true,
          showValues: true,
          showConstants: true,
          showEnums: true,
          showEnumMembers: true,
          showColors: true,
          showFiles: true,
          showReferences: true,
          showFolders: true,
          showTypeParameters: true,
        },
        quickSuggestions: {
          other: true,
          comments: false,
          strings: false,
        },
        parameterHints: {
          enabled: true,
          cycle: true,
        },
        acceptSuggestionOnCommitCharacter: true,
        acceptSuggestionOnEnter: "on",
        accessibilitySupport: "auto",
      });

      // Listen for content changes
      monacoEditorRef.current.onDidChangeModelContent(() => {
        const currentValue = monacoEditorRef.current?.getValue() || "";
        onChange(currentValue);
      });

      // Listen for cursor position changes
      monacoEditorRef.current.onDidChangeCursorPosition((e) => {
        setCursorPosition({
          line: e.position.lineNumber,
          column: e.position.column,
        });
      });

      // Add custom keyboard shortcuts
      monacoEditorRef.current.addCommand(
        monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS,
        () => {
          onSave?.();
        }
      );

      monacoEditorRef.current.addCommand(
        monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyF,
        () => {
          formatCode();
        }
      );

      // Setup language features
      setupLanguageFeatures(language);
    }

    return () => {
      if (monacoEditorRef.current) {
        monacoEditorRef.current.dispose();
        monacoEditorRef.current = null;
      }
    };
  }, []);

  // Update language when it changes
  useEffect(() => {
    if (monacoEditorRef.current) {
      const model = monacoEditorRef.current.getModel();
      if (model) {
        monaco.editor.setModelLanguage(model, getMonacoLanguage(language));
        setupLanguageFeatures(language);
      }
    }
  }, [language]);

  // Update value when it changes externally
  useEffect(() => {
    if (
      monacoEditorRef.current &&
      monacoEditorRef.current.getValue() !== value
    ) {
      monacoEditorRef.current.setValue(value);
    }
  }, [value]);

  return (
    <EditorContainer>
      <EditorToolbar>
        <ToolbarLeft>
          <span>
            Ln {cursorPosition.line}, Col {cursorPosition.column}
          </span>
          <span>•</span>
          <span>{getMonacoLanguage(language).toUpperCase()}</span>
        </ToolbarLeft>
        <ToolbarRight>
          <ToolbarButton onClick={toggleWordWrap} title="Toggle Word Wrap">
            <StatusIndicator active={wordWrap}>Wrap</StatusIndicator>
          </ToolbarButton>
          <ToolbarButton onClick={toggleVimMode} title="Toggle Vim Mode">
            <StatusIndicator active={isVimMode}>Vim</StatusIndicator>
          </ToolbarButton>
          <ToolbarButton
            onClick={formatCode}
            title="Format Code (Ctrl+Shift+F)"
          >
            Format
          </ToolbarButton>
        </ToolbarRight>
      </EditorToolbar>
      <div ref={editorRef} style={{ flex: 1 }} />
    </EditorContainer>
  );
};

export default CodeEditor;
