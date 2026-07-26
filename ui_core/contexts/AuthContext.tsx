import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { firebaseClient as supabase } from "@/integrations/firebase/client";

/* ---------------- TYPES ---------------- */

interface User {
  id: string;
  username: string;
  email: string;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signIn: (identifier: string, password: string) => Promise<{ error: Error | null }>;
  signUp: (username: string, email: string, password: string) => Promise<{ error: Error | null }>;
  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<{ error: Error | null }>;
  sendResetOtp: (email: string) => Promise<{ error: Error | null }>;
  verifyOtp: (email: string, token: string) => Promise<{ error: Error | null }>;
}

/* ---------------- CONTEXT ---------------- */

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
};

/* ---------------- PROVIDER ---------------- */

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  /* -------- AUTH STATE SYNC (REAL PROFILE) -------- */

  useEffect(() => {
    // Check active session on mount
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user) {
        fetchUserProfile(session.user.id, session.user.email || "");
      } else {
        setUser(null);
        setLoading(false);
      }
    });

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (_event: string, session: any) => {
      if (!session?.user) {
        setUser(null);
        setLoading(false);
        return;
      }
      fetchUserProfile(session.user.id, session.user.email || "");
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  const fetchUserProfile = async (uid: string, email: string) => {
    try {
      // In a real Supabase setup, you'd have a 'profiles' table.
      // We will try to fetch the profile, or fallback to the auth metadata.
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { data, error } = await supabase.from("profiles").select("*").eq("id", uid).single();

      if (data) {
        setUser({ id: uid, email, username: data.username, created_at: data.created_at } as User);
      } else {
        // Fallback for new users before their profile trigger fires
        setUser({
          id: uid,
          email,
          username: email.split("@")[0],
          created_at: new Date().toISOString(),
        } as User);
      }
    } catch (err) {
      console.error("Failed to load user profile:", err);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  /* -------- SIGN IN -------- */

  const signIn = async (identifier: string, password: string) => {
    try {
      // Supabase primarily uses email for login by default unless customized.
      // We assume identifier is the email here.
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { data, error } = await supabase.auth.signInWithPassword({
        email: identifier,
        password,
      });

      if (error) throw error;
      return { error: null };
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (error: any) {
      return { error: new Error(error.message || "Invalid credentials") };
    }
  };

  /* -------- SIGN UP -------- */

  const signUp = async (username: string, email: string, password: string) => {
    try {
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            username: username.toLowerCase(),
          },
        },
      });

      if (error) throw error;
      return { error: null };
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      console.error("Registration error details:", err);
      return { error: new Error(err.message || "Registration failed") };
    }
  };

  /* -------- SIGN OUT -------- */

  const signOut = async () => {
    await supabase.auth.signOut();
    setUser(null);
  };

  /* -------- PASSWORD RESET -------- */

  const resetPassword = async (email: string) => {
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email);
      if (error) throw error;
      return { error: null };
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (error: any) {
      return { error: new Error(error.message || "Unable to send reset email") };
    }
  };

  const sendResetOtp = async (email: string) => {
    try {
      const { error } = await supabase.auth.sendResetOtp({ email });
      if (error) throw error;
      return { error: null };
    } catch (error: any) {
      return { error: new Error(error.message || "Failed to send reset code") };
    }
  };

  const verifyOtp = async (email: string, token: string) => {
    try {
      const { error } = await supabase.auth.verifyOtp({ email, token, type: "email" });
      if (error) throw error;
      return { error: null };
    } catch (error: any) {
      return { error: new Error(error.message || "Verification failed") };
    }
  };

  /* -------- PROVIDER -------- */

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        signIn,
        signUp,
        signOut,
        resetPassword,
        sendResetOtp,
        verifyOtp,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
