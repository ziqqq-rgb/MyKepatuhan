"use client";

import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { LogOut } from "lucide-react";
import { useUser } from "@stackframe/stack";
import { clearToken } from "@/lib/api";

type NavbarProps = {
  variant?: string;
  userEmail?: string;
  isAdmin?: boolean;
};

export function Navbar({ variant, userEmail, isAdmin }: NavbarProps) {
  const user = useUser();
  const router = useRouter();

  async function handleLogout() {
    clearToken();
    try {
      await user?.signOut();
    } finally {
      router.push("/");
    }
  }

  return (
    <nav className="relative z-10 flex items-center justify-between bg-transparent px-6 py-4">
      <Link href="/" className="flex items-center">
        <Image src="/logo.svg" alt="MyKepatuhan logo" width={28} height={28} priority />
        <span className="text-xl font-bold tracking-tight text-primary">
          MyKepatuhan
        </span>
      </Link>

      <div className="flex items-center gap-4">
        {user ? (
          <>
            <span className="text-sm font-semibold text-primary">
              {userEmail ?? user.primaryEmail}
            </span>
            <button
              onClick={handleLogout}
              className="flex items-center gap-1.5 rounded-lg border border-border px-3 py-1.5 text-sm font-medium text-muted-foreground transition-colors hover:border-destructive/40 hover:text-destructive"
            >
              <LogOut className="h-3.5 w-3.5" strokeWidth={2} />
              Logout
            </button>
          </>
        ) : (
          <>
            <Link
              href="/login"
              className="text-sm font-medium text-muted-foreground hover:text-foreground"
            >
              Log in
            </Link>
            <Link
              href="/register"
              className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
            >
              Sign up
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}