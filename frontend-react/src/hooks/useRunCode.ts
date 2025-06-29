import { useState, useCallback } from "react";

export function useRunCode() {
  const [loading, setLoading] = useState(false);
  const [output, setOutput] = useState("");
  const [error, setError] = useState<string | null>(null);

  const run = useCallback(async (code: string) => {
    setLoading(true);
    setError(null);
    setOutput("");
    try {
      const res = await fetch("/api/code", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, language: "python", action: "execute" }),
      });
      const data = await res.json();
      setOutput(data.output || data.stdout || data.stderr || "No output.");
    } catch (err: any) {
      setError("⚠️ Error running code.");
      setOutput("⚠️ Error running code.");
    } finally {
      setLoading(false);
    }
  }, []);

  return { run, loading, output, error };
} 