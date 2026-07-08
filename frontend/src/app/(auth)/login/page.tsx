"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Eye, EyeOff } from "lucide-react";
import { useStackApp } from "@stackframe/stack";
import { useLanguage } from "@/lib/i18n";
import { ErrorBanner } from "@/components/ErrorBanner";
import { ApiError,apiLogin, setToken } from "@/lib/api";
import { GoogleIcon } from "@/components/icons/GoogleIcon";
import { BreadcrumbJsonLd } from "@/components/seo/BreadcrumbJsonLd";

export default function LoginPage() {
  const { tr } = useLanguage();
  const router = useRouter();
  const stackApp = useStackApp();

  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [showPw, setShowPw]     = useState(false);
  const [loading, setLoading]   = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [error, setError]       = useState<string | null>(null);

  /* ── Google OAuth ── */
  async function handleGoogle() {
    setError(null);
    setGoogleLoading(true);
    try {
      await stackApp.signInWithOAuth("google");
    } catch {
      setError("Google sign-in failed. Please try again.");
      setGoogleLoading(false);
    }
  }

  /* ── Email / password ── */
  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const result = await stackApp.signInWithCredential({ email, password });
      if (result.status === "error") {
        setError(tr("login_error"));
        return;
      }

      const authResponse = await apiLogin(email, password);
      setToken(authResponse.access_token);

      window.location.href = "/chat";
    } catch (err) {
      setError(err instanceof ApiError && err.status === 429 ? tr("error_rate_limited") : tr("login_error"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="w-full max-w-100 animate-fade-in">
      <BreadcrumbJsonLd
        trail={[
          { name: "Home", path: "/" },
          { name: "Login", path: "/login" },
        ]}
      />

      {/* Logo mark */}
      <div className="mb-8 flex flex-col items-center text-center">
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">
          {tr("login_title")}
        </h1>
        <p className="mt-1.5 text-sm text-muted-foreground">{tr("login_sub")}</p>
      </div>

      {/* Card */}
      <div
        className="rounded-2xl border border-border/60 p-6"
        style={{ background: "var(--gradient-card)", boxShadow: "var(--shadow-card)" }}
      >
        {error && <div className="mb-5"><ErrorBanner error={error} /></div>}

        {/* Google button */}
        <button
          onClick={handleGoogle}
          disabled={googleLoading || loading}
          className="flex w-full items-center justify-center gap-3 rounded-xl border border-border bg-secondary/80 px-4 py-2.5 text-sm font-medium text-foreground transition-all hover:bg-secondary hover:border-border/80 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {googleLoading
            ? <span className="h-4 w-4 animate-spin rounded-full border-2 border-border border-t-foreground" />
            : <GoogleIcon />}
          Continue with Google
        </button>

        {/* Divider */}
        <div className="my-5 flex items-center gap-3">
          <div className="h-px flex-1 bg-border" />
          <span className="text-xs text-muted-foreground">or continue with email</span>
          <div className="h-px flex-1 bg-border" />
        </div>

        {/* Email / password form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-foreground">
              {tr("login_email")}
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
              placeholder="you@example.com"
              className="w-full rounded-xl border border-border bg-background/60 px-3.5 py-2.5 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none transition-all focus:border-primary/60 focus:ring-2 focus:ring-primary/15"
            />
          </div>

          <div>
            <label className="mb-1.5 block text-sm font-medium text-foreground">
              {tr("login_password")}
            </label>
            <div className="relative">
              <input
                type={showPw ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
                placeholder="••••••••"
                className="w-full rounded-xl border border-border bg-background/60 px-3.5 py-2.5 pr-10 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none transition-all focus:border-primary/60 focus:ring-2 focus:ring-primary/15"
              />
              <button
                type="button"
                onClick={() => setShowPw((v) => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground transition-colors hover:text-foreground"
                tabIndex={-1}
              >
                {showPw ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading || googleLoading}
            className="flex w-full items-center justify-center rounded-xl py-2.5 text-sm font-semibold text-white transition-all hover:opacity-90 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50"
            style={{ background: "var(--gradient-primary)", boxShadow: "var(--shadow-elegant)" }}
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                Signing in...
              </span>
            ) : tr("login_submit")}
          </button>
        </form>
      </div>

      <p className="mt-5 text-center text-sm text-muted-foreground">
        {tr("login_no_account")}{" "}
        <Link href="/register" className="font-medium text-primary transition-colors hover:text-primary/80">
          {tr("login_register_link")}
        </Link>
      </p>
    </div>
  );
}