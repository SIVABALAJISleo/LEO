import React, { createContext, useContext, useState, useEffect } from "react";
import { fetchLeoStatus, LeoStatus } from "../lib/api";

interface LeoStatusContextType {
  status: LeoStatus | null;
  loading: boolean;
  error: string;
  refreshStatus: () => Promise<void>;
}

const LeoStatusContext = createContext<LeoStatusContextType | undefined>(undefined);

export const LeoStatusProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [status, setStatus] = useState<LeoStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const refreshStatus = async () => {
    try {
      const data = await fetchLeoStatus();
      setStatus(data);
      setError("");
    } catch (err: any) {
      setError(err.message || "Failed to fetch status");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshStatus();
    const interval = setInterval(refreshStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <LeoStatusContext.Provider value={{ status, loading, error, refreshStatus }}>
      {children}
    </LeoStatusContext.Provider>
  );
};

export const useLeoStatus = () => {
  const context = useContext(LeoStatusContext);
  if (!context) {
    throw new Error("useLeoStatus must be used within a LeoStatusProvider");
  }
  return context;
};
