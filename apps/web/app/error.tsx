"use client";

export default function Error({
  reset
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main className="grid min-h-screen place-items-center px-6">
      <div className="max-w-md text-center">
        <p className="text-xs font-bold tracking-[0.2em] text-accent uppercase">Something went wrong</p>
        <h1 className="mt-4 text-3xl font-semibold">The journal could not load.</h1>
        <p className="mt-4 leading-7 text-muted">
          Try again, or return when the local application is available.
        </p>
        <button
          className="mt-8 rounded-full bg-accent px-5 py-3 text-sm font-bold text-white hover:bg-accent-strong"
          onClick={() => reset()}
        >
          Try again
        </button>
      </div>
    </main>
  );
}
