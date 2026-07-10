import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

// The private area. Everything else is public (the verified asset is meant to be seen).
const isProtectedRoute = createRouteMatcher(["/research(.*)"]);

export default clerkMiddleware(async (auth, req) => {
  if (isProtectedRoute(req)) {
    await auth.protect();
  }
});

export const config = {
  matcher: [
    // Skip Next internals and static files; run on everything else + API routes.
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpg|jpeg|gif|png|svg|ico|webp|woff2?)).*)",
    "/(api|trpc)(.*)",
  ],
};
