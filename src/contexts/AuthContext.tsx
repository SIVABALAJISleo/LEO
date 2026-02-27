import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { auth, db } from "@/lib/firebase";

import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  sendPasswordResetEmail,
} from "firebase/auth";

import {
  doc,
  setDoc,
  getDoc,
} from "firebase/firestore";

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
  // Compatibility placeholders for existing components if needed, or we remove them if unused.
  // The user didn't include them in their snippet, but existing pages might call them.
  // Let's see if we strictly need them. If `Login.tsx` calls `updatePassword` etc, we'll need to add them back or mock them.
  // Based on the user's snippet, they only include `resetPassword`.
  // I will add back the mocks for `updatePassword` etc to prevent build errors in other files, 
  // but typed optionally or implemented as no-op if the interface definition allows.
  // The user's interface definition REMOVED `updatePassword`, `sendResetOtp`, `verifyOtp`.
  // So I will stick to the USER'S definition. If other pages break, I will fix those pages.
}

/* ---------------- CONTEXT ---------------- */

const AuthContext = createContext<AuthContextType | undefined>(undefined);

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
    const unsub = onAuthStateChanged(auth, async (fbUser) => {
      if (!fbUser) {
        setUser(null);
        setLoading(false);
        return;
      }

      try {
        const snap = await getDoc(doc(db, "users", fbUser.uid));

        if (!snap.exists()) {
          // If user exists in Auth but not in Firestore, we might want to create a profile or just sign out.
          // For now, adhering to user's logic: sign out.
          await firebaseSignOut(auth);
          setUser(null);
        } else {
          setUser({ id: fbUser.uid, ...snap.data() } as User);
        }
      } catch {
        setUser(null);
      }

      setLoading(false);
    });

    return () => unsub();
  }, []);

  /* -------- USERNAME → EMAIL LOOKUP -------- */

  const getEmailFromUsername = async (username: string): Promise<string> => {
    const ref = doc(db, "usernames", username.toLowerCase());
    const snap = await getDoc(ref);
    if (!snap.exists()) throw new Error("Invalid credentials");
    return snap.data().email;
  };

  /* -------- SIGN IN -------- */

  const signIn = async (identifier: string, password: string) => {
    try {
      const email = identifier.includes("@")
        ? identifier
        : await getEmailFromUsername(identifier);

      await signInWithEmailAndPassword(auth, email, password);
      return { error: null };
    } catch {
      return { error: new Error("Invalid credentials") };
    }
  };

  /* -------- SIGN UP -------- */

  const signUp = async (username: string, email: string, password: string) => {
    try {
      username = username.toLowerCase();

      // check username uniqueness
      const usernameRef = doc(db, "usernames", username);
      const usernameSnap = await getDoc(usernameRef);
      if (usernameSnap.exists())
        return { error: new Error("Username already taken") };

      // create auth account
      const cred = await createUserWithEmailAndPassword(auth, email, password);
      const uid = cred.user.uid;

      const profile: User = {
        id: uid,
        username,
        email,
        created_at: new Date().toISOString(),
      };

      // save profile
      await setDoc(doc(db, "users", uid), profile);

      // reserve username
      await setDoc(usernameRef, { uid, email });

      return { error: null };
    } catch (err: any) {
      console.error("Registration error details:", err);
      return { error: new Error(err.message || "Registration failed") };
    }
  };

  /* -------- SIGN OUT -------- */

  const signOut = async () => {
    await firebaseSignOut(auth);
    setUser(null);
  };

  /* -------- PASSWORD RESET -------- */

  const resetPassword = async (email: string) => {
    try {
      await sendPasswordResetEmail(auth, email);
      return { error: null };
    } catch {
      return { error: new Error("Unable to send reset email") };
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
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
