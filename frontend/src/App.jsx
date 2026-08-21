import { useEffect, useState } from "react";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";
const ANALYSIS_SECTIONS = [
  "1. Main Topic",
  "2. Why It Is Trending",
  "3. Audience Signal",
  "4. Trend Strength",
  "5. Trend Risk",
  "6. Future Outlook",
  "7. One-Sentence Summary",
];

async function fetchJson(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) throw new Error(`Request failed with status ${response.status}`);
  return response.json();
}

function formatNumber(value, maximumFractionDigits = 0) {
  return Number(value || 0).toLocaleString(undefined, { maximumFractionDigits });
}

function parseAnalysis(text) {
  if (!text) return [];
  return text.split(/(?=^\d+\. .+$)/m).map((section) => section.trim()).filter(Boolean).map((section) => {
    const lineBreak = section.indexOf("\n");
    return { heading: lineBreak === -1 ? section : section.slice(0, lineBreak), body: lineBreak === -1 ? "" : section.slice(lineBreak + 1).trim() };
  });
}

function StatusBadge({ status }) {
  return <span className={`status-badge status-${String(status || "").toLowerCase()}`}>{status || "UNKNOWN"}</span>;
}

function StatCard({ label, value, accent }) {
  return <article className={`stat-card stat-${accent}`}><span className="stat-label">{label}</span><strong className="stat-value">{value}</strong></article>;
}

