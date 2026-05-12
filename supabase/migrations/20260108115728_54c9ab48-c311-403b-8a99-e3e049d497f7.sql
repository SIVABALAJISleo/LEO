-- =====================================================
-- PRODUCTION HARDENING: POLICY-AS-CODE + GUARDRAILS
-- =====================================================

-- 1. FEATURE FLAGS TABLE (Policy-as-Code)
CREATE TABLE IF NOT EXISTS public.feature_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    flag_key TEXT NOT NULL UNIQUE,
    flag_value BOOLEAN NOT NULL DEFAULT false,
    description TEXT,
    applies_to_roles app_role[] DEFAULT ARRAY['user'::app_role],
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 2. SYSTEM LIMITS TABLE (Guardrails)
CREATE TABLE IF NOT EXISTS public.system_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    limit_key TEXT NOT NULL UNIQUE,
    limit_value INTEGER NOT NULL,
    limit_type TEXT NOT NULL CHECK (limit_type IN ('rate', 'quota', 'cost', 'timeout')),
    scope TEXT NOT NULL CHECK (scope IN ('global', 'per_user', 'per_role')),
    applies_to_role app_role,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 3. RATE LIMIT TRACKING TABLE (Circuit Breaker)
CREATE TABLE IF NOT EXISTS public.rate_limit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    action_type TEXT NOT NULL,
    action_count INTEGER NOT NULL DEFAULT 1,
    window_start TIMESTAMPTZ NOT NULL DEFAULT now(),
    blocked BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 4. SECURITY AUDIT LOG (Observability)
CREATE TABLE IF NOT EXISTS public.security_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT,
    result TEXT NOT NULL CHECK (result IN ('allowed', 'denied', 'error')),
    reason TEXT,
    ip_address TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 5. POLICY VIOLATIONS TABLE (Alerts)
CREATE TABLE IF NOT EXISTS public.policy_violations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    violation_type TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    user_id UUID,
    resource_type TEXT,
    resource_id TEXT,
    details JSONB,
    resolved BOOLEAN NOT NULL DEFAULT false,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable RLS on all new tables
ALTER TABLE public.feature_flags ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.system_limits ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.rate_limit_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.security_audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.policy_violations ENABLE ROW LEVEL SECURITY;

-- FEATURE FLAGS POLICIES (Read-only for all, write for admins)
CREATE POLICY "Anyone can read feature flags"
ON public.feature_flags FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Only admins can modify feature flags"
ON public.feature_flags FOR ALL
TO authenticated
USING (public.has_role(auth.uid(), 'admin'))
WITH CHECK (public.has_role(auth.uid(), 'admin'));

-- SYSTEM LIMITS POLICIES (Read-only for all, write for admins)
CREATE POLICY "Anyone can read system limits"
ON public.system_limits FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Only admins can modify system limits"
ON public.system_limits FOR ALL
TO authenticated
USING (public.has_role(auth.uid(), 'admin'))
WITH CHECK (public.has_role(auth.uid(), 'admin'));

-- RATE LIMIT EVENTS POLICIES (Users see own, admins see all)
CREATE POLICY "Users can view own rate limit events"
ON public.rate_limit_events FOR SELECT
TO authenticated
USING (user_id = auth.uid() OR public.has_role(auth.uid(), 'admin'));

CREATE POLICY "Service role inserts rate limit events"
ON public.rate_limit_events FOR INSERT
TO anon, authenticated
WITH CHECK (false);

-- SECURITY AUDIT LOG POLICIES (Admins only)
CREATE POLICY "Only admins can view audit log"
ON public.security_audit_log FOR SELECT
TO authenticated
USING (public.has_role(auth.uid(), 'admin'));

CREATE POLICY "No direct inserts to audit log"
ON public.security_audit_log FOR INSERT
TO anon, authenticated
WITH CHECK (false);

-- POLICY VIOLATIONS POLICIES (Admins only)
CREATE POLICY "Only admins can view violations"
ON public.policy_violations FOR SELECT
TO authenticated
USING (public.has_role(auth.uid(), 'admin'));

CREATE POLICY "Only admins can update violations"
ON public.policy_violations FOR UPDATE
TO authenticated
USING (public.has_role(auth.uid(), 'admin'))
WITH CHECK (public.has_role(auth.uid(), 'admin'));

CREATE POLICY "No direct inserts to violations"
ON public.policy_violations FOR INSERT
TO anon, authenticated
WITH CHECK (false);

