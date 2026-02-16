"use client";

import dynamic from "next/dynamic";
import { useMemo } from "react";

const MonacoEditor = dynamic(() => import("@monaco-editor/react"), { ssr: false });

type Props = {
  code: string;
  onChange: (value: string) => void;
};

export default function CodeEditor({ code, onChange }: Props) {
  const language = useMemo(() => "python", []);

  return (
    <div className="card">
      <h2>Generated Code</h2>
      <MonacoEditor
        height="420px"
        language={language}
        value={code}
        options={{ minimap: { enabled: false }, fontSize: 14, wordWrap: "on" }}
        onChange={(value) => onChange(value ?? "")}
      />
    </div>
  );
}
