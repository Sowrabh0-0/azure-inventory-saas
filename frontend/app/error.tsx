"use client";

export default function Error({ error }: { error: Error }) {
  return (
    <div className="p-5">
      <h1 className="text-lg font-semibold">Something went wrong</h1>
      <p className="mt-2 text-sm text-muted-foreground">{error.message}</p>
    </div>
  );
}

