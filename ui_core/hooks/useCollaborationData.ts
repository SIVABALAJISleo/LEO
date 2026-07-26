import { useState, useEffect, useCallback } from "react";
import { firebaseClient as supabase } from "@/integrations/firebase/client";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";
import type { Json } from "@/integrations/supabase/types";

export interface CollaborationSession {
  id: string;
  room_id: string;
  name: string;
  description: string | null;
  owner_id: string;
  inference_job_id: string | null;
  status: string;
  settings: Json;
  created_at: string;
  updated_at: string;
  archived_at: string | null;
}

export interface Participant {
  id: string;
  session_id: string;
  user_id: string;
  role: string;
  joined_at: string;
  last_active_at: string | null;
  cursor_position: Json | null;
  is_online: boolean | null;
}

export interface CollaborationChange {
  id: string;
  session_id: string;
  user_id: string;
  change_type: string;
  target_module: string | null;
  previous_value: Json | null;
  new_value: Json | null;
  created_at: string;
}

export interface CollaborationComment {
  id: string;
  session_id: string;
  user_id: string;
  parent_id: string | null;
  module_name: string | null;
  content: string;
  mentions: string[] | null;
  created_at: string;
  updated_at: string;
}

export interface CollaborationMessage {
  id: string;
  session_id: string;
  user_id: string;
  content: string;
  mentions: string[] | null;
  created_at: string;
}

export interface ModuleLock {
  id: string;
  session_id: string;
  module_name: string;
  locked_by: string;
  locked_at: string;
  expires_at: string;
}

export interface CollaborationVote {
  id: string;
  session_id: string;
  user_id: string;
  vote_type: string;
  target_id: string | null;
  value: number;
  created_at: string;
}

