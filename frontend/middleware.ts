import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

export function middleware(request: NextRequest) {
  // Add the backend API key as a server-side header before proxying to the backend.
  // This keeps the API key out of the browser and client-side code.
  const apiKey = process.env.API_KEY;
  if (!apiKey) {
    return NextResponse.next();
  }

  const headers = new Headers(request.headers);
  headers.set("X-API-Key", apiKey);
  return NextResponse.next({
    request: { headers },
  });
}

export const config = {
  matcher: "/api/v1/:path*",
};
