import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/about")({
  head: () => ({
    meta: [
      { title: "About — LEO AI" },
      {
        name: "description",
        content:
          "LEO AI: building the most efficient open-source AI runtime for commodity hardware.",
      },
      { property: "og:title", content: "About LEO AI" },
      {
        property: "og:description",
        content: "One developer. One mission: capable AI without expensive GPUs.",
      },
    ],
  }),
  component: AboutPage,
});

function AboutPage() {
  return (
    <div className="mx-auto max-w-[1440px] px-6 py-24">
      <p className="eyebrow">Our mission</p>
      <h1 className="mt-3 max-w-4xl font-display text-5xl font-bold md:text-7xl">
        Capable AI shouldn't require a data center.
      </h1>
      <div className="mt-16 grid gap-12 md:grid-cols-2">
        <div>
          <div className="eyebrow">The problem</div>
          <p className="mt-4 text-lg text-muted-foreground leading-relaxed">
            Modern AI assumes racks of expensive GPUs and constant cloud connectivity. That excludes
            most developers, students, and privacy-sensitive users.
          </p>
        </div>
        <div>
          <div className="eyebrow">The approach</div>
          <p className="mt-4 text-lg text-muted-foreground leading-relaxed">
            LEO combines software innovations — semantic caching, adaptive routing, speculative
            decoding, heterogeneous CPU+iGPU execution — to make ordinary hardware perform.
          </p>
        </div>
        <div>
          <div className="eyebrow">The vision</div>
          <p className="mt-4 text-lg text-muted-foreground leading-relaxed">
            Build one of the most efficient open-source AI runtimes for commodity hardware. Measure
            everything. Prove it with real benchmarks.
          </p>
        </div>
        <div>
          <div className="eyebrow">The team</div>
          <p className="mt-4 text-lg text-muted-foreground leading-relaxed">
            LEO AI is built by a solo developer, in the open, for developers, researchers, students,
            and privacy-conscious users worldwide.
          </p>
        </div>
      </div>
    </div>
  );
}
