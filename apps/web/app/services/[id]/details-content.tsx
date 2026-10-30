"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";

import {
  ApiError,
  createServiceEvent,
  EventStatus,
  getService,
  getServiceEvents,
  resolveServiceEvent,
  Service,
  ServiceEvent
} from "../../../lib/api";

function readableError(error: unknown): string {
  return error instanceof ApiError ? error.message : "Something went wrong. Please try again.";
}

export default function ServiceDetailsContent({ id }: { id: string }) {
  const [service, setService] = useState<Service | null>(null);
  const [events, setEvents] = useState<ServiceEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showEventForm, setShowEventForm] = useState(false);

  const loadEvents = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [loadedService, loadedEvents] = await Promise.all([
        getService(id),
        getServiceEvents(id)
      ]);
      setService(loadedService);
      setEvents(loadedEvents);
    } catch (requestError) {
      setError(readableError(requestError));
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    void loadEvents();
  }, [loadEvents]);

  return (
    <main className="mx-auto min-h-screen max-w-4xl px-6 py-8 lg:px-10">
      <Link className="text-sm font-bold text-accent-strong hover:underline" href="/services">← Back to services</Link>
      <section className="mt-14">
        <p className="text-xs font-bold tracking-[0.2em] text-accent uppercase">Service events</p>
        <h1 className="mt-3 text-4xl font-semibold tracking-[-0.05em]">{service?.name || "Service details"}</h1>
        {service && <p className="mt-3 text-muted">{service.environment}{service.description ? ` · ${service.description}` : ""}</p>}
      </section>
      {loading && <p className="mt-10 rounded-2xl border border-line bg-panel p-8 text-muted">Loading event history...</p>}
      {!loading && error && (
        <div className="mt-10 rounded-2xl border border-red-200 bg-red-50 p-8 text-red-800">
          <p>{error}</p>
          <button className="mt-4 rounded-full border border-red-300 px-4 py-2 text-sm font-bold" onClick={() => void loadEvents()} type="button">Try again</button>
        </div>
      )}
      {!loading && !error && events.length === 0 && (
        <div className="mt-10 rounded-2xl border border-dashed border-line bg-panel p-10 text-center">
          <h2 className="text-xl font-semibold">No events recorded</h2>
          <p className="mt-2 text-muted">This service has an empty reliability history.</p>
        </div>
      )}
      {!loading && !error && (
        <div className="mt-8">
          <button className="rounded-full bg-accent px-5 py-2.5 text-sm font-bold text-white hover:bg-accent-strong" onClick={() => setShowEventForm((visible) => !visible)} type="button">
            {showEventForm ? "Close event form" : "Record event"}
          </button>
          {showEventForm && <EventForm serviceId={id} onCreated={(event) => {
            setEvents((current) => [event, ...current]);
            setShowEventForm(false);
          }} />}
        </div>
      )}
      {!loading && !error && events.length > 0 && (
        <ol className="mt-10 space-y-4">
          {events.map((event) => (
            <li className="rounded-2xl border border-line bg-panel p-6" key={event.id}>
              <div className="flex flex-wrap items-center justify-between gap-3">
                <h2 className="font-semibold">{event.summary}</h2>
                <span className="text-xs font-bold uppercase text-muted">{event.event_type} · {event.status}</span>
              </div>
              <p className="mt-3 text-sm text-muted">{new Date(event.occurred_at).toLocaleString()}</p>
              {event.details && <p className="mt-4 leading-7">{event.details}</p>}
              {event.resolved_at && <p className="mt-4 text-sm text-accent-strong">Resolved {new Date(event.resolved_at).toLocaleString()}</p>}
              {event.event_type === "incident" && !event.resolved_at && (
                <ResolveButton serviceId={id} event={event} onResolved={(resolved) => setEvents((current) => current.map((item) => item.id === resolved.id ? resolved : item))} />
              )}
            </li>
          ))}
        </ol>
      )}
    </main>
  );
}

function EventForm({ serviceId, onCreated }: { serviceId: string; onCreated: (event: ServiceEvent) => void }) {
  const [eventType, setEventType] = useState<"check" | "incident">("check");
  const [status, setStatus] = useState<EventStatus>("operational");
  const [summary, setSummary] = useState("");
  const [details, setDetails] = useState("");
  const [occurredAt, setOccurredAt] = useState(() => new Date().toISOString().slice(0, 16));
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!summary.trim()) {
      setError("Summary is required.");
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      const created = await createServiceEvent(serviceId, {
        event_type: eventType,
        status,
        summary: summary.trim(),
        ...(details.trim() ? { details: details.trim() } : {}),
        occurred_at: new Date(occurredAt).toISOString()
      });
      onCreated(created);
    } catch (requestError) {
      setError(readableError(requestError));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="mt-6 rounded-2xl border border-line bg-panel p-6" onSubmit={submit}>
      <h2 className="text-xl font-semibold">Record a reliability event</h2>
      <div className="mt-5 grid gap-5 md:grid-cols-2">
        <label className="text-sm font-semibold">Event type
          <select className="mt-2 w-full rounded-xl border border-line bg-background px-4 py-3 font-normal" value={eventType} onChange={(event) => {
            const nextType = event.target.value as "check" | "incident";
            setEventType(nextType);
            if (nextType === "incident" && status === "operational") setStatus("degraded");
          }}>
            <option value="check">Check</option>
            <option value="incident">Incident</option>
          </select>
        </label>
        <label className="text-sm font-semibold">Status
          <select className="mt-2 w-full rounded-xl border border-line bg-background px-4 py-3 font-normal" value={status} onChange={(event) => setStatus(event.target.value as EventStatus)}>
            {eventType === "check" && <option value="operational">Operational</option>}
            <option value="degraded">Degraded</option>
            <option value="down">Down</option>
          </select>
        </label>
      </div>
      <label className="mt-5 block text-sm font-semibold">Summary<input className="mt-2 w-full rounded-xl border border-line bg-background px-4 py-3 font-normal" value={summary} onChange={(event) => setSummary(event.target.value)} /></label>
      <label className="mt-5 block text-sm font-semibold">Details<textarea className="mt-2 min-h-20 w-full rounded-xl border border-line bg-background px-4 py-3 font-normal" value={details} onChange={(event) => setDetails(event.target.value)} /></label>
      <label className="mt-5 block text-sm font-semibold">Occurred at<input className="mt-2 w-full rounded-xl border border-line bg-background px-4 py-3 font-normal" type="datetime-local" value={occurredAt} onChange={(event) => setOccurredAt(event.target.value)} /></label>
      {error && <p className="mt-4 text-sm text-red-700" role="alert">{error}</p>}
      <button className="mt-5 rounded-full bg-accent px-5 py-2.5 text-sm font-bold text-white disabled:opacity-50" disabled={submitting} type="submit">{submitting ? "Recording..." : "Record event"}</button>
    </form>
  );
}

function ResolveButton({ serviceId, event, onResolved }: { serviceId: string; event: ServiceEvent; onResolved: (event: ServiceEvent) => void }) {
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function resolve() {
    setSubmitting(true);
    setError("");
    try {
      onResolved(await resolveServiceEvent(serviceId, event.id));
    } catch (requestError) {
      setError(readableError(requestError));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="mt-5">
      <button className="rounded-full border border-accent px-4 py-2 text-sm font-bold text-accent-strong disabled:opacity-50" disabled={submitting} onClick={() => void resolve()} type="button">{submitting ? "Resolving..." : "Resolve incident"}</button>
      {error && <p className="mt-2 text-sm text-red-700" role="alert">{error}</p>}
    </div>
  );
}
