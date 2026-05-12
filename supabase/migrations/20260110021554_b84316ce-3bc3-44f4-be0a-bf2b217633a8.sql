-- Backup metadata table for tracking backup history and verification
CREATE TABLE IF NOT EXISTS public.backup_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    backup_type TEXT NOT NULL CHECK (backup_type IN ('daily', 'weekly', 'monthly', 'manual')),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'failed', 'verified')),
    size_bytes BIGINT,
    checksum TEXT,
    location TEXT,
    region TEXT DEFAULT 'us-east-1',
    retention_days INTEGER DEFAULT 30,
    encrypted BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    verified_at TIMESTAMPTZ,
    verification_result JSONB,
    expires_at TIMESTAMPTZ,
    user_id UUID NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Enable RLS
ALTER TABLE public.backup_metadata ENABLE ROW LEVEL SECURITY;

-- Only admins can view backup metadata
CREATE POLICY "Admins can view backups"
ON public.backup_metadata FOR SELECT
TO authenticated
USING (public.has_role(auth.uid(), 'admin'));

-- Only service role can insert/update
CREATE POLICY "Service role manages backups"
ON public.backup_metadata FOR ALL
TO authenticated
USING (public.has_role(auth.uid(), 'admin'))
WITH CHECK (public.has_role(auth.uid(), 'admin'));

-- Release management table for versioned deployments
CREATE TABLE IF NOT EXISTS public.releases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version TEXT NOT NULL,
    previous_version TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'deploying', 'deployed', 'rolled_back', 'failed')),
    rollout_percentage INTEGER DEFAULT 0 CHECK (rollout_percentage >= 0 AND rollout_percentage <= 100),
    deployed_at TIMESTAMPTZ,
    rolled_back_at TIMESTAMPTZ,
    health_check_passed BOOLEAN,
    health_metrics JSONB DEFAULT '{}'::jsonb,
    feature_flags JSONB DEFAULT '[]'::jsonb,
    schema_changes JSONB DEFAULT '[]'::jsonb,
    rollback_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.releases ENABLE ROW LEVEL SECURITY;

-- Only admins can manage releases
CREATE POLICY "Admins can manage releases"
ON public.releases FOR ALL
TO authenticated
USING (public.has_role(auth.uid(), 'admin'))
WITH CHECK (public.has_role(auth.uid(), 'admin'));

-- Incident log table for detailed incident tracking
CREATE TABLE IF NOT EXISTS public.incident_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_type TEXT NOT NULL CHECK (incident_type IN (
        'auth_failure', 'permission_violation', 'payment_webhook_failure',
        'rate_limit_breach', 'internal_exception', 'circuit_breaker',
        'backup_failure', 'health_check_failure', 'deploy_failure'
    )),
    severity TEXT NOT NULL CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    request_id TEXT,
    reason TEXT NOT NULL,
    auto_action TEXT CHECK (auto_action IN ('retry', 'circuit_break', 'temporary_block', 'module_shutdown', 'alert_only')),
    action_result TEXT,
    resolved BOOLEAN DEFAULT false,
    resolved_at TIMESTAMPTZ,
    resolved_by TEXT,
    user_id UUID,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.incident_log ENABLE ROW LEVEL SECURITY;

-- Users can view their own incidents, admins can view all
CREATE POLICY "Users view own incidents"
ON public.incident_log FOR SELECT
TO authenticated
USING (user_id = auth.uid() OR public.has_role(auth.uid(), 'admin'));

-- Only service role can insert
CREATE POLICY "Service role logs incidents"
ON public.incident_log FOR INSERT
TO authenticated
WITH CHECK (true);

-- Admins can update (resolve incidents)
CREATE POLICY "Admins can resolve incidents"
ON public.incident_log FOR UPDATE
TO authenticated
USING (public.has_role(auth.uid(), 'admin'))
WITH CHECK (public.has_role(auth.uid(), 'admin'));

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_incident_log_type ON public.incident_log(incident_type);
CREATE INDEX IF NOT EXISTS idx_incident_log_severity ON public.incident_log(severity);
CREATE INDEX IF NOT EXISTS idx_incident_log_created_at ON public.incident_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_backup_metadata_created_at ON public.backup_metadata(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_releases_version ON public.releases(version);