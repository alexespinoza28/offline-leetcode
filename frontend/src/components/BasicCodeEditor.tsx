import React, { useState, useEffect } from "react";
import styled from "styled-components";

const EditorContainer = styled.div`
  height: 400px;
  width: 100%;
  border: 1px solid #404040;
  background-color: #1a1a1a;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
`;

const EditorHeader = styled.div`
  background-color: #2a2a2a;
  padding: 8px 16px;
  border-bottom: 1px solid #404040;
  font-size: 12px;
  color: #9ca3af;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const LanguageSelect = styled.select`
  background-color: #1a1a1a;
  border: 1px solid #404040;
  color: #e8e8e8;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  margin-right: 12px;

  &:focus {
    outline: none;
    border-color: #ffa116;
  }

  option {
    background-color: #1a1a1a;
    color: #e8e8e8;
  }
`;

const CodeArea = styled.textarea`
  flex: 1;
  background-color: #1a1a1a;
  color: #e8e8e8;
  border: none;
  outline: none;
  padding: 16px;
  font-family: "JetBrains Mono", "Fira Code", "SF Mono", "Consolas", "Monaco",
    monospace;
  font-size: 14px;
  line-height: 1.5;
  resize: none;
  tab-size: 4;

  &::selection {
    background-color: #ffa11640;
  }
`;

const HighlightedCode = styled.pre`
  flex: 1;
  background-color: #1a1a1a;
  color: #e8e8e8;
  border: none;
  outline: none;
  padding: 16px;
  font-family: "JetBrains Mono", "Fira Code", "SF Mono", "Consolas", "Monaco",
    monospace;
  font-size: 14px;
  line-height: 1.5;
  margin: 0;
  overflow: auto;
  white-space: pre-wrap;
  word-wrap: break-word;

  .keyword {
    color: #569cd6;
    font-weight: bold;
  }
  .string {
    color: #ce9178;
  }
  .comment {
    color: #6a9955;
    font-style: italic;
  }
  .number {
    color: #b5cea8;
  }
  .function {
    color: #dcdcaa;
  }
  .operator {
    color: #d4d4d4;
  }
  .builtin {
    color: #4ec9b0;
  }
