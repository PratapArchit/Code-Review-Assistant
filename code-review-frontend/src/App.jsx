import React, { useState } from "react";
import { Upload, Loader2, CheckCircle2, AlertTriangle } from "lucide-react";

const App = () => {
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("python");
  const [loading, setLoading] = useState(false);
  const [review, setReview] = useState(null);
  const [error, setError] = useState(null);

  const handleReview = async () => {
    if (!code.trim()) {
      setError("Please paste or upload some code first!");
      return;
    }
    setError(null);
    setLoading(true);
    setReview(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/review", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, language }),
      });

      if (!response.ok) throw new Error("Backend error");

      const data = await response.json();
      setReview(data);
    } catch (err) {
      setError("Failed to connect to backend. Make sure FastAPI is running!");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center p-6">
      <h1 className="text-3xl font-bold mb-4">⚡ Code Review Assistant</h1>

      <textarea
        className="w-full max-w-3xl h-64 p-3 bg-slate-900 border border-slate-700 rounded-md text-sm font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500"
        placeholder="Paste your code here..."
        value={code}
        onChange={(e) => setCode(e.target.value)}
      />

      <div className="flex gap-3 my-4">
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="bg-slate-800 border border-slate-700 p-2 rounded-md text-sm"
        >
          <option value="python">Python</option>
          <option value="javascript">JavaScript</option>
          <option value="java">Java</option>
          <option value="cpp">C++</option>
        </select>

        <button
          onClick={handleReview}
          disabled={loading}
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 px-4 py-2 rounded-md font-semibold text-sm disabled:opacity-50"
        >
          {loading ? <Loader2 className="animate-spin w-4 h-4" /> : <Upload className="w-4 h-4" />}
          {loading ? "Analyzing..." : "Review Code"}
        </button>
      </div>

      {error && <p className="text-red-400 text-sm mt-2">{error}</p>}

      {review && (
        <div className="w-full max-w-3xl bg-slate-900 border border-slate-700 rounded-md p-5 mt-6">
          <div className="flex justify-between mb-3">
            <h2 className="text-xl font-semibold">Review Report</h2>
            <span className="text-indigo-400 font-bold">Score: {review.score}/100</span>
          </div>

          <p className="text-slate-300 text-sm mb-3">{review.summary}</p>

          <h3 className="font-semibold text-indigo-400 mb-2">Issues</h3>
          <ul className="list-disc pl-5 text-sm text-slate-300 space-y-1">
            {review.issues.map((issue, i) => (
              <li key={i}>
                <span className="font-medium text-red-400">{issue.severity.toUpperCase()}</span>:{" "}
                {issue.message} (Line {issue.line})
              </li>
            ))}
          </ul>

          <h3 className="font-semibold text-indigo-400 mt-4 mb-2">Suggestions</h3>
          <ul className="list-disc pl-5 text-sm text-slate-300 space-y-1">
            {review.suggestions.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default App;
