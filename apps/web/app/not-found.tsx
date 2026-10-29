import Link from "next/link";

export default function NotFound() {
  return (
    <main className="grid min-h-screen place-items-center px-6">
      <div className="max-w-md text-center">
        <p className="font-mono text-sm text-accent">404</p>
        <h1 className="mt-4 text-3xl font-semibold">This page is not in the journal.</h1>
        <p className="mt-4 leading-7 text-muted">
          The page you requested does not exist in this foundation.
        </p>
        <Link
          className="mt-8 inline-flex rounded-full bg-accent px-5 py-3 text-sm font-bold text-white hover:bg-accent-strong"
          href="/"
        >
          Return home
        </Link>
      </div>
    </main>
  );
}
