import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

// Gated areas: the private research zone and the verification submit flow. Everything else is
// public (the verified asset is meant to be seen).
const isProtectedRoute = createRouteMatcher(["/research(.*)", "/submit(.*)", "/api/submissions(.*)"]);

export default clerkMiddleware(async (auth, req) => {
  if (isProtectedRoute(req)) {
    // Clerk v5: `auth` is a function returning the auth object; `.protect()` is on the result.
    await auth().protect();
  }
});

export const config = {
  matcher: [
    // Skip Next internals and static files; run on everything else + API routes.
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpg|jpeg|gif|png|svg|ico|webp|woff2?)).*)",
    "/(api|trpc)(.*)",
  ],
};
