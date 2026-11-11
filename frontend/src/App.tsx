import { useEffect, useState } from "react";

type ApiState = "loading" | "connected" | "error";

function App() {
  const [state, setState] = useState<ApiState>("loading");

  useEffect(() => {
    fetch("/api/health/")
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
      })
      .then((data) => setState(data.status === "ok" ? "connected" : "error"))
      .catch(() => setState("error"));
  }, []);

  return (
    <main>
      <h1>Monitor</h1>
      {state === "loading" && <p>API: Checking…</p>}
      {state === "connected" && <p className="ok">API: Connected</p>}
      {state === "error" && (
        <p className="error" role="alert">
          API: Unreachable — could not connect to the backend.
        </p>
      )}
    </main>
  );
}

export default App;
