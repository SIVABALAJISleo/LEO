-- Fix module_status table - add missing columns that system-bootstrap expects
ALTER TABLE public.module_status 
ADD COLUMN IF NOT EXISTS config jsonb DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS version text,
ADD COLUMN IF NOT EXISTS error_count integer DEFAULT 0,
ADD COLUMN IF NOT EXISTS success_count integer DEFAULT 0;

-- Comment on the new columns
COMMENT ON COLUMN public.module_status.config IS 'Module-specific configuration settings';
COMMENT ON COLUMN public.module_status.version IS 'Current version of the module';
COMMENT ON COLUMN public.module_status.error_count IS 'Number of errors encountered';
COMMENT ON COLUMN public.module_status.success_count IS 'Number of successful operations';

-- Fix system_metrics status constraint to allow more valid statuses
ALTER TABLE public.system_metrics DROP CONSTRAINT IF EXISTS system_metrics_status_check;

ALTER TABLE public.system_metrics 
ADD CONSTRAINT system_metrics_status_check 
CHECK (status = ANY (ARRAY['healthy'::text, 'warning'::text, 'critical'::text, 'active'::text, 'idle'::text, 'offline'::text]));

-- Create index for better performance on module lookups
CREATE INDEX IF NOT EXISTS idx_module_status_user_module 
ON public.module_status(user_id, module_name);