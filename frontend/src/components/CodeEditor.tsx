import React, { useRef, useEffect } from "react";
import * as monaco from "monaco-editor";
import styled from "styled-components";

const EditorContainer = styled.div`
  flex: 1;
  position: relative;
  background-color: #1a1a1a;
  border-radius: 0 0 12px 12px;
  overflow: hidden;
`;

interface CodeEditorProps {
  language: string;
  value: string;
  onChange: (value: string) => void;
}

const CodeEditor: React.FC<CodeEditorProps> = ({
  language,
  value,
  onChange,
}) => {
  const editorRef = useRef<HTMLDivElement>(null);
  const monacoEditorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(
    null
  );

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

  return <EditorContainer ref={editorRef} />;
};

export default CodeEditor;
