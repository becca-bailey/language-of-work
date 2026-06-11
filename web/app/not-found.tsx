import Link from "next/link";

export default function NotFound() {
  return (
    <main className="mx-auto w-full max-w-3xl flex-1 px-6 py-16">
      <p className="font-mono text-xs uppercase tracking-[0.2em] text-neutral-500">
        404
      </p>
      <h1 className="mt-2 text-3xl font-semibold tracking-tight">
        Page not found
      </h1>
      <p className="mt-4 max-w-prose text-neutral-600 dark:text-neutral-400">
        This page doesn&apos;t exist, or the data for it hasn&apos;t been
        exported yet.
      </p>
      <Link
        href="/"
        className="mt-8 inline-block text-sm text-indigo-600 hover:underline dark:text-indigo-400"
      >
        &larr; Back to stories
      </Link>
    </main>
  );
}
