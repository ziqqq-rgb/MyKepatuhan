"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Eye, EyeOff } from "lucide-react";
import { useStackApp } from "@stackframe/stack";
import { useLanguage } from "@/lib/i18n";
import { ErrorBanner } from "@/components/ErrorBanner";
import { apiLogin, setToken, apiGetMe } from "@/lib/api";

export default function LoginPage() {
  const { tr } = useLanguage();
  const router = useRouter();
  const stackApp = useStackApp();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      // 1. Sign in with Neon Auth (Stack Auth) — manages the frontend session
      const result = await stackApp.signInWithCredential({ email, password });
      if (result.status === "error") {
        setError(tr("login_error"));
        return;
      }

      // 2. Exchange for a FastAPI JWT — used for API calls
      const authResponse = await apiLogin(email, password);
      setToken(authResponse.access_token);

      // 3. Check if admin and redirect accordingly
      const me = await apiGetMe();
      router.push(me.is_admin ? "/admin" : "/chat");
    } catch {
      setError(tr("login_error"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="w-full max-w-sm animate-fade-in">
      {/* Card */}
      <div className="rounded-2xl border border-border bg-card p-8 shadow-sm">
        {/* Header */}
        <div className="mb-7 text-center">
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">
            {tr("login_title")}
          </h1>
          <p className="mt-1.5 text-sm text-muted-foreground">{tr("login_sub")}</p>
        </div>

        {error && (
          <div className="mb-5">
            <ErrorBanner message={error} />
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Email */}
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
              className="w-full rounded-lg border border-border bg-background px-3.5 py-2.5 text-sm text-foreground placeholder:text-muted-foreground/60 outline-none transition-colors focus:border-primary focus:ring-2 focus:ring-primary/20"
            />
          </div>

          {/* Password */}
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
                className="w-full rounded-lg border border-border bg-background px-3.5 py-2.5 pr-10 text-sm text-foreground placeholder:text-muted-foreground/60 outline-none transition-colors focus:border-primary focus:ring-2 focus:ring-primary/20"
              />
              <button
                type="button"
                onClick={() => setShowPw((v) => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                tabIndex={-1}
              >
                {showPw ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="mt-1 flex w-full items-center justify-center rounded-xl py-2.5 text-sm font-semibold text-white transition-all hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
            style={{ background: "var(--gradient-primary)" }}
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                Signing in...
              </span>
            ) : (
              tr("login_submit")
            )}
          </button>
        </form>

        {/* Footer */}
        <p className="mt-6 text-center text-sm text-muted-foreground">
          {tr("login_no_account")}{" "}
          <Link href="/register" className="font-medium text-primary hover:underline">
            {tr("login_register_link")}
          </Link>
        </p>
      </div>
    </div>
  );
}
