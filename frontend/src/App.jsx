import { useEffect, useState } from "react";

function App() {
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);

  const loadTrends = () => {
    setLoading(true);
    setError("");

    fetch("http://127.0.0.1:8000/trends/top")
      .then((response) => {
        if (!response.ok) {
          throw new Error("API request failed");
        }

        return response.json();
      })
      .then((data) => {
        setTrends(data.trends || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError("Could not connect to the API.");
        setLoading(false);
      });
  };

  const analyzeVideo = (videoId) => {
    setAnalysisLoading(true);
    setAnalysis(null);

    fetch(`http://127.0.0.1:8000/trends/${videoId}/analysis`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Analysis request failed");
        }

        return response.json();
      })
      .then((data) => {
        setAnalysis(data);
        setAnalysisLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setAnalysisLoading(false);
        setAnalysis({
          error: "Could not generate AI analysis.",
        });
      });
  };

  useEffect(() => {
    loadTrends();
  }, []);

  const totalViews = trends.reduce(
    (sum, video) => sum + Number(video.views || 0),
    0
  );

  const explodingCount = trends.filter(
    (video) => video.trend_status === "EXPLODING"
  ).length;

  const averageVelocity =
    trends.length > 0
      ? trends.reduce(
          (sum, video) => sum + Number(video.velocity_score || 0),
          0
        ) / trends.length
      : 0;

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#111",
        color: "#eee",
        padding: "40px",
        fontFamily: "Arial, sans-serif",
      }}
    >
      {/* Header */}

      <div style={{ maxWidth: "1400px", margin: "0 auto" }}>
        <h1
          style={{
            fontSize: "42px",
            marginBottom: "8px",
          }}
        >
          🔥 YouTube Trend Intelligence
        </h1>

        <p
          style={{
            color: "#aaa",
            fontSize: "18px",
          }}
        >
          AI-powered YouTube trend analysis
        </p>

        <button
          onClick={loadTrends}
          style={{
            marginTop: "15px",
            padding: "10px 18px",
            borderRadius: "8px",
            border: "none",
            cursor: "pointer",
          }}
        >
          🔄 Refresh Trends
        </button>

        {/* Dashboard Cards */}

        {!loading && !error && (
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(4, 1fr)",
              gap: "20px",
              marginTop: "35px",
              marginBottom: "35px",
            }}
          >
            <div style={cardStyle}>
              <div style={cardTitleStyle}>🔥 TOP TRENDS</div>

              <div style={cardValueStyle}>{trends.length}</div>
            </div>

            <div style={cardStyle}>
              <div style={cardTitleStyle}>📈 EXPLODING</div>

              <div style={cardValueStyle}>{explodingCount}</div>
            </div>

            <div style={cardStyle}>
              <div style={cardTitleStyle}>👁 TOTAL VIEWS</div>

              <div style={cardValueStyle}>
                {totalViews.toLocaleString()}
              </div>
            </div>

            <div style={cardStyle}>
              <div style={cardTitleStyle}>⚡ AVG VELOCITY</div>

              <div style={cardValueStyle}>
                {averageVelocity.toFixed(0)}
              </div>
            </div>
          </div>
        )}

        {/* Loading */}

        {loading && <p>Loading trends...</p>}

        {/* Error */}

        {error && (
          <div
            style={{
              marginTop: "30px",
              padding: "20px",
              border: "1px solid #733",
              borderRadius: "10px",
            }}
          >
            ❌ {error}
          </div>
        )}

        {/* Trend Table */}

        {!loading && !error && (
          <div
            style={{
              overflowX: "auto",
              marginTop: "30px",
            }}
          >
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
              }}
            >
              <thead>
                <tr>
                  <th style={headerStyle}>Rank</th>
                  <th style={headerStyle}>Title</th>
                  <th style={headerStyle}>Channel</th>
                  <th style={headerStyle}>Views</th>
                  <th style={headerStyle}>Likes</th>
                  <th style={headerStyle}>Comments</th>
                  <th style={headerStyle}>Velocity</th>
                  <th style={headerStyle}>Status</th>
                  <th style={headerStyle}>Actions</th>
                </tr>
              </thead>

              <tbody>
                {trends.map((video) => (
                  <tr key={video.video_id}>
                    <td style={cellStyle}>
                      {video.velocity_rank}
                    </td>

                    <td style={cellStyle}>
                      {video.title}
                    </td>

                    <td style={cellStyle}>
                      {video.channel}
                    </td>

                    <td style={cellStyle}>
                      {Number(video.views).toLocaleString()}
                    </td>

                    <td style={cellStyle}>
                      {Number(video.likes).toLocaleString()}
                    </td>

                    <td style={cellStyle}>
                      {Number(video.comments).toLocaleString()}
                    </td>

                    <td style={cellStyle}>
                      {Number(video.velocity_score).toFixed(2)}
                    </td>

                    <td style={cellStyle}>
                      <span
                        style={{
                          padding: "6px 10px",
                          borderRadius: "20px",
                          background:
                            video.trend_status === "EXPLODING"
                              ? "#5a1a1a"
                              : "#222",
                        }}
                      >
                        {video.trend_status === "EXPLODING"
                          ? "🔥 EXPLODING"
                          : video.trend_status}
                      </span>
                    </td>

                    <td style={cellStyle}>
                      <button
                        onClick={() =>
                          window.open(
                            `https://www.youtube.com/watch?v=${video.video_id}`,
                            "_blank"
                          )
                        }
                        style={actionButtonStyle}
                      >
                        ▶ Watch
                      </button>

                      <button
                        onClick={() =>
                          analyzeVideo(video.video_id)
                        }
                        style={actionButtonStyle}
                      >
                        🤖 Analyze
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* AI Analysis */}

        {analysisLoading && (
          <div style={analysisBoxStyle}>
            <h2>🤖 AI Trend Analysis</h2>

            <p>Gemini is analyzing this trend...</p>
          </div>
        )}

        {analysis && !analysisLoading && (
          <div style={analysisBoxStyle}>
            <h2>🤖 AI Trend Analysis</h2>

            {analysis.error ? (
              <p>{analysis.error}</p>
            ) : (
              <>
                <h3>{analysis.title}</h3>

                <div
                  style={{
                    whiteSpace: "pre-wrap",
                    lineHeight: "1.8",
                    color: "#ccc",
                  }}
                >
                  {analysis.analysis}
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

const cardStyle = {
  background: "#1b1b1b",
  border: "1px solid #333",
  borderRadius: "12px",
  padding: "22px",
};

const cardTitleStyle = {
  color: "#999",
  fontSize: "14px",
};

const cardValueStyle = {
  fontSize: "30px",
  fontWeight: "bold",
  marginTop: "10px",
};

const headerStyle = {
  textAlign: "left",
  padding: "14px",
  borderBottom: "2px solid #444",
};

const cellStyle = {
  padding: "14px",
  borderBottom: "1px solid #333",
};

const actionButtonStyle = {
  marginRight: "8px",
  marginBottom: "5px",
  padding: "8px 12px",
  border: "none",
  borderRadius: "7px",
  cursor: "pointer",
};

const analysisBoxStyle = {
  marginTop: "40px",
  padding: "30px",
  border: "1px solid #555",
  borderRadius: "12px",
  background: "#171717",
};

export default App;