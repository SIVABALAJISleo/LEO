-- Fix collaboration tables INSERT policies to verify participant membership
-- This prevents non-participants from injecting data into collaboration sessions

-- Fix collaboration_changes INSERT policy
DROP POLICY IF EXISTS "Participants can create changes" ON public.collaboration_changes;
CREATE POLICY "Participants can create changes" 
ON public.collaboration_changes FOR INSERT 
TO authenticated
WITH CHECK (
  user_id = auth.uid() 
  AND EXISTS (
    SELECT 1 FROM public.collaboration_participants
    WHERE collaboration_participants.session_id = collaboration_changes.session_id
      AND collaboration_participants.user_id = auth.uid()
  )
);

-- Fix collaboration_comments INSERT policy
DROP POLICY IF EXISTS "Participants can create comments" ON public.collaboration_comments;
CREATE POLICY "Participants can create comments" 
ON public.collaboration_comments FOR INSERT 
TO authenticated
WITH CHECK (
  user_id = auth.uid() 
  AND EXISTS (
    SELECT 1 FROM public.collaboration_participants
    WHERE collaboration_participants.session_id = collaboration_comments.session_id
      AND collaboration_participants.user_id = auth.uid()
  )
);

-- Fix collaboration_messages INSERT policy
DROP POLICY IF EXISTS "Participants can send messages" ON public.collaboration_messages;
CREATE POLICY "Participants can send messages" 
ON public.collaboration_messages FOR INSERT 
TO authenticated
WITH CHECK (
  user_id = auth.uid() 
  AND EXISTS (
    SELECT 1 FROM public.collaboration_participants
    WHERE collaboration_participants.session_id = collaboration_messages.session_id
      AND collaboration_participants.user_id = auth.uid()
  )
);

-- Fix collaboration_votes INSERT policy
DROP POLICY IF EXISTS "Participants can vote" ON public.collaboration_votes;
CREATE POLICY "Participants can vote" 
ON public.collaboration_votes FOR INSERT 
TO authenticated
WITH CHECK (
  user_id = auth.uid() 
  AND EXISTS (
    SELECT 1 FROM public.collaboration_participants
    WHERE collaboration_participants.session_id = collaboration_votes.session_id
      AND collaboration_participants.user_id = auth.uid()
  )
);