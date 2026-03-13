-- Fix overly permissive RLS policy on payment_webhook_events
-- The current policy allows anyone to insert with WITH CHECK (true)
-- Change it so only service role can insert (service role bypasses RLS anyway)

-- Drop the existing overly permissive insert policy
DROP POLICY IF EXISTS "Service can insert webhook events" ON public.payment_webhook_events;

-- Create a restrictive policy that denies direct inserts from anon/authenticated users
-- The service role key used in the edge function will bypass RLS and can still insert
CREATE POLICY "Deny direct webhook event inserts" 
ON public.payment_webhook_events 
FOR INSERT 
TO anon, authenticated
WITH CHECK (false);