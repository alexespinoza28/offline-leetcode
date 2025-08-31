import React, { useRef, useEffect, useState } from "react";
import * as monaco from "monaco-editor";

interface SimpleCodeEditorProps {
  language: string;
  value: string;
  onChange: (value: string) => void;
}

const SimpleCodeEditor: React.FC<SimpleCodeEditorProps> = ({
  language,
  value,
  onChange,
}) => {
  console.log("SimpleCodeEditor component mounted with language:", language);

  const editorRef = useRef<HTMLDivElement>(null);
  const monacoEditorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(
    null
  );
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initEditor = async () => {
      try {
        if (editorRef.current && !monacoEditorRef.current) {
          console.log("Initializing Monaco Editor...");

          // Configure Monaco Environment to disable workers
          (window as any).MonacoEnvironment = {
            getWorker: () => {
              return {
                postMessage: () => {},
                addEventListener: () => {},
                removeEventListener: () => {},
                terminate: () => {},
              };
            },
          };

          // Map language
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

          console.log(
            `Creating editor with language: ${getMonacoLanguage(language)}`
          );

          // Create editor
          monacoEditorRef.current = monaco.editor.create(editorRef.current, {
            value: value,
            language: getMonacoLanguage(language),
            theme: "vs-dark",
            fontSize: 14,
            automaticLayout: true,
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            lineNumbers: "on",
            wordWrap: "off",
          });

          console.log("Monaco Editor created successfully!");

          // Listen for content changes
          monacoEditorRef.current.onDidChangeModelContent(() => {
            const currentValue = monacoEditorRef.current?.getValue() || "";
            onChange(currentValue);
          });

          setLoading(false);
        }
      } catch (err) {
        console.error("Failed to initialize Monaco Editor:", err);
        setError(`Failed to load editor: ${err}`);
        setLoading(false);
      }
    };

    initEditor();

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

        console.log(`Changing language to: ${getMonacoLanguage(language)}`);
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

  if (loading) {
    return (
      <div
        style={{
          height: "400px",
          width: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: "#1a1a1a",
          color: "#e8e8e8",
        }}
      >
        Loading Monaco Editor...
      </div>
    );
  }

  if (error) {
    return (
      <div
        style={{
          height: "400px",
          width: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: "#1a1a1a",
          color: "#ff6b6b",
          flexDirection: "column",
          padding: "20px",
        }}
      >
        <div>Error loading Monaco Editor:</div>
        <div style={{ fontSize: "12px", marginTop: "10px" }}>{error}</div>
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          style={{
            width: "100%",
            height: "300px",
            marginTop: "20px",
            backgroundColor: "#2a2a2a",
            color: "#e8e8e8",
            border: "1px solid #404040",
            padding: "10px",
            fontFamily: "monospace",
          }}
        />
      </div>
    );
  }

  return (
    <div
      ref={editorRef}
      style={{
        height: "400px",
        width: "100%",
        border: "1px solid #404040",
        backgroundColor: "#1a1a1a",
      }}
    />
  );
};

export default SimpleCodeEditor;
