import Link from "next/link";

const principles = [
  {
    number: "01",
    title: "Record the signal",
    description: "Keep checks and incidents together in one readable history."
  },
  {
    number: "02",
    title: "See the context",
    description: "Understand what changed before reaching for another tool."
  },
  {
    number: "03",
    title: "Close the loop",
    description: "Resolve incidents deliberately and leave a useful record."
  }
];

export default function Home() {
  return (
    <main className="min-h-screen">
      <header className="mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-6 lg:px-10">
        <Link
          className="flex items-center gap-3 rounded-sm text-sm font-bold tracking-[0.18em] text-accent-strong uppercase"
          href="/"
          aria-label="CloudXzen home"
        >
          <span
            className="grid size-9 place-items-center rounded-xl bg-accent text-sm text-white shadow-sm"
            aria-hidden="true"
          >
            CX
          </span>
          CloudXzen
        </Link>
        <nav aria-label="Primary navigation" className="hidden items-center gap-8 text-sm text-muted sm:flex">
          <a className="transition-colors hover:text-foreground" href="#principles">
            Principles
          </a>
          <a className="transition-colors hover:text-foreground" href="#status">
            Foundation status
          </a>
        </nav>
      </header>

      <section className="mx-auto grid w-full max-w-7xl gap-16 px-6 pb-20 pt-14 lg:grid-cols-[1.1fr_0.9fr] lg:px-10 lg:pb-28 lg:pt-24">
        <div className="flex flex-col justify-center">
          <p className="mb-6 flex items-center gap-3 text-xs font-bold tracking-[0.2em] text-accent uppercase">
            <span className="h-px w-8 bg-accent" aria-hidden="true" />
            Service reliability journal
          </p>
          <h1 className="max-w-3xl text-5xl leading-[0.98] font-semibold tracking-[-0.06em] text-foreground sm:text-7xl">
            Service reliability,
            <span className="block text-accent">without the noise.</span>
          </h1>
          <p className="mt-8 max-w-xl text-lg leading-8 text-muted">
            CloudXzen is a focused place to record service checks, understand
            incidents, and keep the operational story close at hand.
          </p>
          <div className="mt-10 flex flex-wrap items-center gap-4">
            <Link
              className="rounded-full bg-accent px-6 py-3 text-sm font-bold text-white shadow-sm transition-colors hover:bg-accent-strong"
              href="/services"
            >
              View services
            </Link>
            <span className="text-sm text-muted">Built for deliberate operations.</span>
          </div>
        </div>

        <div className="relative flex items-center justify-center" aria-label="Journal preview">
          <div className="absolute -inset-8 rounded-[3rem] bg-accent-soft/70 blur-3xl" aria-hidden="true" />
          <div className="relative w-full max-w-md rounded-3xl border border-line bg-panel p-5 shadow-[0_24px_70px_rgba(27,65,52,0.12)]">
            <div className="flex items-center justify-between border-b border-line pb-5">
              <div>
                <p className="text-xs font-bold tracking-[0.16em] text-muted uppercase">Journal view</p>
                <p className="mt-1 text-lg font-semibold">Your operational record</p>
              </div>
              <span className="rounded-full bg-accent-soft px-3 py-1 text-xs font-bold text-accent-strong">
                Ready
              </span>
            </div>
            <div className="py-6">
              <div className="mb-5 flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold">A calm place for context</p>
                  <p className="mt-1 text-sm text-muted">Connect the dots as the story develops.</p>
                </div>
                <span className="grid size-10 place-items-center rounded-full bg-[#f0e4d3] text-sm font-bold text-[#8c5c22]">
                  +
                </span>
              </div>
              <div className="space-y-3">
                <div className="h-2 w-full rounded-full bg-accent-soft" />
                <div className="h-2 w-4/5 rounded-full bg-[#eef1ed]" />
                <div className="h-2 w-3/5 rounded-full bg-[#eef1ed]" />
              </div>
            </div>
            <div className="rounded-2xl bg-[#f4f7f4] p-4 text-sm text-muted">
              Connect the API locally to record services, checks, and incidents
              without losing the operational context.
            </div>
          </div>
        </div>
      </section>

      <section
        id="principles"
        className="border-y border-line bg-white/50 px-6 py-16 lg:px-10 lg:py-20"
      >
        <div className="mx-auto max-w-7xl">
          <div className="max-w-xl">
            <p className="text-xs font-bold tracking-[0.2em] text-accent uppercase">The approach</p>
            <h2 className="mt-4 text-3xl font-semibold tracking-[-0.04em] sm:text-4xl">
              Make the useful part easier to see.
            </h2>
          </div>
          <div className="mt-12 grid gap-8 md:grid-cols-3">
            {principles.map((principle) => (
              <article key={principle.number} className="border-t-2 border-accent pt-5">
                <p className="font-mono text-sm text-accent">{principle.number}</p>
                <h3 className="mt-8 text-xl font-semibold">{principle.title}</h3>
                <p className="mt-3 leading-7 text-muted">{principle.description}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="status" className="mx-auto max-w-7xl px-6 py-16 lg:px-10 lg:py-24">
        <div className="rounded-3xl bg-accent-strong p-8 text-white sm:p-12">
          <div className="grid gap-8 md:grid-cols-[1fr_auto] md:items-end">
            <div>
              <p className="text-xs font-bold tracking-[0.2em] text-[#a8d7c6] uppercase">Service journal</p>
              <h2 className="mt-4 max-w-2xl text-3xl font-semibold tracking-[-0.04em] sm:text-4xl">
                Keep the operational story close at hand.
              </h2>
            </div>
            <p className="max-w-xs text-sm leading-6 text-[#c8e4d9]">
              Browse registered services, record supported events, and resolve
              incidents through the existing API.
            </p>
          </div>
        </div>
      </section>

      <footer className="mx-auto flex max-w-7xl flex-col gap-3 px-6 pb-8 text-sm text-muted sm:flex-row sm:items-center sm:justify-between lg:px-10">
        <p>CloudXzen Service Reliability Journal</p>
        <p>Foundation milestone · Local-first · KSh 0 target</p>
      </footer>
    </main>
  );
}
