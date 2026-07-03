export const getApiUrl = (): string => {
  if (typeof window !== "undefined") {
    const stored = localStorage.getItem("COGNIVEAVE_API_URL");
    if (stored) return stored.replace(/\/$/, "");
  }
  return (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "");
};