`;

interface BasicCodeEditorProps {
  language: string;
  value: string;
  onChange: (value: string) => void;
  onLanguageChange?: (language: string) => void;
}

const BasicCodeEditor: React.FC<BasicCodeEditorProps> = ({
  language,
  value,
  onChange,
  onLanguageChange,
}) => {
  const [showHighlighted, setShowHighlighted] = useState(true);

  const languages = [
    { id: "py", name: "Python" },
    { id: "cpp", name: "C++" },
    { id: "c", name: "C" },
    { id: "js", name: "JavaScript" },
    { id: "java", name: "Java" },
  ];

  const getLanguageName = (lang: string): string => {
    const names: { [key: string]: string } = {
      py: "Python",
      cpp: "C++",
      c: "C",
      js: "JavaScript",
      java: "Java",
    };
    return names[lang] || "Python";
  };

  const highlightCode = (code: string, lang: string): string => {
    if (!code) return "";

    let highlighted = code;

    // Python highlighting
    if (lang === "py") {
      // Keywords
      highlighted = highlighted.replace(
        /\b(def|class|if|elif|else|for|while|try|except|finally|import|from|as|return|yield|break|continue|pass|lambda|with|assert|global|nonlocal|and|or|not|in|is|True|False|None)\b/g,
        '<span class="keyword">$1</span>'
      );

      // Built-in functions
      highlighted = highlighted.replace(
        /\b(print|len|range|str|int|float|list|dict|set|tuple|bool|type|isinstance|hasattr|getattr|setattr|enumerate|zip|map|filter|sorted|sum|min|max|abs|round|open|input)\b/g,
        '<span class="builtin">$1</span>'
      );
    }

    // C++ highlighting
    else if (lang === "cpp") {
      highlighted = highlighted.replace(
        /\b(int|float|double|char|bool|void|string|vector|map|set|pair|auto|const|static|public|private|protected|class|struct|namespace|using|include|if|else|for|while|do|switch|case|default|break|continue|return|try|catch|throw|new|delete|this|nullptr)\b/g,
        '<span class="keyword">$1</span>'
      );

      highlighted = highlighted.replace(
        /\b(std|cout|cin|endl|vector|string|map|set|pair|make_pair|push_back|size|begin|end)\b/g,
        '<span class="builtin">$1</span>'
      );
    }

    // JavaScript highlighting
    else if (lang === "js") {
      highlighted = highlighted.replace(
        /\b(function|var|let|const|if|else|for|while|do|switch|case|default|break|continue|return|try|catch|finally|throw|new|this|typeof|instanceof|in|of|class|extends|super|static|async|await|yield|import|export|from|as|default)\b/g,
        '<span class="keyword">$1</span>'
      );

      highlighted = highlighted.replace(
        /\b(console|log|error|warn|Array|Object|String|Number|Boolean|Date|Math|JSON|parseInt|parseFloat|isNaN|setTimeout|setInterval|clearTimeout|clearInterval)\b/g,
        '<span class="builtin">$1</span>'
      );
    }

    // Java highlighting
    else if (lang === "java") {
      highlighted = highlighted.replace(
        /\b(public|private|protected|static|final|abstract|class|interface|extends|implements|import|package|if|else|for|while|do|switch|case|default|break|continue|return|try|catch|finally|throw|throws|new|this|super|int|float|double|char|boolean|byte|short|long|void|String|Object)\b/g,
        '<span class="keyword">$1</span>'
      );

      highlighted = highlighted.replace(
        /\b(System|out|println|print|Scanner|ArrayList|HashMap|HashSet|List|Map|Set|Arrays|Collections|Math|String|Integer|Double|Boolean)\b/g,
        '<span class="builtin">$1</span>'
      );
    }

    // Common patterns for all languages

    // Strings (simple pattern)
    highlighted = highlighted.replace(
      /"([^"\\]|\\.)*"/g,
      '<span class="string">"$1"</span>'
    );
    highlighted = highlighted.replace(
      /'([^'\\]|\\.)*'/g,
      "<span class=\"string\">'$1'</span>"
    );

    // Numbers
    highlighted = highlighted.replace(
      /\b\d+\.?\d*\b/g,
      '<span class="number">$&</span>'
    );

    // Comments
    highlighted = highlighted.replace(
      /\/\/.*$/gm,
      '<span class="comment">$&</span>'
    );
    highlighted = highlighted.replace(
      /#.*$/gm,
      '<span class="comment">$&</span>'
    );
    highlighted = highlighted.replace(
      /\/\*[\s\S]*?\*\//g,
      '<span class="comment">$&</span>'
    );

    // Function calls (simple pattern)
    highlighted = highlighted.replace(
      /\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(/g,
      '<span class="function">$1</span>('
    );

    return highlighted;
  };

  return (
    <EditorContainer>
      <EditorHeader>
        <div style={{ display: "flex", alignItems: "center" }}>
          <span style={{ marginRight: "12px" }}>Language:</span>
          <LanguageSelect
            value={language}
            onChange={(e) => onLanguageChange?.(e.target.value)}
          >
            {languages.map((lang) => (
              <option key={lang.id} value={lang.id}>
                {lang.name}
              </option>
            ))}
          </LanguageSelect>
          <span>{getLanguageName(language)} Editor</span>
        </div>
        <button
          onClick={() => setShowHighlighted(!showHighlighted)}
          style={{
            background: "none",
            border: "1px solid #404040",
            color: "#9ca3af",
            padding: "4px 8px",
            borderRadius: "4px",
            cursor: "pointer",
            fontSize: "11px",
          }}
        >
          {showHighlighted ? "Raw" : "Highlight"}
        </button>
      </EditorHeader>

      {showHighlighted ? (
        <div style={{ position: "relative", flex: 1 }}>
          <HighlightedCode
            dangerouslySetInnerHTML={{
              __html: highlightCode(value, language),
            }}
          />
          <CodeArea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: "transparent",
              color: "transparent",
              caretColor: "#ffa116",
              zIndex: 2,
            }}
            spellCheck={false}
            autoComplete="off"
            autoCorrect="off"
            autoCapitalize="off"
          />
        </div>
      ) : (
        <CodeArea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          spellCheck={false}
          autoComplete="off"
          autoCorrect="off"
          autoCapitalize="off"
        />
      )}
    </EditorContainer>
  );
};

export default BasicCodeEditor;
