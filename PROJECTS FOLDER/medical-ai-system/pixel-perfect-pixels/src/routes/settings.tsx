import { createFileRoute } from "@tanstack/react-router";
import { PageHeader, Notice } from "@/components/common";

export const Route = createFileRoute("/settings")({
  head: () => ({ meta: [
    { title: "Settings — BioPulse" },
    { name: "description", content: "Interface preferences and integration status." },
    { property: "og:title", content: "Settings — BioPulse" },
    { property: "og:description", content: "Interface preferences and integration status." },
  ] }),
  component: () => (
    <div>
      <PageHeader title="Settings" subtitle="Interface preferences and integration status." />
      <Notice tone="signal">This workspace is in demonstration mode. Backend: not connected · CNN model: integration pending · IoT sensors: not connected.</Notice>
    </div>
  ),
});
