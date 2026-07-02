"use client";

import { StackHandler } from "@stackframe/stack";
import { stackApp } from "@/lib/stack";

/**
 * Catch-all route Stack Auth uses internally for every auth-related
 * URL (OAuth callbacks, sign-in, sign-up, account settings). Stack
 * decides which screen to render based on the URL segment — this
 * page never needs to know the specifics itself.
 */
export default function Handler(props: any) {
  return <StackHandler fullPage app={stackApp} routeProps={props} />;
}