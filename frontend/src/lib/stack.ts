import { StackClientApp } from "@stackframe/stack";

export const stackApp = new StackClientApp({
  projectId: process.env.NEXT_PUBLIC_STACK_PROJECT_ID!,
  publishableClientKey: process.env.NEXT_PUBLIC_STACK_PUBLISHABLE_KEY!,
  tokenStore: "cookie",
  urls: {
    signIn: "/login",
    signUp: "/register",
    afterSignIn: "/chat",
    afterSignUp: "/chat",
    afterSignOut: "/",
  },
});