function App() {
  const [trends, setTrends] = useState([]);
  const [summary, setSummary] = useState(null);
  const [dashboardLoading, setDashboardLoading] = useState(true);
  const [summaryLoading, setSummaryLoading] = useState(true);
  const [trendsLoading, setTrendsLoading] = useState(true);
  const [dashboardError, setDashboardError] = useState("");
  const [connection, setConnection] = useState("checking");
  const [analysis, setAnalysis] = useState(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);

  const loadDashboard = async () => {
    setDashboardLoading(true);
    setSummaryLoading(true);
    setTrendsLoading(true);
    setDashboardError("");
    const [summaryResult, trendsResult] = await Promise.allSettled([fetchJson("/trends/summary"), fetchJson("/trends/emerging")]);
    const summarySucceeded = summaryResult.status === "fulfilled";
    const trendsSucceeded = trendsResult.status === "fulfilled";
    setConnection(summarySucceeded && trendsSucceeded ? "online" : "offline");
    setSummary(summarySucceeded ? summaryResult.value : null);
    setTrends(trendsSucceeded ? trendsResult.value || [] : []);
    if (!summarySucceeded && !trendsSucceeded) setDashboardError("The intelligence API is unavailable. Refresh to try again.");
    else if (!summarySucceeded || !trendsSucceeded) setDashboardError("Some trend data could not be loaded. Refresh to retry.");
    setSummaryLoading(false);
    setTrendsLoading(false);
    setDashboardLoading(false);
  };

  const analyzeVideo = async (videoId) => {
    setAnalysisLoading(true);
    setAnalysis(null);
    try {
      setAnalysis(await fetchJson(`/trends/${encodeURIComponent(videoId)}/analysis`));
    } catch (error) {
      console.error(error);
      setAnalysis({ error: "AI analysis is temporarily unavailable." });
    } finally {
      setAnalysisLoading(false);
    }
  };

  useEffect(() => { loadDashboard(); }, []);

  const statusCounts = summary?.status_counts || {};
  const topCategory = summary?.top_categories?.[0]?.category || "No data";
  const parsedAnalysis = parseAnalysis(analysis?.analysis);

  return (
    <main className="app-shell">
      <div className="dashboard-wrap">
        <header className="dashboard-header">
          <div><p className="eyebrow">SIGNAL DESK / LIVE MONITOR</p><h1>YouTube Trend Intelligence</h1><p className="subtitle">AI-powered real-time trend intelligence</p></div>
          <div className="header-actions">
            <span className={`connection-status connection-${connection}`}><span className="connection-dot" />{connection === "checking" ? "Checking API" : connection === "online" ? "API connected" : "API unavailable"}</span>
            <button className="button button-primary" onClick={loadDashboard} disabled={dashboardLoading}><span aria-hidden="true">↻</span> {dashboardLoading ? "Refreshing..." : "Refresh"}</button>
          </div>
        </header>

        {dashboardError && <div className="error-banner" role="alert"><span>{dashboardError}</span><button className="button button-quiet" onClick={loadDashboard}>Retry</button></div>}

        <section className="stats-grid" aria-label="Trend summary">
          <StatCard label="Total videos" value={summaryLoading ? "..." : formatNumber(summary?.total_videos)} accent="cyan" />
          <StatCard label="Average strength" value={summaryLoading ? "..." : `${Number(summary?.average_trend_strength || 0).toFixed(1)} / 100`} accent="amber" />
          <StatCard label="Top category" value={summaryLoading ? "..." : topCategory} accent="violet" />
          <StatCard label="Exploding trends" value={summaryLoading ? "..." : formatNumber(statusCounts.EXPLODING)} accent="red" />
          <StatCard label="Growing trends" value={summaryLoading ? "..." : formatNumber(statusCounts.GROWING)} accent="green" />
          <StatCard label="Declining trends" value={summaryLoading ? "..." : formatNumber(statusCounts.DECLINING)} accent="slate" />
        </section>

        <section className="workspace-section">
          <div className="section-heading"><div><p className="eyebrow">EMERGING SIGNALS</p><h2>Trending videos</h2></div><span className="result-count">{trendsLoading ? "Loading signals" : `${trends.length} ranked signals`}</span></div>
          {trendsLoading ? <div className="loading-panel"><span className="loading-bar" /> Loading emerging trends...</div> : trends.length === 0 ? <div className="empty-panel">No emerging trends are available right now.</div> : (
            <div className="table-frame"><table className="trend-table"><thead><tr><th>Rank</th><th>Video title</th><th>Channel</th><th>Category</th><th>Views</th><th>Likes</th><th>Comments</th><th>Velocity score</th><th>Strength</th><th>Status</th><th>Actions</th></tr></thead><tbody>
              {trends.map((video) => { const watchUrl = video.video_url || video.url; return <tr key={video.video_id}><td className="rank-cell">{video.rank}</td><td className="title-cell" title={video.title}>{video.title}</td><td>{video.channel}</td><td><span className="category-label">{video.category}</span></td><td>{formatNumber(video.views)}</td><td>{formatNumber(video.likes)}</td><td>{formatNumber(video.comments)}</td><td>{formatNumber(video.velocity_score, 2)}</td><td><strong className="strength-value">{Number(video.trend_strength || 0).toFixed(2)}</strong></td><td><StatusBadge status={video.trend_status} /></td><td className="action-cell"><button className="button button-watch" onClick={() => watchUrl && window.open(watchUrl, "_blank", "noopener,noreferrer")} disabled={!watchUrl} title={watchUrl ? "Open video" : "No video URL available from the API"}>Watch</button><button className="button button-analyze" onClick={() => analyzeVideo(video.video_id)}>Analyze</button></td></tr>; })}
            </tbody></table></div>
          )}
        </section>

        {analysisLoading && <section className="analysis-panel" aria-live="polite"><div className="analysis-heading"><span className="ai-mark">AI</span><div><p className="eyebrow">GEMINI INSIGHT</p><h2>AI Trend Analysis</h2></div></div><div className="analysis-loading">Analyzing trend<span className="loading-dots">...</span></div></section>}
        {analysis && !analysisLoading && <section className="analysis-panel" aria-live="polite"><div className="analysis-heading"><span className="ai-mark">AI</span><div><p className="eyebrow">GEMINI INSIGHT</p><h2>AI Trend Analysis</h2><p className="analysis-title">{analysis.title}</p></div><button className="close-button" onClick={() => setAnalysis(null)} aria-label="Close analysis">×</button></div>{analysis.error ? <div className="analysis-error">{analysis.error}</div> : <div className="analysis-grid">{ANALYSIS_SECTIONS.map((heading) => { const section = parsedAnalysis.find((item) => item.heading === heading); return <article className="analysis-item" key={heading}><h3>{heading.replace(/^\d+\. /, "")}</h3><p>{section?.body || "Insufficient data to determine."}</p></article>; })}</div>}</section>}
      </div>
    </main>
  );
}

export default App;