"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";

import { ApiError, createService, listServices, Service, ServiceStatus } from "../../lib/api";

const statusStyles: Record<ServiceStatus, string> = {
  unknown: "bg-slate-100 text-slate-700",
  operational: "bg-accent-soft text-accent-strong",
  degraded: "bg-amber-100 text-amber-800",
  down: "bg-red-100 text-red-800"
};

function readableError(error: unknown): string {
  return error instanceof ApiError ? error.message : "Something went wrong. Please try again.";
}

export default function ServicesPage() {
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);

  const loadServices = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setServices(await listServices());
    } catch (requestError) {
      setError(readableError(requestError));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadServices();
  }, [loadServices]);

  return (
    <main className="mx-auto min-h-screen max-w-7xl px-6 py-8 lg:px-10">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <Link className="text-sm font-bold tracking-[0.18em] text-accent-strong uppercase" href="/">
          CloudXzen
        </Link>
        <button
          className="rounded-full bg-accent px-5 py-2.5 text-sm font-bold text-white hover:bg-accent-strong"
          onClick={() => setShowForm((visible) => !visible)}
          type="button"
        >
          {showForm ? "Close form" : "Register service"}
        </button>
      </header>

      <section className="mt-16">
        <p className="text-xs font-bold tracking-[0.2em] text-accent uppercase">Service journal</p>
        <h1 className="mt-3 text-4xl font-semibold tracking-[-0.05em] sm:text-6xl">Registered services</h1>
        <p className="mt-5 max-w-2xl leading-7 text-muted">
          Track the current signal and event history for each service without inventing metrics the API does not provide.
        </p>
      </section>

      {showForm && <ServiceForm onCreated={(service) => {
        setServices((current) => [service, ...current]);
        setShowForm(false);
      }} />}

      <section aria-live="polite" className="mt-12">
        {loading && <p className="rounded-2xl border border-line bg-panel p-8 text-muted">Loading services...</p>}
        {!loading && error && (
          <div className="rounded-2xl border border-red-200 bg-red-50 p-8 text-red-800">
            <p>{error}</p>
            <button className="mt-4 rounded-full border border-red-300 px-4 py-2 text-sm font-bold" onClick={() => void loadServices()} type="button">
              Try again
            </button>
          </div>
        )}
        {!loading && !error && services.length === 0 && (
          <div className="rounded-2xl border border-dashed border-line bg-panel p-10 text-center">
            <h2 className="text-xl font-semibold">No services registered yet</h2>
            <p className="mt-2 text-muted">Register the first service to begin its reliability journal.</p>
          </div>
        )}
        {!loading && !error && services.length > 0 && (
          <div className="grid gap-5 md:grid-cols-2">
            {services.map((service) => (
              <Link className="rounded-2xl border border-line bg-panel p-6 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md" href={`/services/${service.id}`} key={service.id}>
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h2 className="text-xl font-semibold">{service.name}</h2>
                    <p className="mt-1 text-sm text-muted">{service.environment}</p>
                  </div>
                  <span className={`rounded-full px-3 py-1 text-xs font-bold uppercase ${statusStyles[service.status]}`}>
                    {service.status}
                  </span>
                </div>
                {service.description && <p className="mt-5 leading-7 text-muted">{service.description}</p>}
              </Link>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}

function ServiceForm({ onCreated }: { onCreated: (service: Service) => void }) {
  const [name, setName] = useState("");
  const [environment, setEnvironment] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!name.trim() || !environment.trim()) {
      setError("Name and environment are required.");
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      const service = await createService({
        name: name.trim(),
        environment: environment.trim(),
        ...(description.trim() ? { description: description.trim() } : {})
      });
      onCreated(service);
    } catch (requestError) {
      setError(readableError(requestError));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="mt-10 rounded-2xl border border-line bg-panel p-6" onSubmit={submit}>
      <h2 className="text-xl font-semibold">Register a service</h2>
      <div className="mt-5 grid gap-5 md:grid-cols-2">
        <label className="text-sm font-semibold">Name<input className="mt-2 w-full rounded-xl border border-line bg-background px-4 py-3 font-normal" value={name} onChange={(event) => setName(event.target.value)} /></label>
        <label className="text-sm font-semibold">Environment<input className="mt-2 w-full rounded-xl border border-line bg-background px-4 py-3 font-normal" value={environment} onChange={(event) => setEnvironment(event.target.value)} /></label>
      </div>
      <label className="mt-5 block text-sm font-semibold">Description<textarea className="mt-2 min-h-24 w-full rounded-xl border border-line bg-background px-4 py-3 font-normal" value={description} onChange={(event) => setDescription(event.target.value)} /></label>
      {error && <p className="mt-4 text-sm text-red-700" role="alert">{error}</p>}
      <button className="mt-5 rounded-full bg-accent px-5 py-2.5 text-sm font-bold text-white disabled:opacity-50" disabled={submitting} type="submit">
        {submitting ? "Registering..." : "Register service"}
      </button>
    </form>
  );
}
