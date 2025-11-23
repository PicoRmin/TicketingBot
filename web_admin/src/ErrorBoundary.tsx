import React, { Component, ErrorInfo, ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: 20,
          background: "var(--bg)",
          color: "var(--fg)"
        }}>
          <div style={{
            maxWidth: 600,
            padding: 24,
            background: "var(--bg-secondary)",
            borderRadius: "var(--radius)",
            border: "1px solid var(--border)"
          }}>
            <h1 style={{ margin: "0 0 16px 0", color: "var(--error)" }}>
              ⚠️ خطا در بارگذاری صفحه
            </h1>
            <p style={{ margin: "0 0 16px 0", color: "var(--fg-secondary)" }}>
              متأسفانه خطایی در بارگذاری صفحه رخ داده است.
            </p>
            {this.state.error && (
              <details style={{
                marginTop: 16,
                padding: 12,
                background: "var(--bg)",
                borderRadius: "var(--radius)",
                fontSize: 12,
                fontFamily: "monospace"
              }}>
                <summary style={{ cursor: "pointer", marginBottom: 8 }}>
                  جزئیات خطا
                </summary>
                <pre style={{ margin: 0, whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
                  {this.state.error.toString()}
                  {this.state.error.stack}
                </pre>
              </details>
            )}
            <button
              onClick={() => {
                this.setState({ hasError: false, error: null });
                window.location.href = "/";
              }}
              style={{
                marginTop: 16,
                padding: "10px 20px",
                background: "var(--primary)",
                color: "white",
                border: "none",
                borderRadius: "var(--radius)",
                cursor: "pointer",
                fontSize: 14
              }}
            >
              🔄 بارگذاری مجدد
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

