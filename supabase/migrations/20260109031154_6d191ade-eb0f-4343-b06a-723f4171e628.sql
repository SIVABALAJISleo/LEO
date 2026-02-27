-- Add signature verification and processing tracking to payment_webhook_events
ALTER TABLE public.payment_webhook_events 
ADD COLUMN IF NOT EXISTS signature_verified BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS processed BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS processed_at TIMESTAMPTZ;

-- Create index for idempotency lookups
CREATE INDEX IF NOT EXISTS idx_payment_webhook_events_event_id_processed 
ON public.payment_webhook_events(event_id, processed);

-- Create execution_audit_log table for deterministic pipeline tracking
CREATE TABLE IF NOT EXISTS public.execution_audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workload_id TEXT NOT NULL,
  workload_type TEXT NOT NULL,
  selected_path TEXT NOT NULL,
  path_reason TEXT NOT NULL,
  confidence NUMERIC(5,4) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
  outcome TEXT NOT NULL,
  outcome_reason TEXT NOT NULL,
  latency_ms INTEGER NOT NULL,
  gpu_avoided BOOLEAN DEFAULT false,
  surrogate_used BOOLEAN DEFAULT false,
  authority_required BOOLEAN DEFAULT false,
  authority_status TEXT,
  input_hash TEXT NOT NULL,
  output_hash TEXT,
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.execution_audit_log ENABLE ROW LEVEL SECURITY;

-- Users can only view their own execution logs
CREATE POLICY "Users can view their own execution logs"
ON public.execution_audit_log FOR SELECT
TO authenticated
USING (user_id = auth.uid() OR public.has_role(auth.uid(), 'admin'));

-- Only system (service role) can insert execution logs
-- No direct user inserts allowed
CREATE POLICY "System can insert execution logs"
ON public.execution_audit_log FOR INSERT
TO authenticated
WITH CHECK (false);

-- Create alert_rules table for observability-as-code
CREATE TABLE IF NOT EXISTS public.alert_rules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  description TEXT,
  metric_name TEXT NOT NULL,
  condition TEXT NOT NULL, -- 'gt', 'lt', 'eq', 'gte', 'lte'
  threshold NUMERIC NOT NULL,
  severity TEXT NOT NULL DEFAULT 'warning' CHECK (severity IN ('info', 'warning', 'error', 'critical')),
  is_active BOOLEAN DEFAULT true,
  notification_channels JSONB DEFAULT '[]'::jsonb,
  cooldown_minutes INTEGER DEFAULT 15,
  last_triggered_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.alert_rules ENABLE ROW LEVEL SECURITY;

-- Only admins can manage alert rules
CREATE POLICY "Admins can manage alert rules"
ON public.alert_rules FOR ALL
TO authenticated
USING (public.has_role(auth.uid(), 'admin'))
WITH CHECK (public.has_role(auth.uid(), 'admin'));

-- Create automated_alerts table for triggered alerts
CREATE TABLE IF NOT EXISTS public.automated_alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  rule_id UUID REFERENCES public.alert_rules(id) ON DELETE CASCADE,
  metric_name TEXT NOT NULL,
  metric_value NUMERIC NOT NULL,
  threshold NUMERIC NOT NULL,
  severity TEXT NOT NULL,
  message TEXT NOT NULL,
  acknowledged BOOLEAN DEFAULT false,
  acknowledged_by UUID REFERENCES auth.users(id),
  acknowledged_at TIMESTAMPTZ,
  resolved BOOLEAN DEFAULT false,
  resolved_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.automated_alerts ENABLE ROW LEVEL SECURITY;

-- Users can view alerts, admins can manage
CREATE POLICY "Users can view automated alerts"
ON public.automated_alerts FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Admins can update automated alerts"
ON public.automated_alerts FOR UPDATE
TO authenticated
USING (public.has_role(auth.uid(), 'admin'))
WITH CHECK (public.has_role(auth.uid(), 'admin'));

-- Insert default alert rules
INSERT INTO public.alert_rules (name, metric_name, condition, threshold, severity, description) VALUES
  ('High Payment Failures', 'payment_webhook_failures', 'gt', 5, 'error', 'Triggers when payment webhook failures exceed threshold'),
  ('Rate Limit Violations', 'rate_limit_violations', 'gt', 10, 'warning', 'Triggers when rate limit violations exceed threshold'),
  ('Cost Ceiling Warning', 'daily_cost_usd', 'gt', 80, 'warning', 'Triggers when daily cost approaches ceiling'),
  ('Circuit Breaker Open', 'circuit_breaker_open', 'eq', 1, 'critical', 'Triggers when circuit breaker opens'),
  ('High Latency', 'avg_latency_ms', 'gt', 5000, 'warning', 'Triggers when average latency exceeds 5 seconds'),
  ('Security Denials', 'security_denials', 'gt', 3, 'error', 'Triggers on repeated security policy violations')
ON CONFLICT DO NOTHING;