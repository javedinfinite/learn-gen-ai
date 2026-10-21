import { NextResponse } from "next/server";

export async function POST(request: Request) {
  try {
    const body = await request.json();

    if (
      typeof body.query !== "string" ||
      !body.query.trim()
    ) {
      return NextResponse.json(
        { error: "A search query is required" },
        { status: 400 }
      );
    }

    const response = await fetch(
      "http://127.0.0.1:8000/search",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: body.query,
        }),
        cache: "no-store",
      }
    );

    if (!response.ok) {
      return NextResponse.json(
        { error: "Python search service failed" },
        { status: 502 }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch {
    return NextResponse.json(
      { error: "Unable to reach the Python service" },
      { status: 503 }
    );
  }
}