-- Create updated_at trigger for new tables
CREATE TRIGGER update_feature_flags_updated_at
    BEFORE UPDATE ON public.feature_flags
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_system_limits_updated_at
    BEFORE UPDATE ON public.system_limits
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- 6. SECURITY DEFINER FUNCTION: Check feature flag
CREATE OR REPLACE FUNCTION public.is_feature_enabled(
    _flag_key TEXT,
    _user_id UUID DEFAULT NULL
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    _flag_value BOOLEAN;
    _applies_to app_role[];
    _user_role app_role;
BEGIN
    SELECT flag_value, applies_to_roles INTO _flag_value, _applies_to
    FROM public.feature_flags
    WHERE flag_key = _flag_key;
    
    IF _flag_value IS NULL THEN
        RETURN false; -- Default: disabled if not found
    END IF;
    
    IF NOT _flag_value THEN
        RETURN false;
    END IF;
    
    -- If user provided, check role
    IF _user_id IS NOT NULL THEN
        SELECT role INTO _user_role
        FROM public.user_roles
        WHERE user_id = _user_id
        LIMIT 1;
        
        IF _user_role IS NOT NULL AND NOT (_user_role = ANY(_applies_to)) THEN
            RETURN false;
        END IF;
    END IF;
    
    RETURN true;
END;
$$;

-- 7. SECURITY DEFINER FUNCTION: Check rate limit
CREATE OR REPLACE FUNCTION public.check_rate_limit(
    _user_id UUID,
    _action_type TEXT,
    _window_minutes INTEGER DEFAULT 60
)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    _limit INTEGER;
    _current_count INTEGER;
    _window_start TIMESTAMPTZ;
BEGIN
    -- Get limit for this action
    SELECT limit_value INTO _limit
    FROM public.system_limits
    WHERE limit_key = _action_type AND limit_type = 'rate';
    
    IF _limit IS NULL THEN
        RETURN true; -- No limit defined = allowed
    END IF;
    
    _window_start := now() - (_window_minutes * interval '1 minute');
    
    -- Count actions in window
    SELECT COALESCE(SUM(action_count), 0) INTO _current_count
    FROM public.rate_limit_events
    WHERE user_id = _user_id
      AND action_type = _action_type
      AND window_start >= _window_start;
    
    RETURN _current_count < _limit;
END;
$$;

-- 8. SECURITY DEFINER FUNCTION: Log security event
CREATE OR REPLACE FUNCTION public.log_security_event(
    _user_id UUID,
    _action TEXT,
    _resource_type TEXT,
    _resource_id TEXT,
    _result TEXT,
    _reason TEXT DEFAULT NULL,
    _metadata JSONB DEFAULT NULL
)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    _event_id UUID;
BEGIN
    INSERT INTO public.security_audit_log (
        user_id, action, resource_type, resource_id, result, reason, metadata
    ) VALUES (
        _user_id, _action, _resource_type, _resource_id, _result, _reason, _metadata
    ) RETURNING id INTO _event_id;
    
    RETURN _event_id;
END;
$$;

-- 9. INSERT DEFAULT SYSTEM LIMITS (Guardrails)
INSERT INTO public.system_limits (limit_key, limit_value, limit_type, scope, description) VALUES
    ('api_calls_per_hour', 1000, 'rate', 'per_user', 'Maximum API calls per hour per user'),
    ('jobs_per_day', 100, 'quota', 'per_user', 'Maximum GPU jobs per day per user'),
    ('max_job_cost_usd', 100, 'cost', 'per_user', 'Maximum cost per single job in USD'),
    ('job_timeout_seconds', 3600, 'timeout', 'global', 'Maximum job execution time'),
    ('concurrent_jobs', 5, 'quota', 'per_user', 'Maximum concurrent running jobs'),
    ('webhook_retries', 3, 'quota', 'global', 'Maximum webhook retry attempts'),
    ('failed_auth_per_hour', 10, 'rate', 'per_user', 'Maximum failed auth attempts per hour')
ON CONFLICT (limit_key) DO NOTHING;

-- 10. INSERT DEFAULT FEATURE FLAGS
INSERT INTO public.feature_flags (flag_key, flag_value, description, applies_to_roles) VALUES
    ('payment_stripe_enabled', true, 'Enable Stripe payments', ARRAY['user'::app_role, 'admin'::app_role]),
    ('payment_razorpay_enabled', true, 'Enable Razorpay payments', ARRAY['user'::app_role, 'admin'::app_role]),
    ('gpu_jobs_enabled', true, 'Enable GPU job submissions', ARRAY['user'::app_role, 'admin'::app_role]),
    ('admin_bypass_limits', true, 'Admins can bypass rate limits', ARRAY['admin'::app_role]),
    ('maintenance_mode', false, 'System maintenance mode - blocks non-admin access', ARRAY['admin'::app_role])
ON CONFLICT (flag_key) DO NOTHING;

-- 11. FIX SYSTEM SETTINGS WRITE PROTECTION (Security finding)
CREATE POLICY "Only admins can insert system settings"
ON public.system_settings FOR INSERT
TO authenticated
WITH CHECK (public.has_role(auth.uid(), 'admin'));

CREATE POLICY "Only admins can update system settings"
ON public.system_settings FOR UPDATE
TO authenticated
USING (public.has_role(auth.uid(), 'admin'))
WITH CHECK (public.has_role(auth.uid(), 'admin'));

CREATE POLICY "Only admins can delete system settings"
ON public.system_settings FOR DELETE
TO authenticated
USING (public.has_role(auth.uid(), 'admin'));