export const useCollaborationData = (sessionId?: string) => {
  const { user } = useAuth();
  const [sessions, setSessions] = useState<CollaborationSession[]>([]);
  const [currentSession, setCurrentSession] = useState<CollaborationSession | null>(null);
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [changes, setChanges] = useState<CollaborationChange[]>([]);
  const [comments, setComments] = useState<CollaborationComment[]>([]);
  const [messages, setMessages] = useState<CollaborationMessage[]>([]);
  const [locks, setLocks] = useState<ModuleLock[]>([]);
  const [votes, setVotes] = useState<CollaborationVote[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchSessions = useCallback(async () => {
    if (!user) return;

    try {
      const { data, error } = await supabase
        .from("collaboration_sessions")
        .select("*")
        .order("created_at", { ascending: false });

      if (error) throw error;
      setSessions((data || []) as CollaborationSession[]);
    } catch (err) {
      console.error("Error fetching sessions:", err);
      setError(err as Error);
    }
  }, [user]);

  const fetchSessionData = useCallback(async () => {
    if (!user || !sessionId) return;

    setIsLoading(true);
    try {
      // Fetch session details
      const { data: sessionData, error: sessionError } = await supabase
        .from("collaboration_sessions")
        .select("*")
        .eq("id", sessionId)
        .single();

      if (sessionError) throw sessionError;
      setCurrentSession(sessionData as CollaborationSession);

      // Fetch participants
      const { data: participantsData } = await supabase
        .from("collaboration_participants")
        .select("*")
        .eq("session_id", sessionId);
      setParticipants((participantsData || []) as Participant[]);

      // Fetch changes
      const { data: changesData } = await supabase
        .from("collaboration_changes")
        .select("*")
        .eq("session_id", sessionId)
        .order("created_at", { ascending: false });
      setChanges((changesData || []) as CollaborationChange[]);

      // Fetch comments
      const { data: commentsData } = await supabase
        .from("collaboration_comments")
        .select("*")
        .eq("session_id", sessionId)
        .order("created_at", { ascending: true });
      setComments((commentsData || []) as CollaborationComment[]);

      // Fetch messages
      const { data: messagesData } = await supabase
        .from("collaboration_messages")
        .select("*")
        .eq("session_id", sessionId)
        .order("created_at", { ascending: true });
      setMessages((messagesData || []) as CollaborationMessage[]);

      // Fetch locks
      const { data: locksData } = await supabase
        .from("module_locks")
        .select("*")
        .eq("session_id", sessionId);
      setLocks((locksData || []) as ModuleLock[]);

      // Fetch votes
      const { data: votesData } = await supabase
        .from("collaboration_votes")
        .select("*")
        .eq("session_id", sessionId);
      setVotes((votesData || []) as CollaborationVote[]);
    } catch (err) {
      console.error("Error fetching session data:", err);
      setError(err as Error);
    } finally {
      setIsLoading(false);
    }
  }, [user, sessionId]);

  const createSession = async (name: string, description?: string) => {
    if (!user) return null;

    try {
      const roomId = `room-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      const { data, error } = await supabase
        .from("collaboration_sessions")
        .insert({
          room_id: roomId,
          name,
          description,
          owner_id: user.id,
        })
        .select()
        .single();

      if (error) throw error;

      // Add owner as participant
      await supabase.from("collaboration_participants").insert({
        session_id: data.id,
        user_id: user.id,
        role: "admin",
        is_online: true,
      });

      toast.success("Session created successfully");
      await fetchSessions();
      return data;
    } catch (err) {
      console.error("Error creating session:", err);
      toast.error("Failed to create session");
      return null;
    }
  };

  const joinSession = async (roomId: string) => {
    if (!user) return null;

    try {
      const { data: session, error: sessionError } = await supabase
        .from("collaboration_sessions")
        .select("*")
        .eq("room_id", roomId)
        .single();

      if (sessionError) throw sessionError;

      // Add as participant
      await supabase.from("collaboration_participants").insert({
        session_id: session.id,
        user_id: user.id,
        role: "editor",
        is_online: true,
      });

      toast.success("Joined session successfully");
      return session;
    } catch (err) {
      console.error("Error joining session:", err);
      toast.error("Failed to join session");
      return null;
    }
  };

  const sendMessage = async (content: string, mentions?: string[]) => {
    if (!user || !sessionId) return;

    try {
      const { error } = await supabase.from("collaboration_messages").insert({
        session_id: sessionId,
        user_id: user.id,
        content,
        mentions,
      });

      if (error) throw error;
    } catch (err) {
      console.error("Error sending message:", err);
      toast.error("Failed to send message");
    }
  };

  const addComment = async (
    content: string,
    moduleName?: string,
    parentId?: string,
    mentions?: string[],
  ) => {
    if (!user || !sessionId) return;

    try {
      const { error } = await supabase.from("collaboration_comments").insert({
        session_id: sessionId,
        user_id: user.id,
        content,
        module_name: moduleName,
        parent_id: parentId,
        mentions,
      });

      if (error) throw error;
      toast.success("Comment added");
    } catch (err) {
      console.error("Error adding comment:", err);
      toast.error("Failed to add comment");
    }
  };

  const lockModule = async (moduleName: string) => {
    if (!user || !sessionId) return false;

    try {
      const { error } = await supabase.from("module_locks").insert({
        session_id: sessionId,
        module_name: moduleName,
        locked_by: user.id,
      });

      if (error) throw error;
      return true;
    } catch (err) {
      console.error("Error locking module:", err);
      return false;
    }
  };

  const unlockModule = async (moduleName: string) => {
    if (!user || !sessionId) return false;

    try {
      const { error } = await supabase
        .from("module_locks")
        .delete()
        .eq("session_id", sessionId)
        .eq("module_name", moduleName)
        .eq("locked_by", user.id);

      if (error) throw error;
      return true;
    } catch (err) {
      console.error("Error unlocking module:", err);
      return false;
    }
  };

  const recordChange = async (
    changeType: string,
    targetModule: string,
    previousValue: Json,
    newValue: Json,
  ) => {
    if (!user || !sessionId) return;

    try {
      const { error } = await supabase.from("collaboration_changes").insert({
        session_id: sessionId,
        user_id: user.id,
        change_type: changeType,
        target_module: targetModule,
        previous_value: previousValue,
        new_value: newValue,
      });

      if (error) throw error;
    } catch (err) {
      console.error("Error recording change:", err);
    }
  };

  const vote = async (voteType: string, targetId?: string, value: number = 1) => {
    if (!user || !sessionId) return;

    try {
      const { error } = await supabase.from("collaboration_votes").insert({
        session_id: sessionId,
        user_id: user.id,
        vote_type: voteType,
        target_id: targetId,
        value,
      });

      if (error) throw error;
      toast.success("Vote recorded");
    } catch (err) {
      console.error("Error voting:", err);
      toast.error("Failed to vote");
    }
  };

  // Set up real-time subscriptions
  useEffect(() => {
    if (!sessionId) return;

    const channel = supabase
      .channel(`collaboration-${sessionId}`)
      .on(
        "postgres_changes",
        {
          event: "*",
          schema: "public",
          table: "collaboration_participants",
          filter: `session_id=eq.${sessionId}`,
        },
        () => fetchSessionData(),
      )
      .on(
        "postgres_changes",
        {
          event: "*",
          schema: "public",
          table: "collaboration_changes",
          filter: `session_id=eq.${sessionId}`,
        },
        () => fetchSessionData(),
      )
      .on(
        "postgres_changes",
        {
          event: "*",
          schema: "public",
          table: "collaboration_comments",
          filter: `session_id=eq.${sessionId}`,
        },
        () => fetchSessionData(),
      )
      .on(
        "postgres_changes",
        {
          event: "*",
          schema: "public",
          table: "collaboration_messages",
          filter: `session_id=eq.${sessionId}`,
        },
        () => fetchSessionData(),
      )
      .on(
        "postgres_changes",
        {
          event: "*",
          schema: "public",
          table: "module_locks",
          filter: `session_id=eq.${sessionId}`,
        },
        () => fetchSessionData(),
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [sessionId, fetchSessionData]);

  useEffect(() => {
    if (sessionId) {
      fetchSessionData();
    } else {
      fetchSessions();
      setIsLoading(false);
    }
  }, [sessionId, fetchSessions, fetchSessionData]);

  return {
    sessions,
    currentSession,
    participants,
    changes,
    comments,
    messages,
    locks,
    votes,
    isLoading,
    error,
    createSession,
    joinSession,
    sendMessage,
    addComment,
    lockModule,
    unlockModule,
    recordChange,
    vote,
    refetch: sessionId ? fetchSessionData : fetchSessions,
  };
};
