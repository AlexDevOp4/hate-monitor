import { useEffect, useState } from "react";
import type { FormEvent } from "react";

type Post = {
  id: string;
  platform: string;
  account_handle: string;
  text: string;
  published_at: string;
  url: string;
};

type Analysis = {
  id: number;
  post: string;
  category: string;
  confidence: number;
  reasoning: string;
  requires_review: boolean;
  created_at: string;
};

const PLATFORMS = ["TWITTER", "LINKEDIN", "YOUTUBE", "REDDIT", "OTHER"];

const EMPTY_FORM = {
  platform: "TWITTER",
  platform_post_id: "",
  account_handle: "",
  text: "",
  url: "",
  published_at: "",
};

const CATEGORIES = [
  "NONE",
  "CRITICISM",
  "HOSTILITY",
  "DEHUMANIZATION",
  "HARASSMENT",
  "INCITEMENT",
  "THREAT",
  "HIGH_PRIORITY_THREAT",
];

const EMPTY_ANALYSIS = {
  category: "NONE",
  confidence: "",
  reasoning: "",
  requires_review: false,
};

async function readErrors(response: Response): Promise<string[]> {
  const data = await response.json().catch(() => null);
  if (data && typeof data === "object") {
    return Object.entries(data).map(
      ([field, value]) =>
        `${field}: ${Array.isArray(value) ? value.join(" ") : String(value)}`,
    );
  }
  return [`Request failed (HTTP ${response.status}).`];
}

