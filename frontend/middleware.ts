import { NextResponse, type NextRequest } from "next/server";

const protectedRoutes = ["/dashboard", "/subscriptions", "/resources", "/settings"];

export function middleware(request: NextRequest) {
  const session = request.cookies.get(process.env.NEXT_PUBLIC_SESSION_COOKIE ?? "azinv_session");
  const isProtected = protectedRoutes.some((path) => request.nextUrl.pathname.startsWith(path));
  if (isProtected && !session) {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/subscriptions/:path*", "/resources/:path*", "/settings/:path*"]
};

