"use client";

import Link from "next/link";
import { useUser } from "@stackframe/stack";

type NavbarProps = {
  variant?: string;
  userEmail?: string;
  isAdmin?: boolean;
};

export function Navbar({ variant, userEmail, isAdmin }: NavbarProps) {
  const user = useUser();

  return (
    <nav className="flex items-center justify-between border-b border-border bg-background px-6 py-4">
      <Link href="/" className="text-xl font-bold tracking-tight text-primary">
        MyKepatuhan
      </Link>
      
      <div className="flex items-center gap-4">
        {user ? (
          <>
            <Link 
              href="/chat" 
              className="text-sm font-medium text-muted-foreground hover:text-foreground"
            >
              Chat
            </Link>
            <Link 
              href="/admin" 
              className="text-sm font-medium text-muted-foreground hover:text-foreground"
            >
              Admin
            </Link>
            <span className="text-sm font-semibold text-primary">
              {user.primaryEmail}
            </span>
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