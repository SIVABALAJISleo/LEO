-- Fix log_security_event() to validate caller permissions
-- Users can only log events for themselves unless they're admin

CREATE OR REPLACE FUNCTION public.log_security_event(
    _user_id uuid, 
    _action text, 
    _resource_type text, 
    _resource_id text, 
    _result text, 
    _reason text DEFAULT NULL::text, 
    _metadata jsonb DEFAULT NULL::jsonb
)
RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    _event_id UUID;
    _caller_id UUID;
BEGIN
    -- Get the caller's ID
    _caller_id := auth.uid();
    
    -- Validate: Users can only log events for themselves unless they're admin
    -- Allow NULL user_id for system/anonymous events
    IF _user_id IS NOT NULL AND _caller_id IS NOT NULL AND _user_id != _caller_id THEN
        IF NOT public.has_role(_caller_id, 'admin') THEN
            RAISE EXCEPTION 'Permission denied: Cannot log security events for other users';
        END IF;
    END IF;
    
    -- If caller is authenticated but no user_id provided, use caller's id
    IF _user_id IS NULL AND _caller_id IS NOT NULL THEN
        _user_id := _caller_id;
    END IF;
    
    INSERT INTO public.security_audit_log (
        user_id, action, resource_type, resource_id, result, reason, metadata
    ) VALUES (
        _user_id, _action, _resource_type, _resource_id, _result, _reason, _metadata
    ) RETURNING id INTO _event_id;
    
    RETURN _event_id;
END;
$$;