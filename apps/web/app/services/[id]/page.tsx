"use client";

import { use } from "react";

import ServiceDetailsContent from "./details-content";

export default function ServiceDetailsPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  return <ServiceDetailsContent id={id} />;
}