function App() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loadError, setLoadError] = useState("");
  const [form, setForm] = useState(EMPTY_FORM);
  const [message, setMessage] = useState("");
  const [errors, setErrors] = useState<string[]>([]);
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [analysisPostId, setAnalysisPostId] = useState("");
  const [analysisForm, setAnalysisForm] = useState(EMPTY_ANALYSIS);
  const [analysisMessage, setAnalysisMessage] = useState("");
  const [analysisErrors, setAnalysisErrors] = useState<string[]>([]);

  function loadPosts() {
    fetch("/api/posts/")
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
      })
      .then((data: Post[]) => {
        setPosts(data);
        setLoadError("");
      })
      .catch(() => setLoadError("Could not load posts."));
  }

  function loadAnalyses() {
    fetch("/api/analyses/")
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
      })
      .then((data: Analysis[]) => setAnalyses(data))
      .catch(() => setLoadError("Could not load analyses."));
  }

  useEffect(() => {
    loadPosts();
    loadAnalyses();
  }, []);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setMessage("");
    setErrors([]);

    const payload = {
      ...form,
      published_at: form.published_at
        ? new Date(form.published_at).toISOString()
        : "",
    };

    try {
      const response = await fetch("/api/posts/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (response.ok) {
        setForm(EMPTY_FORM);
        setMessage("Post submitted.");
        loadPosts();
        return;
      }
      setErrors(await readErrors(response));
    } catch {
      setErrors(["Could not reach the server."]);
    }
  }

  function openAnalysis(postId: string) {
    setAnalysisPostId(postId);
    setAnalysisForm(EMPTY_ANALYSIS);
    setAnalysisMessage("");
    setAnalysisErrors([]);
  }

  async function handleAnalysisSubmit(event: FormEvent) {
    event.preventDefault();
    setAnalysisMessage("");
    setAnalysisErrors([]);

    try {
      const response = await fetch("/api/analyses/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ post: analysisPostId, ...analysisForm }),
      });
      if (response.ok) {
        setAnalysisForm(EMPTY_ANALYSIS);
        setAnalysisMessage("Analysis saved.");
        loadAnalyses();
        return;
      }
      setAnalysisErrors(await readErrors(response));
    } catch {
      setAnalysisErrors(["Could not reach the server."]);
    }
  }

  function update(field: keyof typeof EMPTY_FORM, value: string) {
    setForm({ ...form, [field]: value });
  }

  return (
    <main>
      <h1>Monitor</h1>

      <h2>Submit Post</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Platform
          <select
            value={form.platform}
            onChange={(e) => update("platform", e.target.value)}
          >
            {PLATFORMS.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </label>
        <label>
          Platform Post ID
          <input
            value={form.platform_post_id}
            onChange={(e) => update("platform_post_id", e.target.value)}
          />
        </label>
        <label>
          Account Handle
          <input
            value={form.account_handle}
            onChange={(e) => update("account_handle", e.target.value)}
          />
        </label>
        <label>
          Post Text
          <textarea
            value={form.text}
            onChange={(e) => update("text", e.target.value)}
          />
        </label>
        <label>
          URL
          <input
            value={form.url}
            onChange={(e) => update("url", e.target.value)}
          />
        </label>
        <label>
          Published At
          <input
            type="datetime-local"
            value={form.published_at}
            onChange={(e) => update("published_at", e.target.value)}
          />
        </label>
        <button type="submit">Submit</button>
      </form>

      {message && <p className="ok">{message}</p>}
      {errors.length > 0 && (
        <ul className="error" role="alert">
          {errors.map((error) => (
            <li key={error}>{error}</li>
          ))}
        </ul>
      )}

      <h2>Monitored Posts</h2>
      {loadError && (
        <p className="error" role="alert">
          {loadError}
        </p>
      )}
      {!loadError && posts.length === 0 && <p>No monitored posts yet.</p>}
      <ul>
        {posts.map((post) => (
          <li key={post.id}>
            <strong>{post.platform}</strong> @{post.account_handle} ·{" "}
            {new Date(post.published_at).toLocaleString()}
            <p>{post.text}</p>
            <a href={post.url} target="_blank" rel="noreferrer">
              {post.url}
            </a>

            <h3>Analyses</h3>
            {analyses.some((a) => a.post === post.id) ? (
              <ul>
                {analyses
                  .filter((a) => a.post === post.id)
                  .map((a) => (
                    <li key={a.id}>
                      {a.category} · confidence {a.confidence} · review{" "}
                      {a.requires_review ? "required" : "not required"} ·{" "}
                      {new Date(a.created_at).toLocaleString()}
                      {a.reasoning && <p>{a.reasoning}</p>}
                    </li>
                  ))}
              </ul>
            ) : (
              <p>No analysis yet.</p>
            )}

            {analysisPostId === post.id ? (
              <form onSubmit={handleAnalysisSubmit} noValidate>
                <label>
                  Category
                  <select
                    value={analysisForm.category}
                    onChange={(e) =>
                      setAnalysisForm({ ...analysisForm, category: e.target.value })
                    }
                  >
                    {CATEGORIES.map((c) => (
                      <option key={c} value={c}>
                        {c}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Confidence (0–1)
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.01"
                    value={analysisForm.confidence}
                    onChange={(e) =>
                      setAnalysisForm({ ...analysisForm, confidence: e.target.value })
                    }
                  />
                </label>
                <label>
                  Reasoning
                  <textarea
                    value={analysisForm.reasoning}
                    onChange={(e) =>
                      setAnalysisForm({ ...analysisForm, reasoning: e.target.value })
                    }
                  />
                </label>
                <label className="checkbox">
                  <input
                    type="checkbox"
                    checked={analysisForm.requires_review}
                    onChange={(e) =>
                      setAnalysisForm({
                        ...analysisForm,
                        requires_review: e.target.checked,
                      })
                    }
                  />
                  Requires review
                </label>
                <button type="submit">Save analysis</button>
              </form>
            ) : (
              <button type="button" onClick={() => openAnalysis(post.id)}>
                Analyze
              </button>
            )}

            {analysisPostId === post.id && analysisMessage && (
              <p className="ok">{analysisMessage}</p>
            )}
            {analysisPostId === post.id && analysisErrors.length > 0 && (
              <ul className="error" role="alert">
                {analysisErrors.map((error) => (
                  <li key={error}>{error}</li>
                ))}
              </ul>
            )}
          </li>
        ))}
      </ul>
    </main>
  );
}

export default App;
