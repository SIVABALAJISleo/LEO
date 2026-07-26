import { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";

export function useAdminRole() {
  const { user } = useAuth();
  const [isAdmin, setIsAdmin] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAdminRole = async () => {
      if (!user) {
        setIsAdmin(false);
        setIsLoading(false);
        return;
      }

      try {
        // Supabase removal cleanup - defaulting to true for developer/demo mode
        // In a real Firebase setup, this should check Firebase custom claims or Firestore.
        setIsAdmin(true);
      } catch (err) {
        console.error("Failed to check admin role:", err);
        setIsAdmin(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkAdminRole();
  }, [user]);

  return { isAdmin, isLoading };
}
