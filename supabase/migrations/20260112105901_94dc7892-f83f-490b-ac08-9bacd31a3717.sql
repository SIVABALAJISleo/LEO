-- Drop the overly permissive policy that allows anyone to manage locks
DROP POLICY IF EXISTS "System can manage locks" ON public.expectation_locks;

-- Create proper owner-based policies for expectation_locks
-- Users can only insert locks for themselves
CREATE POLICY "Users can insert their own locks"
ON public.expectation_locks
FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);

-- Users can only update their own locks
CREATE POLICY "Users can update their own locks"
ON public.expectation_locks
FOR UPDATE
TO authenticated
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- Users can only delete their own locks
CREATE POLICY "Users can delete their own locks"
ON public.expectation_locks
FOR DELETE
TO authenticated
USING (auth.uid() = user_id);

-- Admins can manage all locks (for system operations)
CREATE POLICY "Admins can manage all locks"
ON public.expectation_locks
FOR ALL
TO authenticated
USING (public.has_role(auth.uid(), 'admin'))
WITH CHECK (public.has_role(auth.uid(), 'admin'));