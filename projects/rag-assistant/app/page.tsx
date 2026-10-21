"use client";

import { useState } from "react";

type SearchResult = {
  id: number;
  title: string;
  content: string;
  source: string;
  score: number;
};

export default function Home() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSearch(
    event: React.FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    setLoading(true);
    setError("");
    setResults([]);

    try {
      const response = await fetch("/api/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Search failed");
      }

      setResults(data.results);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-2xl p-8">
      <h1 className="text-3xl font-bold">
        AI Document Assistant
      </h1>

      <p className="mt-2 text-gray-600">
        Search our sample policy documents.
      </p>

      <form onSubmit={handleSearch} className="mt-6 flex gap-2">
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="e.g. refund within 30 days"
          className="min-w-0 flex-1 rounded border p-3"
          required
        />

        <button
          type="submit"
          disabled={loading}
          className="rounded bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {error && (
        <p className="mt-4 text-red-600">{error}</p>
      )}

      <section className="mt-8 space-y-4">
        {results.map((result) => (
          <article
            key={result.id}
            className="rounded-lg border p-4"
          >
            <h2 className="text-lg font-semibold">
              {result.title}
            </h2>

            <p className="mt-2">{result.content}</p>

            <p className="mt-3 text-sm text-gray-500">
              Source: {result.source} · Match score: {result.score}
            </p>
          </article>
        ))}

        {!loading && !error && results.length === 0 && (
          <p className="text-gray-500">
            No results yet. Try searching for a policy.
          </p>
        )}
      </section>
    </main>
  );
}