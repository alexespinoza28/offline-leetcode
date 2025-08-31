// Type definitions for the interview coding platform

export interface Problem {
  slug: string;
  title: string;
  difficulty: "Easy" | "Medium" | "Hard";
  tags: string[];
  statement_md: string;
  examples: Example[];
  constraints: Constraint[];
}

export interface Example {
  in: string;
  out: string;
}

export interface Constraint {
  name: string;
  min?: number;
  max?: number;
  value?: string;
  desc: string;
}

export interface RunRequest {
  action: "run" | "explain" | "gen-tests";
  problem: string;
  lang: string;
  code: string;
  tests?: "sample" | "unit" | "all";
}

export interface TestCase {
  id: string;
  status: "OK" | "WA" | "TLE" | "MLE" | "RE" | "CE";
  time_ms?: number;
  memory_mb?: number;
  input?: string;
  expected?: string;
  actual?: string;
  diff?: string;
}

export interface TestSummary {
  passed: number;
  failed: number;
  total: number;
  time_ms: number;
  memory_mb: number;
}

export interface RunResult {
  status:
    | "OK"
    | "COMPILE_ERROR"
    | "RUNTIME_ERROR"
    | "TIMEOUT"
    | "MLE"
    | "WA"
    | "ERROR";
  summary?: TestSummary | null;
  cases?: TestCase[] | null;
  logs?: {
    compile?: string;
    stderr?: string;
  } | null;
  explanation?: string | null;
}

export interface SolutionResponse {
  code: string;
}

export type Language = "py" | "cpp" | "c" | "js" | "java";

export interface LanguageConfig {
  id: Language;
  name: string;
  extension: string;
  monacoId: string;
}

export const LANGUAGES: LanguageConfig[] = [
  { id: "py", name: "Python 3", extension: "py", monacoId: "python" },
  { id: "cpp", name: "C++", extension: "cpp", monacoId: "cpp" },
  { id: "c", name: "C", extension: "c", monacoId: "c" },
  { id: "js", name: "JavaScript", extension: "js", monacoId: "javascript" },
  { id: "java", name: "Java", extension: "java", monacoId: "java" },
];

export const DIFFICULTY_COLORS = {
  Easy: "#4caf50",
  Medium: "#ff9800",
  Hard: "#f44336",
};

export const STATUS_COLORS = {
  OK: "#4caf50",
  WA: "#f44336",
  TLE: "#ff9800",
  MLE: "#ff9800",
  RE: "#f44336",
  CE: "#f44336",
  ERROR: "#f44336",
};

export const STATUS_LABELS = {
  OK: "Accepted",
  WA: "Wrong Answer",
  TLE: "Time Limit Exceeded",
  MLE: "Memory Limit Exceeded",
  RE: "Runtime Error",
  CE: "Compilation Error",
  ERROR: "System Error",
};

export interface ConnectionStatus {
  connected: boolean;
  latency: number | null;
  error: string | null;
  lastPing: Date | null;
}

export interface EditorSettings {
  theme: "light" | "dark";
  fontSize: number;
  tabSize: number;
  wordWrap: boolean;
  showLineNumbers: boolean;
  autoComplete: boolean;
}

export interface SettingsPanelProps {
  settings: EditorSettings;
  onSettingsChange: (settings: Partial<EditorSettings>) => void;
  languages: LanguageConfig[];
  currentLanguage: string;
  onLanguageChange: (language: string) => void;
}
