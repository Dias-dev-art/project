import { useQuery } from "@tanstack/react-query";
import { fetchScans } from "../api/client";

export default function Dashboard() {
  const { data, isLoading } = useQuery({ queryKey: ["scans"], queryFn: fetchScans });
  if (isLoading) return <p>Loading…</p>;
  return (
    <main>
      <h1>PR Security Scanner</h1>
      <ul>
        {data?.map((s) => (
          <li key={s.id}>
            {s.repo_full_name} #{s.pr_number} — {s.status}
          </li>
        ))}
      </ul>
    </main>
  );
}
