CREATE EXTENSION IF NOT EXISTS "pg_graphql" WITH SCHEMA "graphql";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements" WITH SCHEMA "extensions";
CREATE EXTENSION IF NOT EXISTS "pgcrypto" WITH SCHEMA "extensions";
CREATE EXTENSION IF NOT EXISTS "plpgsql" WITH SCHEMA "pg_catalog";
CREATE EXTENSION IF NOT EXISTS "supabase_vault" WITH SCHEMA "vault";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA "extensions";
BEGIN;

--
-- PostgreSQL database dump
--


-- Dumped from database version 17.6
-- Dumped by pg_dump version 18.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--



--
-- Name: app_role; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.app_role AS ENUM (
    'admin',
    'user',
    'enterprise'
);


--
-- Name: job_tier; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.job_tier AS ENUM (
    'light',
    'medium',
    'heavy'
);


--
-- Name: handle_new_user(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.handle_new_user() RETURNS trigger
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'public'
    AS $$
BEGIN
  -- Insert profile
  INSERT INTO public.profiles (user_id, full_name)
  VALUES (NEW.id, NEW.raw_user_meta_data->>'full_name');
  
  -- Insert default role
  INSERT INTO public.user_roles (user_id, role)
  VALUES (NEW.id, 'user');
  
  -- Insert default subscription
  INSERT INTO public.subscriptions (user_id, tier, api_calls_limit)
  VALUES (NEW.id, 'free', 100);
  
  RETURN NEW;
END;
$$;


--
-- Name: has_role(uuid, public.app_role); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.has_role(_user_id uuid, _role public.app_role) RETURNS boolean
    LANGUAGE sql STABLE SECURITY DEFINER
    SET search_path TO 'public'
    AS $$
  SELECT EXISTS (
    SELECT 1
    FROM public.user_roles
    WHERE user_id = _user_id AND role = _role
  )
$$;


--
-- Name: hash_api_key(text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.hash_api_key(key_value text) RETURNS text
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'public', 'extensions'
    AS $$
BEGIN
  -- Use bcrypt with cost factor 10 for secure hashing
  RETURN extensions.crypt(key_value, extensions.gen_salt('bf', 10));
END;
$$;


--
-- Name: is_team_member(uuid, uuid); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.is_team_member(_user_id uuid, _team_id uuid) RETURNS boolean
    LANGUAGE sql STABLE SECURITY DEFINER
    SET search_path TO 'public'
    AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.teams
    WHERE id = _team_id 
    AND (owner_id = _user_id OR EXISTS (
      SELECT 1 FROM public.team_members 
      WHERE team_id = _team_id AND user_id = _user_id
    ))
  )
$$;


--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    SET search_path TO 'public'
    AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$;


--
-- Name: validate_api_key(text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_api_key(key_to_validate text) RETURNS uuid
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'public', 'extensions'
    AS $$
DECLARE
  found_user_id uuid;
  key_record RECORD;
  is_valid boolean;
BEGIN
  -- Input validation: reject NULL, empty, or excessively long keys
  IF key_to_validate IS NULL OR length(key_to_validate) < 10 OR length(key_to_validate) > 200 THEN
    RETURN NULL;
  END IF;
  
  -- Input validation: API keys should start with 'hyper_' prefix
  IF NOT key_to_validate LIKE 'hyper_%' THEN
    RETURN NULL;
  END IF;

  -- Loop through active keys and check each one
  -- This is necessary because bcrypt hashes are salted and can't be compared directly
  FOR key_record IN 
    SELECT user_id, key_hash 
    FROM public.api_keys
    WHERE is_active = true
      AND (expires_at IS NULL OR expires_at > now())
  LOOP
    -- Use verify_api_key to check (handles both bcrypt and legacy SHA-256)
    is_valid := public.verify_api_key(key_to_validate, key_record.key_hash);
    
    IF is_valid THEN
      found_user_id := key_record.user_id;
      
      -- Update last_used_at
      UPDATE public.api_keys
      SET last_used_at = now()
      WHERE user_id = found_user_id 
        AND key_hash = key_record.key_hash;
      
      EXIT; -- Found valid key, stop searching
    END IF;
  END LOOP;
  
  RETURN found_user_id;
END;
$$;


--
-- Name: verify_api_key(text, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.verify_api_key(provided_key text, stored_hash text) RETURNS boolean
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'public', 'extensions'
    AS $_$
BEGIN
  -- Handle different hash formats
  IF stored_hash IS NULL OR provided_key IS NULL THEN
    RETURN false;
  END IF;
  
  -- Bcrypt hashes start with $2a$, $2b$, or $2y$
  IF stored_hash LIKE '$2%' THEN 
    RETURN extensions.crypt(provided_key, stored_hash) = stored_hash;
  -- Legacy SHA-256 hashes are hex encoded (64 chars)
  ELSIF length(stored_hash) = 64 THEN 
    RETURN encode(sha256(provided_key::bytea), 'hex') = stored_hash;
  ELSE 
    RETURN false;
  END IF;
END;
$_$;


SET default_table_access_method = heap;

--
-- Name: agent_heartbeats; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.agent_heartbeats (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    agent_token_id uuid,
    worker_id text NOT NULL,
    gpu_temp_celsius integer,
    gpu_vram_used_mb integer,
    gpu_vram_total_mb integer,
    cpu_temp_celsius integer,
    cpu_usage_percent numeric,
    is_processing boolean DEFAULT false,
    current_job_id uuid,
    recorded_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: agent_tokens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.agent_tokens (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    agent_name text NOT NULL,
    secret_hash text NOT NULL,
    allowed_until timestamp with time zone,
    is_active boolean DEFAULT true,
    last_used_at timestamp with time zone,
    capabilities jsonb DEFAULT '{"max_vram_mb": 24576, "supports_heavy": true}'::jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: alerts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alerts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    alert_type text NOT NULL,
    severity text DEFAULT 'info'::text NOT NULL,
    title text NOT NULL,
    message text NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb,
    resolved boolean DEFAULT false NOT NULL,
    resolved_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    module_name text
);


--
-- Name: analytics_dashboards; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.analytics_dashboards (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    name text NOT NULL,
    description text,
    layout jsonb DEFAULT '{}'::jsonb,
    widgets jsonb DEFAULT '[]'::jsonb,
    is_default boolean DEFAULT false,
    is_shared boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: analytics_events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.analytics_events (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid,
    event_type text NOT NULL,
    event_data jsonb DEFAULT '{}'::jsonb,
    page_path text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: analytics_reports; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.analytics_reports (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    name text NOT NULL,
    description text,
    report_type text NOT NULL,
    config jsonb DEFAULT '{}'::jsonb,
    schedule text,
    last_generated_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: anomalies; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.anomalies (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    metric_name text NOT NULL,
    anomaly_type text NOT NULL,
    severity text DEFAULT 'medium'::text NOT NULL,
    expected_value double precision,
    actual_value double precision,
    deviation_percent double precision,
    is_resolved boolean DEFAULT false,
    resolved_at timestamp with time zone,
    detected_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: api_keys; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.api_keys (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    key_name text NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    last_used_at timestamp with time zone,
    expires_at timestamp with time zone,
    key_hash text,
    key_prefix text
);


--
-- Name: api_keys_safe; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.api_keys_safe WITH (security_invoker='true') AS
 SELECT id,
    user_id,
    key_name,
    key_prefix,
    is_active,
    created_at,
    last_used_at,
    expires_at
   FROM public.api_keys;


--
-- Name: approval_workflows; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.approval_workflows (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    team_id uuid,
    name text NOT NULL,
    description text,
    workflow_type text NOT NULL,
    steps jsonb DEFAULT '[]'::jsonb,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: backup_metadata; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backup_metadata (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    backup_type text NOT NULL,
    size_bytes bigint,
    location text,
    region text,
    status text DEFAULT 'pending'::text,
    retention_days integer DEFAULT 30,
    encrypted boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone
);


--
-- Name: billing_cost_predictions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.billing_cost_predictions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    month text NOT NULL,
    predicted_cost double precision DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: billing_subscriptions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.billing_subscriptions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    plan text DEFAULT 'free'::text NOT NULL,
    status text DEFAULT 'active'::text NOT NULL,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    renewed_at timestamp with time zone,
    cancelled_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT billing_subscriptions_plan_check CHECK ((plan = ANY (ARRAY['free'::text, 'pro'::text, 'enterprise'::text]))),
    CONSTRAINT billing_subscriptions_status_check CHECK ((status = ANY (ARRAY['active'::text, 'cancelled'::text, 'trial'::text])))
);


--
-- Name: billing_usage_records; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.billing_usage_records (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    month text NOT NULL,
    inference_tokens bigint DEFAULT 0,
    training_hours double precision DEFAULT 0,
    rendering_hours double precision DEFAULT 0,
    storage_gb double precision DEFAULT 0,
    computed_cost double precision DEFAULT 0,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: budget_allocations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.budget_allocations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    name text NOT NULL,
    total_budget double precision NOT NULL,
    spent_amount double precision DEFAULT 0,
    alert_threshold double precision DEFAULT 80,
    period_start date NOT NULL,
    period_end date NOT NULL,
    category text,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: cache_analytics; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cache_analytics (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    cache_level text NOT NULL,
    hits integer DEFAULT 0,
    misses integer DEFAULT 0,
    evictions integer DEFAULT 0,
    avg_response_time_saved_ms integer,
    total_size_bytes bigint DEFAULT 0,
    recorded_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: cache_invalidation_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cache_invalidation_log (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    cache_level text NOT NULL,
    invalidation_type text NOT NULL,
    affected_keys integer,
    reason text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: cache_metadata; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cache_metadata (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    cache_key text NOT NULL,
    cache_level text NOT NULL,
    content_type text,
    size_bytes integer,
    hit_count integer DEFAULT 0,
    last_accessed_at timestamp with time zone DEFAULT now(),
    expires_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: cache_warming_jobs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cache_warming_jobs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    job_type text NOT NULL,
    status text DEFAULT 'pending'::text NOT NULL,
    target_cache_level text,
    items_to_warm integer,
    items_warmed integer DEFAULT 0,
    trigger_reason text,
    started_at timestamp with time zone,
    completed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: cloud_costs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cloud_costs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    provider_id uuid,
    resource_type text NOT NULL,
    cost_per_hour double precision,
    cost_per_request double precision,
    recorded_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: cloud_failover_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cloud_failover_log (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    from_provider_id uuid,
    to_provider_id uuid,
    reason text NOT NULL,
    duration_ms integer,
    success boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: cloud_latencies; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cloud_latencies (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    provider_id uuid,
    endpoint_type text NOT NULL,
    latency_ms integer NOT NULL,
    success boolean DEFAULT true,
    recorded_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: cloud_providers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cloud_providers (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    provider_name text NOT NULL,
    region text NOT NULL,
    is_active boolean DEFAULT true,
    credentials_configured boolean DEFAULT false,
    capabilities jsonb DEFAULT '{}'::jsonb,
    priority integer DEFAULT 5,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: cloud_routing_rules; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cloud_routing_rules (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    name text NOT NULL,
    mode text DEFAULT 'balanced'::text NOT NULL,
    conditions jsonb DEFAULT '{}'::jsonb,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: collaboration_changes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.collaboration_changes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    session_id uuid NOT NULL,
    user_id uuid NOT NULL,
    change_type text NOT NULL,
    target_module text,
    previous_value jsonb,
    new_value jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: collaboration_comments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.collaboration_comments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    session_id uuid NOT NULL,
    user_id uuid NOT NULL,
    parent_id uuid,
    module_name text,
    content text NOT NULL,
    mentions uuid[],
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: collaboration_messages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.collaboration_messages (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    session_id uuid NOT NULL,
    user_id uuid NOT NULL,
    content text NOT NULL,
    mentions uuid[],
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: collaboration_participants; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.collaboration_participants (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    session_id uuid NOT NULL,
    user_id uuid NOT NULL,
    role text DEFAULT 'viewer'::text NOT NULL,
    joined_at timestamp with time zone DEFAULT now() NOT NULL,
    last_active_at timestamp with time zone DEFAULT now(),
    cursor_position jsonb,
    is_online boolean DEFAULT false
);


--
-- Name: collaboration_sessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.collaboration_sessions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    room_id text NOT NULL,
    name text NOT NULL,
    description text,
    owner_id uuid NOT NULL,
    inference_job_id uuid,
    status text DEFAULT 'active'::text NOT NULL,
    settings jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    archived_at timestamp with time zone
);


--
-- Name: collaboration_votes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.collaboration_votes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    session_id uuid NOT NULL,
    user_id uuid NOT NULL,
    vote_type text NOT NULL,
    target_id uuid,
    value integer DEFAULT 1 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: compliance_checks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.compliance_checks (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    check_name text NOT NULL,
    framework text NOT NULL,
    status text DEFAULT 'pending'::text NOT NULL,
    score double precision,
    findings jsonb DEFAULT '[]'::jsonb,
    last_run_at timestamp with time zone,
    next_run_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: correlations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.correlations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    metric_a text NOT NULL,
    metric_b text NOT NULL,
    correlation_coefficient double precision,
    relationship_type text,
    confidence double precision,
    sample_size integer,
    calculated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: cost_analysis; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cost_analysis (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    period_start timestamp with time zone NOT NULL,
    period_end timestamp with time zone NOT NULL,
    resource_type text NOT NULL,
    actual_cost double precision,
    optimized_cost double precision,
    savings double precision,
    roi double precision,
    recommendations jsonb DEFAULT '[]'::jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: cost_predictions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cost_predictions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    resource_type text NOT NULL,
    predicted_amount double precision NOT NULL,
    confidence_lower double precision,
    confidence_upper double precision,
    prediction_period text NOT NULL,
    prediction_date date NOT NULL,
    model_version text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: cost_transactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cost_transactions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    resource_type text NOT NULL,
    resource_id text,
    amount double precision NOT NULL,
    currency text DEFAULT 'USD'::text,
    provider text,
    category text,
    tags jsonb DEFAULT '{}'::jsonb,
    transaction_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: custom_roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.custom_roles (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    team_id uuid,
    name text NOT NULL,
    description text,
    permissions jsonb DEFAULT '[]'::jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: custom_visualizations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.custom_visualizations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    dashboard_id uuid,
    name text NOT NULL,
    visualization_type text NOT NULL,
    data_source jsonb DEFAULT '{}'::jsonb,
    config jsonb DEFAULT '{}'::jsonb,
    "position" jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: device_registry; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.device_registry (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    device_name text NOT NULL,
    device_type text DEFAULT 'gpu_worker'::text NOT NULL,
    device_token text NOT NULL,
    capabilities jsonb DEFAULT '{}'::jsonb,
    is_active boolean DEFAULT true,
    last_seen_at timestamp with time zone,
    registered_at timestamp with time zone DEFAULT now(),
    metadata jsonb DEFAULT '{}'::jsonb
);


--
-- Name: distillation_jobs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.distillation_jobs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    distilled_model_id uuid,
    distillation_type text NOT NULL,
    stage integer DEFAULT 1 NOT NULL,
    status text DEFAULT 'queued'::text NOT NULL,
    priority integer DEFAULT 5 NOT NULL,
    progress integer DEFAULT 0,
    config jsonb DEFAULT '{}'::jsonb,
    metrics jsonb DEFAULT '{}'::jsonb,
    error_message text,
    started_at timestamp with time zone,
    completed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: distillation_metrics; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.distillation_metrics (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    distillation_job_id uuid,
    epoch integer NOT NULL,
    loss double precision,
    accuracy double precision,
    alignment_score double precision,
    teacher_latency_ms integer,
    student_latency_ms integer,
    recorded_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: distilled_models; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.distilled_models (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    name text NOT NULL,
    description text,
    teacher_model_id uuid,
    model_type text DEFAULT 'general'::text NOT NULL,
    specialization text,
    current_stage integer DEFAULT 1 NOT NULL,
    status text DEFAULT 'pending'::text NOT NULL,
    accuracy double precision,
    latency_ms integer,
    memory_mb integer,
    compression_ratio double precision,
    parameters jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: distributed_training_jobs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.distributed_training_jobs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    name text NOT NULL,
    model_id uuid,
    config jsonb DEFAULT '{}'::jsonb,
    mixed_precision boolean DEFAULT true,
    gradient_compression boolean DEFAULT true,
    model_sharding boolean DEFAULT false,
    node_count integer DEFAULT 1,
    status text DEFAULT 'pending'::text,
    progress integer DEFAULT 0,
    speedup_vs_rtx5090 double precision,
    started_at timestamp with time zone,
    completed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: enterprise_requests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.enterprise_requests (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    name text NOT NULL,
    email text NOT NULL,
    company text,
    role text,
    expected_workload text,
    budget_range text,
    message text,
    status text DEFAULT 'new'::text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT enterprise_requests_status_check CHECK ((status = ANY (ARRAY['new'::text, 'in_review'::text, 'contacted'::text, 'closed'::text])))
);


--
-- Name: error_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.error_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid,
    error_message text NOT NULL,
    stack_trace text,
    component_name text,
    job_id uuid,
    module_name text,
    metadata jsonb DEFAULT '{}'::jsonb,
    severity text DEFAULT 'error'::text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: expectation_locks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.expectation_locks (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    lock_type text NOT NULL,
    lock_count integer DEFAULT 1,
    locked_at timestamp with time zone DEFAULT now(),
    lock_message text,
    unlocked_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT expectation_locks_lock_type_check CHECK ((lock_type = ANY (ARRAY['instant_demand'::text, 'exact_demand'::text, 'heavy_demand'::text, 'free_demand'::text])))
);


--
-- Name: failover_events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.failover_events (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    from_region text NOT NULL,
    to_region text NOT NULL,
    trigger_reason text NOT NULL,
    duration_ms integer,
    data_loss_bytes bigint DEFAULT 0,
    success boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: fused_models; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fused_models (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    name text NOT NULL,
    description text,
    source_model_ids uuid[] DEFAULT '{}'::uuid[],
    fusion_strategy text DEFAULT 'late'::text NOT NULL,
    status text DEFAULT 'pending'::text NOT NULL,
    accuracy double precision,
    latency_ms integer,
    parameters jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: fusion_performance_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fusion_performance_log (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    fused_model_id uuid,
    accuracy_before double precision,
    accuracy_after double precision,
    latency_before_ms integer,
    latency_after_ms integer,
    improvement_percent double precision,
    recorded_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: fusion_strategies; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fusion_strategies (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    name text NOT NULL,
    strategy_type text NOT NULL,
    config jsonb DEFAULT '{}'::jsonb,
    weight_distribution jsonb DEFAULT '{}'::jsonb,
    conflict_resolution text DEFAULT 'weighted_average'::text,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: gpu_jobs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.gpu_jobs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    job_type text NOT NULL,
    job_name text,
    payload jsonb DEFAULT '{}'::jsonb NOT NULL,
    status text DEFAULT 'pending'::text NOT NULL,
    priority integer DEFAULT 5 NOT NULL,
    memory_required_mb integer,
    estimated_duration_sec integer,
    progress integer DEFAULT 0,
    result_url text,
    result_data jsonb,
    error_message text,
    checkpoint_data jsonb,
    checkpoint_at timestamp with time zone,
    worker_id text,
    worker_signature text,
    thermal_paused boolean DEFAULT false,
    started_at timestamp with time zone,
    completed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    job_tier text DEFAULT 'heavy'::text,
    retry_count integer DEFAULT 0,
    max_retries integer DEFAULT 3,
    eta_seconds integer,
    CONSTRAINT valid_status CHECK ((status = ANY (ARRAY['pending'::text, 'queued'::text, 'running'::text, 'paused'::text, 'completed'::text, 'failed'::text, 'too_large'::text, 'cancelled'::text])))
);


--
-- Name: gpu_system_status; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.gpu_system_status (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    worker_id text NOT NULL,
    gpu_temperature_celsius double precision,
    gpu_memory_used_mb integer,
    gpu_memory_total_mb integer,
    gpu_utilization_percent double precision,
    cpu_temperature_celsius double precision,
    cpu_utilization_percent double precision,
    is_online boolean DEFAULT true,
    is_thermal_throttled boolean DEFAULT false,
    active_job_id uuid,
    jobs_completed_today integer DEFAULT 0,
    jobs_failed_today integer DEFAULT 0,
    last_heartbeat_at timestamp with time zone DEFAULT now(),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: graphics_benchmarks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.graphics_benchmarks (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    name text NOT NULL,
    scene_complexity text DEFAULT 'medium'::text,
    resolution text DEFAULT '1920x1080'::text,
    your_engine_fps double precision,
    rtx5090_fps double precision,
    comparison_percent double precision,
    ai_enhancement_enabled boolean DEFAULT true,
    settings jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: immutable_audit_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.immutable_audit_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid,
    action text NOT NULL,
    resource_type text NOT NULL,
    resource_id text,
    old_value jsonb,
    new_value jsonb,
    ip_address text,
    user_agent text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: incidents; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.incidents (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    title text NOT NULL,
    description text,
    severity text DEFAULT 'medium'::text NOT NULL,
    status text DEFAULT 'open'::text NOT NULL,
    affected_services jsonb DEFAULT '[]'::jsonb,
    root_cause text,
    resolution text,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    resolved_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: inference_jobs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.inference_jobs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    model_id uuid NOT NULL,
    input_data jsonb NOT NULL,
    output_data jsonb,
    enabled_modules jsonb DEFAULT '[]'::jsonb,
    optimization_options jsonb DEFAULT '{}'::jsonb,
    status text DEFAULT 'queued'::text NOT NULL,
    priority integer DEFAULT 5 NOT NULL,
    progress integer DEFAULT 0,
    error_message text,
    started_at timestamp with time zone,
    completed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    latency_ms integer,
    speedup double precision,
    compression_ratio double precision
);


--
-- Name: integrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.integrations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    plugin_id uuid,
    name text NOT NULL,
    integration_type text NOT NULL,
    config jsonb DEFAULT '{}'::jsonb,
    credentials_configured boolean DEFAULT false,
    is_active boolean DEFAULT true,
    last_sync_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: job_final_states; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.job_final_states (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    job_id uuid NOT NULL,
    user_id uuid NOT NULL,
    final_state text NOT NULL,
    confidence_score numeric(5,2),
    processing_method text,
    is_approximate boolean DEFAULT false,
    checkpoint_available boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    resolved_at timestamp with time zone,
    CONSTRAINT job_final_states_final_state_check CHECK ((final_state = ANY (ARRAY['instantly_served'::text, 'approximation_accepted'::text, 'exact_computing'::text, 'deferred_by_design'::text, 'paused_resumable'::text, 'user_cancelled'::text])))
);


--
-- Name: job_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.job_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    job_id uuid NOT NULL,
    level text DEFAULT 'info'::text NOT NULL,
    message text NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb,
    ts timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: job_queue; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.job_queue (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    job_id uuid NOT NULL,
    priority integer DEFAULT 5 NOT NULL,
    enqueued_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: job_results; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.job_results (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    job_id uuid NOT NULL,
    log text,
    artifacts_json jsonb DEFAULT '[]'::jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: jobs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.jobs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    job_type text NOT NULL,
    status text DEFAULT 'pending'::text NOT NULL,
    priority text DEFAULT 'normal'::text NOT NULL,
    input_data jsonb,
    output_data jsonb,
    progress integer DEFAULT 0,
    error_message text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    started_at timestamp with time zone,
    completed_at timestamp with time zone
);


--
-- Name: knowledge_transfer_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.knowledge_transfer_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    distillation_job_id uuid,
    layer_name text NOT NULL,
    transfer_type text NOT NULL,
    alignment_before double precision,
    alignment_after double precision,
    loss_reduction double precision,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: marketplace_transactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.marketplace_transactions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    plugin_id uuid,
    transaction_type text NOT NULL,
    amount double precision NOT NULL,
    currency text DEFAULT 'USD'::text,
    status text DEFAULT 'pending'::text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: metrics_aggregated; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.metrics_aggregated (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    metric_name text NOT NULL,
    aggregation_type text DEFAULT 'avg'::text NOT NULL,
    value_min double precision,
    value_max double precision,
    value_avg double precision,
    value_sum double precision,
    sample_count integer,
    period_start timestamp with time zone NOT NULL,
    period_end timestamp with time zone NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: metrics_raw; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.metrics_raw (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    metric_name text NOT NULL,
    metric_value double precision NOT NULL,
    tags jsonb DEFAULT '{}'::jsonb,
    source text,
    recorded_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: models; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.models (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    name text NOT NULL,
    description text,
    model_type text NOT NULL,
    version text NOT NULL,
    parameters jsonb DEFAULT '{}'::jsonb,
    storage_path text,
    status text DEFAULT 'active'::text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    file_path text,
    size_mb integer,
    is_public boolean DEFAULT false
);


--
-- Name: module_configs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.module_configs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    module_name text NOT NULL,
    module_type text NOT NULL,
    enabled boolean DEFAULT true NOT NULL,
    config jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    settings jsonb DEFAULT '{}'::jsonb,
    speedup_achieved double precision,
    compression_ratio_achieved double precision
);


--
-- Name: module_locks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.module_locks (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    session_id uuid NOT NULL,
    module_name text NOT NULL,
    locked_by uuid NOT NULL,
    locked_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone DEFAULT (now() + '00:05:00'::interval) NOT NULL
);


--
-- Name: module_status; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.module_status (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    module_name text NOT NULL,
    status text DEFAULT 'idle'::text NOT NULL,
    current_job_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    health_score double precision DEFAULT 100,
    last_checked timestamp with time zone DEFAULT now(),
    error_message text
);


--
-- Name: offline_packages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.offline_packages (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    name text NOT NULL,
    description text,
    models jsonb DEFAULT '[]'::jsonb,
    total_size_mb double precision,
    estimated_latency_ms integer,
    compression_level text DEFAULT 'medium'::text,
    status text DEFAULT 'building'::text,
    download_url text,
    expires_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: owner_diagnostics; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.owner_diagnostics (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    diagnostic_date date DEFAULT CURRENT_DATE NOT NULL,
    instant_percent numeric(5,2) DEFAULT 0,
    approximate_percent numeric(5,2) DEFAULT 0,
    exact_percent numeric(5,2) DEFAULT 0,
    deferred_percent numeric(5,2) DEFAULT 0,
    total_requests integer DEFAULT 0,
    compression_ratio numeric(8,2),
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: payment_webhook_events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.payment_webhook_events (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    provider text NOT NULL,
    event_type text NOT NULL,
    event_id text NOT NULL,
    payload jsonb NOT NULL,
    processed boolean DEFAULT false,
    error_message text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: payments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.payments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    provider text NOT NULL,
    amount numeric(12,2) NOT NULL,
    currency text DEFAULT 'INR'::text NOT NULL,
    plan text NOT NULL,
    billing_cycle text DEFAULT 'monthly'::text,
    status text DEFAULT 'pending'::text NOT NULL,
    transaction_id text,
    provider_payment_id text,
    provider_customer_id text,
    metadata jsonb DEFAULT '{}'::jsonb,
    webhook_received_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT payments_billing_cycle_check CHECK ((billing_cycle = ANY (ARRAY['monthly'::text, 'yearly'::text]))),
    CONSTRAINT payments_plan_check CHECK ((plan = ANY (ARRAY['free'::text, 'pro'::text, 'enterprise'::text]))),
    CONSTRAINT payments_provider_check CHECK ((provider = ANY (ARRAY['stripe'::text, 'razorpay'::text]))),
    CONSTRAINT payments_status_check CHECK ((status = ANY (ARRAY['pending'::text, 'succeeded'::text, 'failed'::text, 'refunded'::text])))
);


--
-- Name: performance_metrics; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.performance_metrics (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    job_id uuid,
    model_id uuid,
    module_name text,
    metric_name text NOT NULL,
    metric_value numeric NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb,
    recorded_at timestamp with time zone DEFAULT now() NOT NULL,
    cpu_usage_percent double precision,
    memory_mb integer,
    latency_ms integer,
    throughput_rps double precision,
    cache_hit_ratio double precision
);


--
-- Name: permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.permissions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    role_id uuid,
    resource text NOT NULL,
    action text NOT NULL,
    conditions jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: persistent_compute_jobs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.persistent_compute_jobs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    name text NOT NULL,
    job_type text NOT NULL,
    checkpoint_interval_min integer DEFAULT 30,
    max_duration_hours integer DEFAULT 48,
    current_checkpoint jsonb DEFAULT '{}'::jsonb,
    recovery_count integer DEFAULT 0,
    failure_tolerance text DEFAULT 'high'::text,
    status text DEFAULT 'pending'::text,
    started_at timestamp with time zone,
    last_checkpoint_at timestamp with time zone,
    completed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: personalization_settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.personalization_settings (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    theme_preference text DEFAULT 'dark'::text,
    layout_preference text DEFAULT 'default'::text,
    notification_preferences jsonb DEFAULT '{}'::jsonb,
    dashboard_config jsonb DEFAULT '{}'::jsonb,
    feature_flags jsonb DEFAULT '{}'::jsonb,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: plugins; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.plugins (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    description text,
    author_id uuid NOT NULL,
    version text DEFAULT '1.0.0'::text NOT NULL,
    category text,
    icon_url text,
    download_count integer DEFAULT 0,
    rating double precision DEFAULT 0,
    price double precision DEFAULT 0,
    is_published boolean DEFAULT false,
    config_schema jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: prediction_accuracy; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.prediction_accuracy (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    prediction_type text NOT NULL,
    time_horizon text NOT NULL,
    mape double precision,
    rmse double precision,
    accuracy_percent double precision,
    sample_count integer,
    recorded_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: profiles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.profiles (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    full_name text,
    company text,
    avatar_url text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: quantum_benchmarks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.quantum_benchmarks (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    circuit_id uuid,
    quantum_time_ms integer,
    classical_time_ms integer,
    speedup_factor double precision,
    resource_usage jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: quantum_circuits; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.quantum_circuits (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    name text NOT NULL,
    description text,
    circuit_data jsonb DEFAULT '{}'::jsonb NOT NULL,
    algorithm_type text DEFAULT 'custom'::text NOT NULL,
    qubit_count integer DEFAULT 2 NOT NULL,
    gate_count integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: quantum_jobs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.quantum_jobs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    circuit_id uuid,
    status text DEFAULT 'queued'::text NOT NULL,
    priority integer DEFAULT 5 NOT NULL,
    shots integer DEFAULT 1000,
    backend_type text DEFAULT 'simulator'::text,
    started_at timestamp with time zone,
    completed_at timestamp with time zone,
    error_message text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: quantum_results; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.quantum_results (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    job_id uuid,
    measurement_counts jsonb DEFAULT '{}'::jsonb,
    probabilities jsonb DEFAULT '{}'::jsonb,
    execution_time_ms integer,
    fidelity double precision,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: recommendations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.recommendations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    recommendation_type text NOT NULL,
    title text NOT NULL,
    description text,
    action_url text,
    priority integer DEFAULT 5,
    score double precision,
    is_dismissed boolean DEFAULT false,
    dismissed_at timestamp with time zone,
    expires_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: scaling_actions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.scaling_actions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    action_type text NOT NULL,
    resource_type text NOT NULL,
    previous_count integer,
    new_count integer,
    trigger_reason text,
    status text DEFAULT 'pending'::text NOT NULL,
    cost_impact double precision,
    latency_impact double precision,
    executed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: security_events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.security_events (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid,
    event_type text NOT NULL,
    severity text DEFAULT 'info'::text NOT NULL,
    source_ip text,
    user_agent text,
    resource text,
    action text,
    outcome text,
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: semantic_embeddings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.semantic_embeddings (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    query_hash text NOT NULL,
    embedding double precision[],
    cache_key text,
    similarity_threshold double precision DEFAULT 0.95,
    hit_count integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: subscriptions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.subscriptions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    tier text DEFAULT 'free'::text NOT NULL,
    status text DEFAULT 'active'::text NOT NULL,
    api_calls_limit integer DEFAULT 100 NOT NULL,
    api_calls_used integer DEFAULT 0 NOT NULL,
    reset_at timestamp with time zone DEFAULT (now() + '30 days'::interval) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: system_health; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.system_health (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    health_score integer DEFAULT 100,
    status text DEFAULT 'healthy'::text,
    checks_passed integer DEFAULT 0,
    checks_failed integer DEFAULT 0,
    last_check_at timestamp with time zone DEFAULT now(),
    issues jsonb DEFAULT '[]'::jsonb,
    recommendations jsonb DEFAULT '[]'::jsonb,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: system_metrics; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.system_metrics (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    gpu_utilization numeric,
    memory_usage numeric,
    temperature numeric,
    power_draw numeric,
    throughput numeric,
    metadata jsonb DEFAULT '{}'::jsonb,
    recorded_at timestamp with time zone DEFAULT now() NOT NULL,
    cpu_percent double precision,
    disk_gb integer,
    active_jobs integer DEFAULT 0,
    total_requests bigint DEFAULT 0,
    status text DEFAULT 'healthy'::text,
    device_id uuid,
    CONSTRAINT system_metrics_status_check CHECK ((status = ANY (ARRAY['healthy'::text, 'warning'::text, 'critical'::text])))
);


--
-- Name: system_settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.system_settings (
    key text NOT NULL,
    value jsonb NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: team_members; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.team_members (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    team_id uuid,
    user_id uuid NOT NULL,
    role text DEFAULT 'member'::text NOT NULL,
    joined_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: teams; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.teams (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    description text,
    owner_id uuid NOT NULL,
    settings jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: threats_detected; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.threats_detected (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid,
    threat_type text NOT NULL,
    severity text NOT NULL,
    source text,
    target text,
    description text,
    mitigation_status text DEFAULT 'pending'::text,
    mitigated_at timestamp with time zone,
    auto_mitigated boolean DEFAULT false,
    detected_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: traces; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.traces (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    trace_id text NOT NULL,
    span_id text NOT NULL,
    parent_span_id text,
    operation_name text NOT NULL,
    service_name text,
    duration_ms integer,
    status text DEFAULT 'ok'::text,
    tags jsonb DEFAULT '{}'::jsonb,
    logs jsonb DEFAULT '[]'::jsonb,
    started_at timestamp with time zone NOT NULL,
    ended_at timestamp with time zone
);


--
-- Name: usage_stats; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.usage_stats (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    api_key_id uuid,
    operation_type text NOT NULL,
    operation_count integer DEFAULT 1 NOT NULL,
    credits_used numeric(10,2) DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: user_behaviors; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_behaviors (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    behavior_type text NOT NULL,
    action text NOT NULL,
    target text,
    metadata jsonb DEFAULT '{}'::jsonb,
    session_id text,
    recorded_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: user_roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_roles (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    role public.app_role DEFAULT 'user'::public.app_role NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: video_benchmarks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.video_benchmarks (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    name text NOT NULL,
    resolution text DEFAULT '4K'::text,
    framerate integer DEFAULT 30,
    codec text DEFAULT 'H.265'::text,
    keyframe_interval integer DEFAULT 60,
    quality_score double precision,
    latency_ms integer,
    pipeline_config jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: webhook_test_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.webhook_test_log (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    webhook_url text NOT NULL,
    status_code integer,
    success boolean,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: worker_api_keys; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.worker_api_keys (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    key_hash text NOT NULL,
    key_prefix text NOT NULL,
    worker_name text NOT NULL,
    is_active boolean DEFAULT true,
    last_used_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: workload_predictions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.workload_predictions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    prediction_type text NOT NULL,
    time_horizon text NOT NULL,
    predicted_value double precision NOT NULL,
    confidence_lower double precision,
    confidence_upper double precision,
    actual_value double precision,
    is_anomaly boolean DEFAULT false,
    model_version text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    target_time timestamp with time zone NOT NULL
);


--
-- Name: agent_heartbeats agent_heartbeats_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_heartbeats
    ADD CONSTRAINT agent_heartbeats_pkey PRIMARY KEY (id);


--
-- Name: agent_tokens agent_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_tokens
    ADD CONSTRAINT agent_tokens_pkey PRIMARY KEY (id);


--
-- Name: alerts alerts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alerts
    ADD CONSTRAINT alerts_pkey PRIMARY KEY (id);


--
-- Name: analytics_dashboards analytics_dashboards_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.analytics_dashboards
    ADD CONSTRAINT analytics_dashboards_pkey PRIMARY KEY (id);


--
-- Name: analytics_events analytics_events_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.analytics_events
    ADD CONSTRAINT analytics_events_pkey PRIMARY KEY (id);


--
-- Name: analytics_reports analytics_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.analytics_reports
    ADD CONSTRAINT analytics_reports_pkey PRIMARY KEY (id);


--
-- Name: anomalies anomalies_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.anomalies
    ADD CONSTRAINT anomalies_pkey PRIMARY KEY (id);


--
-- Name: api_keys api_keys_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_keys
    ADD CONSTRAINT api_keys_pkey PRIMARY KEY (id);


--
-- Name: approval_workflows approval_workflows_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.approval_workflows
    ADD CONSTRAINT approval_workflows_pkey PRIMARY KEY (id);


--
-- Name: backup_metadata backup_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backup_metadata
    ADD CONSTRAINT backup_metadata_pkey PRIMARY KEY (id);


--
-- Name: billing_cost_predictions billing_cost_predictions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.billing_cost_predictions
    ADD CONSTRAINT billing_cost_predictions_pkey PRIMARY KEY (id);


--
-- Name: billing_subscriptions billing_subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.billing_subscriptions
    ADD CONSTRAINT billing_subscriptions_pkey PRIMARY KEY (id);


--
-- Name: billing_usage_records billing_usage_records_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.billing_usage_records
    ADD CONSTRAINT billing_usage_records_pkey PRIMARY KEY (id);


--
-- Name: budget_allocations budget_allocations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.budget_allocations
    ADD CONSTRAINT budget_allocations_pkey PRIMARY KEY (id);


--
-- Name: cache_analytics cache_analytics_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cache_analytics
    ADD CONSTRAINT cache_analytics_pkey PRIMARY KEY (id);


--
-- Name: cache_invalidation_log cache_invalidation_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cache_invalidation_log
    ADD CONSTRAINT cache_invalidation_log_pkey PRIMARY KEY (id);


--
-- Name: cache_metadata cache_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cache_metadata
    ADD CONSTRAINT cache_metadata_pkey PRIMARY KEY (id);


--
-- Name: cache_warming_jobs cache_warming_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cache_warming_jobs
    ADD CONSTRAINT cache_warming_jobs_pkey PRIMARY KEY (id);


--
-- Name: cloud_costs cloud_costs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cloud_costs
    ADD CONSTRAINT cloud_costs_pkey PRIMARY KEY (id);


--
-- Name: cloud_failover_log cloud_failover_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cloud_failover_log
    ADD CONSTRAINT cloud_failover_log_pkey PRIMARY KEY (id);


--
-- Name: cloud_latencies cloud_latencies_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cloud_latencies
    ADD CONSTRAINT cloud_latencies_pkey PRIMARY KEY (id);


--
-- Name: cloud_providers cloud_providers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cloud_providers
    ADD CONSTRAINT cloud_providers_pkey PRIMARY KEY (id);


--
-- Name: cloud_routing_rules cloud_routing_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cloud_routing_rules
    ADD CONSTRAINT cloud_routing_rules_pkey PRIMARY KEY (id);


--
-- Name: collaboration_changes collaboration_changes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.collaboration_changes
    ADD CONSTRAINT collaboration_changes_pkey PRIMARY KEY (id);


--
-- Name: collaboration_comments collaboration_comments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.collaboration_comments
    ADD CONSTRAINT collaboration_comments_pkey PRIMARY KEY (id);


--
-- Name: collaboration_messages collaboration_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.collaboration_messages
    ADD CONSTRAINT collaboration_messages_pkey PRIMARY KEY (id);


--
-- Name: collaboration_participants collaboration_participants_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.collaboration_participants
    ADD CONSTRAINT collaboration_participants_pkey PRIMARY KEY (id);


--
-- Name: collaboration_sessions collaboration_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.collaboration_sessions
    ADD CONSTRAINT collaboration_sessions_pkey PRIMARY KEY (id);


--
-- Name: collaboration_sessions collaboration_sessions_room_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.collaboration_sessions
    ADD CONSTRAINT collaboration_sessions_room_id_key UNIQUE (room_id);


--
-- Name: collaboration_votes collaboration_votes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.collaboration_votes
    ADD CONSTRAINT collaboration_votes_pkey PRIMARY KEY (id);


--
-- Name: compliance_checks compliance_checks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.compliance_checks
    ADD CONSTRAINT compliance_checks_pkey PRIMARY KEY (id);


--
-- Name: correlations correlations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.correlations
    ADD CONSTRAINT correlations_pkey PRIMARY KEY (id);


--
-- Name: cost_analysis cost_analysis_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cost_analysis
    ADD CONSTRAINT cost_analysis_pkey PRIMARY KEY (id);


--
-- Name: cost_predictions cost_predictions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cost_predictions
    ADD CONSTRAINT cost_predictions_pkey PRIMARY KEY (id);


--
-- Name: cost_transactions cost_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cost_transactions
    ADD CONSTRAINT cost_transactions_pkey PRIMARY KEY (id);


--
-- Name: custom_roles custom_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.custom_roles
    ADD CONSTRAINT custom_roles_pkey PRIMARY KEY (id);


--
-- Name: custom_visualizations custom_visualizations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.custom_visualizations
    ADD CONSTRAINT custom_visualizations_pkey PRIMARY KEY (id);


--
-- Name: device_registry device_registry_device_token_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.device_registry
    ADD CONSTRAINT device_registry_device_token_key UNIQUE (device_token);


--
-- Name: device_registry device_registry_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.device_registry
    ADD CONSTRAINT device_registry_pkey PRIMARY KEY (id);


--
-- Name: distillation_jobs distillation_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.distillation_jobs
    ADD CONSTRAINT distillation_jobs_pkey PRIMARY KEY (id);


--
-- Name: distillation_metrics distillation_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.distillation_metrics
    ADD CONSTRAINT distillation_metrics_pkey PRIMARY KEY (id);


--
-- Name: distilled_models distilled_models_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.distilled_models
    ADD CONSTRAINT distilled_models_pkey PRIMARY KEY (id);


--
-- Name: distributed_training_jobs distributed_training_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.distributed_training_jobs
    ADD CONSTRAINT distributed_training_jobs_pkey PRIMARY KEY (id);


--
-- Name: enterprise_requests enterprise_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.enterprise_requests
    ADD CONSTRAINT enterprise_requests_pkey PRIMARY KEY (id);


--
-- Name: error_logs error_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.error_logs
    ADD CONSTRAINT error_logs_pkey PRIMARY KEY (id);


--
-- Name: expectation_locks expectation_locks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.expectation_locks
    ADD CONSTRAINT expectation_locks_pkey PRIMARY KEY (id);


--
-- Name: failover_events failover_events_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.failover_events
    ADD CONSTRAINT failover_events_pkey PRIMARY KEY (id);


--
-- Name: fused_models fused_models_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fused_models
    ADD CONSTRAINT fused_models_pkey PRIMARY KEY (id);


--
-- Name: fusion_performance_log fusion_performance_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fusion_performance_log
    ADD CONSTRAINT fusion_performance_log_pkey PRIMARY KEY (id);


--
-- Name: fusion_strategies fusion_strategies_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fusion_strategies
    ADD CONSTRAINT fusion_strategies_pkey PRIMARY KEY (id);


--
-- Name: gpu_jobs gpu_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gpu_jobs
    ADD CONSTRAINT gpu_jobs_pkey PRIMARY KEY (id);


--
-- Name: gpu_system_status gpu_system_status_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gpu_system_status
    ADD CONSTRAINT gpu_system_status_pkey PRIMARY KEY (id);


--
-- Name: graphics_benchmarks graphics_benchmarks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.graphics_benchmarks
    ADD CONSTRAINT graphics_benchmarks_pkey PRIMARY KEY (id);


--
-- Name: immutable_audit_logs immutable_audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.immutable_audit_logs
    ADD CONSTRAINT immutable_audit_logs_pkey PRIMARY KEY (id);


--
-- Name: incidents incidents_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_pkey PRIMARY KEY (id);


--
-- Name: inference_jobs inference_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inference_jobs
    ADD CONSTRAINT inference_jobs_pkey PRIMARY KEY (id);


--
-- Name: integrations integrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.integrations
    ADD CONSTRAINT integrations_pkey PRIMARY KEY (id);


--
-- Name: job_final_states job_final_states_job_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.job_final_states
    ADD CONSTRAINT job_final_states_job_id_key UNIQUE (job_id);


--
-- Name: job_final_states job_final_states_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.job_final_states
    ADD CONSTRAINT job_final_states_pkey PRIMARY KEY (id);


--
-- Name: job_logs job_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.job_logs
    ADD CONSTRAINT job_logs_pkey PRIMARY KEY (id);


--
-- Name: job_queue job_queue_job_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.job_queue
    ADD CONSTRAINT job_queue_job_id_key UNIQUE (job_id);


--
-- Name: job_queue job_queue_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.job_queue
    ADD CONSTRAINT job_queue_pkey PRIMARY KEY (id);


--
-- Name: job_results job_results_job_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.job_results
    ADD CONSTRAINT job_results_job_id_key UNIQUE (job_id);


--
-- Name: job_results job_results_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.job_results
    ADD CONSTRAINT job_results_pkey PRIMARY KEY (id);


--
-- Name: jobs jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY (id);


--
-- Name: knowledge_transfer_logs knowledge_transfer_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.knowledge_transfer_logs
    ADD CONSTRAINT knowledge_transfer_logs_pkey PRIMARY KEY (id);


--
-- Name: marketplace_transactions marketplace_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.marketplace_transactions
    ADD CONSTRAINT marketplace_transactions_pkey PRIMARY KEY (id);


--
-- Name: metrics_aggregated metrics_aggregated_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.metrics_aggregated
    ADD CONSTRAINT metrics_aggregated_pkey PRIMARY KEY (id);


--
-- Name: metrics_raw metrics_raw_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.metrics_raw
    ADD CONSTRAINT metrics_raw_pkey PRIMARY KEY (id);


--
-- Name: models models_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.models
    ADD CONSTRAINT models_pkey PRIMARY KEY (id);


--
-- Name: module_configs module_configs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.module_configs
    ADD CONSTRAINT module_configs_pkey PRIMARY KEY (id);


--
-- Name: module_configs module_configs_user_id_module_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.module_configs
    ADD CONSTRAINT module_configs_user_id_module_name_key UNIQUE (user_id, module_name);


--
-- Name: module_locks module_locks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.module_locks
    ADD CONSTRAINT module_locks_pkey PRIMARY KEY (id);


--
-- Name: module_locks module_locks_session_id_module_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.module_locks
    ADD CONSTRAINT module_locks_session_id_module_name_key UNIQUE (session_id, module_name);


--
-- Name: module_status module_status_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.module_status
    ADD CONSTRAINT module_status_pkey PRIMARY KEY (id);


--
-- Name: module_status module_status_user_id_module_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.module_status
    ADD CONSTRAINT module_status_user_id_module_name_key UNIQUE (user_id, module_name);


--
-- Name: offline_packages offline_packages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.offline_packages
    ADD CONSTRAINT offline_packages_pkey PRIMARY KEY (id);


--
-- Name: owner_diagnostics owner_diagnostics_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.owner_diagnostics
    ADD CONSTRAINT owner_diagnostics_pkey PRIMARY KEY (id);


--
-- Name: payment_webhook_events payment_webhook_events_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_webhook_events
    ADD CONSTRAINT payment_webhook_events_pkey PRIMARY KEY (id);


--
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (id);


--
-- Name: performance_metrics performance_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.performance_metrics
    ADD CONSTRAINT performance_metrics_pkey PRIMARY KEY (id);


--
-- Name: permissions permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (id);


--
-- Name: persistent_compute_jobs persistent_compute_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.persistent_compute_jobs
    ADD CONSTRAINT persistent_compute_jobs_pkey PRIMARY KEY (id);


--
-- Name: personalization_settings personalization_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.personalization_settings
    ADD CONSTRAINT personalization_settings_pkey PRIMARY KEY (id);


--
-- Name: personalization_settings personalization_settings_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.personalization_settings
    ADD CONSTRAINT personalization_settings_user_id_key UNIQUE (user_id);


--
-- Name: plugins plugins_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.plugins
    ADD CONSTRAINT plugins_pkey PRIMARY KEY (id);


--
-- Name: prediction_accuracy prediction_accuracy_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prediction_accuracy
    ADD CONSTRAINT prediction_accuracy_pkey PRIMARY KEY (id);


--
-- Name: profiles profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT profiles_pkey PRIMARY KEY (id);


--
-- Name: profiles profiles_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT profiles_user_id_key UNIQUE (user_id);


--
-- Name: quantum_benchmarks quantum_benchmarks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quantum_benchmarks
    ADD CONSTRAINT quantum_benchmarks_pkey PRIMARY KEY (id);


--
-- Name: quantum_circuits quantum_circuits_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quantum_circuits
    ADD CONSTRAINT quantum_circuits_pkey PRIMARY KEY (id);


--
-- Name: quantum_jobs quantum_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quantum_jobs
    ADD CONSTRAINT quantum_jobs_pkey PRIMARY KEY (id);


--
-- Name: quantum_results quantum_results_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quantum_results
    ADD CONSTRAINT quantum_results_pkey PRIMARY KEY (id);


--
-- Name: recommendations recommendations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recommendations
    ADD CONSTRAINT recommendations_pkey PRIMARY KEY (id);


--
-- Name: scaling_actions scaling_actions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scaling_actions
    ADD CONSTRAINT scaling_actions_pkey PRIMARY KEY (id);


--
-- Name: security_events security_events_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.security_events
    ADD CONSTRAINT security_events_pkey PRIMARY KEY (id);


--
-- Name: semantic_embeddings semantic_embeddings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.semantic_embeddings
    ADD CONSTRAINT semantic_embeddings_pkey PRIMARY KEY (id);


--
-- Name: subscriptions subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_pkey PRIMARY KEY (id);


--
-- Name: subscriptions subscriptions_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_user_id_key UNIQUE (user_id);


--
-- Name: system_health system_health_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.system_health
    ADD CONSTRAINT system_health_pkey PRIMARY KEY (id);


--
-- Name: system_metrics system_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.system_metrics
    ADD CONSTRAINT system_metrics_pkey PRIMARY KEY (id);


--
-- Name: system_settings system_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.system_settings
    ADD CONSTRAINT system_settings_pkey PRIMARY KEY (key);


--
-- Name: team_members team_members_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.team_members
    ADD CONSTRAINT team_members_pkey PRIMARY KEY (id);


--
-- Name: teams teams_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT teams_pkey PRIMARY KEY (id);


--
-- Name: threats_detected threats_detected_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.threats_detected
    ADD CONSTRAINT threats_detected_pkey PRIMARY KEY (id);


--
-- Name: traces traces_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.traces
    ADD CONSTRAINT traces_pkey PRIMARY KEY (id);


--
-- Name: usage_stats usage_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usage_stats
    ADD CONSTRAINT usage_stats_pkey PRIMARY KEY (id);


--
-- Name: user_behaviors user_behaviors_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_behaviors
    ADD CONSTRAINT user_behaviors_pkey PRIMARY KEY (id);


--
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (id);


--
-- Name: user_roles user_roles_user_id_role_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_user_id_role_key UNIQUE (user_id, role);


--
-- Name: video_benchmarks video_benchmarks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.video_benchmarks
    ADD CONSTRAINT video_benchmarks_pkey PRIMARY KEY (id);


--
-- Name: webhook_test_log webhook_test_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.webhook_test_log
    ADD CONSTRAINT webhook_test_log_pkey PRIMARY KEY (id);


--
-- Name: worker_api_keys worker_api_keys_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.worker_api_keys
    ADD CONSTRAINT worker_api_keys_pkey PRIMARY KEY (id);


--
-- Name: workload_predictions workload_predictions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workload_predictions
    ADD CONSTRAINT workload_predictions_pkey PRIMARY KEY (id);


--
-- Name: idx_agent_heartbeats_worker; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_agent_heartbeats_worker ON public.agent_heartbeats USING btree (worker_id, recorded_at DESC);


--
-- Name: idx_alerts_resolved; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_alerts_resolved ON public.alerts USING btree (resolved);


--
-- Name: idx_alerts_severity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_alerts_severity ON public.alerts USING btree (severity);


--
-- Name: idx_alerts_user_id_resolved; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_alerts_user_id_resolved ON public.alerts USING btree (user_id, resolved);


--
-- Name: idx_analytics_events_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_analytics_events_created_at ON public.analytics_events USING btree (created_at);


--
-- Name: idx_analytics_events_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_analytics_events_user_id ON public.analytics_events USING btree (user_id);


--
-- Name: idx_api_keys_active_lookup; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_api_keys_active_lookup ON public.api_keys USING btree (is_active, expires_at) WHERE (is_active = true);


--
-- Name: idx_api_keys_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_api_keys_user_id ON public.api_keys USING btree (user_id);


--
-- Name: idx_device_registry_token; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_device_registry_token ON public.device_registry USING btree (device_token);


--
-- Name: idx_device_registry_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_device_registry_user ON public.device_registry USING btree (user_id);


--
-- Name: idx_error_logs_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_error_logs_created_at ON public.error_logs USING btree (created_at);


--
-- Name: idx_error_logs_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_error_logs_user_id ON public.error_logs USING btree (user_id);


--
-- Name: idx_expectation_locks_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_expectation_locks_user_id ON public.expectation_locks USING btree (user_id);


--
-- Name: idx_gpu_jobs_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_gpu_jobs_created_at ON public.gpu_jobs USING btree (created_at DESC);


--
-- Name: idx_gpu_jobs_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_gpu_jobs_status ON public.gpu_jobs USING btree (status);


--
-- Name: idx_gpu_jobs_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_gpu_jobs_user_id ON public.gpu_jobs USING btree (user_id);


--
-- Name: idx_gpu_system_status_worker_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_gpu_system_status_worker_id ON public.gpu_system_status USING btree (worker_id);


--
-- Name: idx_inference_jobs_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_inference_jobs_created_at ON public.inference_jobs USING btree (created_at);


--
-- Name: idx_inference_jobs_model_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_inference_jobs_model_id ON public.inference_jobs USING btree (model_id);


--
-- Name: idx_inference_jobs_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_inference_jobs_status ON public.inference_jobs USING btree (status);


--
-- Name: idx_inference_jobs_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_inference_jobs_user_id ON public.inference_jobs USING btree (user_id);


--
-- Name: idx_job_final_states_job_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_job_final_states_job_id ON public.job_final_states USING btree (job_id);


--
-- Name: idx_job_final_states_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_job_final_states_user_id ON public.job_final_states USING btree (user_id);


--
-- Name: idx_job_logs_job_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_job_logs_job_id ON public.job_logs USING btree (job_id);


--
-- Name: idx_job_logs_ts; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_job_logs_ts ON public.job_logs USING btree (ts DESC);


--
-- Name: idx_jobs_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_jobs_created_at ON public.jobs USING btree (created_at DESC);


--
-- Name: idx_jobs_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_jobs_status ON public.jobs USING btree (status);


--
-- Name: idx_jobs_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_jobs_user_id ON public.jobs USING btree (user_id);


--
-- Name: idx_models_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_models_created_at ON public.models USING btree (created_at);


--
-- Name: idx_models_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_models_status ON public.models USING btree (status);


--
-- Name: idx_module_configs_module_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_module_configs_module_name ON public.module_configs USING btree (module_name);


--
-- Name: idx_module_status_module_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_module_status_module_name ON public.module_status USING btree (module_name);


--
-- Name: idx_module_status_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_module_status_status ON public.module_status USING btree (status);


--
-- Name: idx_payments_provider; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_payments_provider ON public.payments USING btree (provider);


--
-- Name: idx_payments_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_payments_status ON public.payments USING btree (status);


--
-- Name: idx_payments_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_payments_user_id ON public.payments USING btree (user_id);


--
-- Name: idx_performance_metrics_job_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_performance_metrics_job_id ON public.performance_metrics USING btree (job_id);


--
-- Name: idx_performance_metrics_recorded_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_performance_metrics_recorded_at ON public.performance_metrics USING btree (recorded_at);


--
-- Name: idx_performance_metrics_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_performance_metrics_user_id ON public.performance_metrics USING btree (user_id);


--
-- Name: idx_system_health_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_system_health_user ON public.system_health USING btree (user_id);


--
-- Name: idx_system_metrics_device; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_system_metrics_device ON public.system_metrics USING btree (device_id);


--
-- Name: idx_system_metrics_recorded_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_system_metrics_recorded_at ON public.system_metrics USING btree (recorded_at);


--
-- Name: idx_system_metrics_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_system_metrics_status ON public.system_metrics USING btree (status);


--
-- Name: idx_system_metrics_user_id_recorded_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_system_metrics_user_id_recorded_at ON public.system_metrics USING btree (user_id, recorded_at DESC);


--
-- Name: idx_usage_stats_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_usage_stats_created_at ON public.usage_stats USING btree (created_at DESC);


--
-- Name: idx_usage_stats_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_usage_stats_user_id ON public.usage_stats USING btree (user_id);


--
-- Name: idx_webhook_test_log_user_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_webhook_test_log_user_created ON public.webhook_test_log USING btree (user_id, created_at DESC);


--
-- Name: gpu_jobs update_gpu_jobs_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_gpu_jobs_updated_at BEFORE UPDATE ON public.gpu_jobs FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: gpu_system_status update_gpu_system_status_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_gpu_system_status_updated_at BEFORE UPDATE ON public.gpu_system_status FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: inference_jobs update_inference_jobs_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_inference_jobs_updated_at BEFORE UPDATE ON public.inference_jobs FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: models update_models_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_models_updated_at BEFORE UPDATE ON public.models FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: module_configs update_module_configs_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_module_configs_updated_at BEFORE UPDATE ON public.module_configs FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: module_status update_module_status_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_module_status_updated_at BEFORE UPDATE ON public.module_status FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: payments update_payments_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON public.payments FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: profiles update_profiles_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON public.profiles FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: subscriptions update_subscriptions_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON public.subscriptions FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: agent_heartbeats agent_heartbeats_agent_token_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_heartbeats
    ADD CONSTRAINT agent_heartbeats_agent_token_id_fkey FOREIGN KEY (agent_token_id) REFERENCES public.agent_tokens(id) ON DELETE CASCADE;


--
-- Name: agent_heartbeats agent_heartbeats_current_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_heartbeats
    ADD CONSTRAINT agent_heartbeats_current_job_id_fkey FOREIGN KEY (current_job_id) REFERENCES public.gpu_jobs(id);


--
-- Name: api_keys api_keys_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_keys
    ADD CONSTRAINT api_keys_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: approval_workflows approval_workflows_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.approval_workflows
    ADD CONSTRAINT approval_workflows_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.teams(id) ON DELETE CASCADE;


--
-- Name: cloud_costs cloud_costs_provider_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cloud_costs
    ADD CONSTRAINT cloud_costs_provider_id_fkey FOREIGN KEY (provider_id) REFERENCES public.cloud_providers(id) ON DELETE CASCADE;


--
-- Name: cloud_failover_log cloud_failover_log_from_provider_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cloud_failover_log
    ADD CONSTRAINT cloud_failover_log_from_provider_id_fkey FOREIGN KEY (from_provider_id) REFERENCES public.cloud_providers(id);


--
-- Name: cloud_failover_log cloud_failover_log_to_provider_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cloud_failover_log
    ADD CONSTRAINT cloud_failover_log_to_provider_id_fkey FOREIGN KEY (to_provider_id) REFERENCES public.cloud_providers(id);


--
-- Name: cloud_latencies cloud_latencies_provider_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cloud_latencies
    ADD CONSTRAINT cloud_latencies_provider_id_fkey FOREIGN KEY (provider_id) REFERENCES public.cloud_providers(id) ON DELETE CASCADE;


--
-- Name: collaboration_changes collaboration_changes_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.collaboration_changes
    ADD CONSTRAINT collaboration_changes_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.collaboration_sessions(id) ON DELETE CASCADE;


--
-- Name: collaboration_comments collaboration_comments_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.collaboration_comments
    ADD CONSTRAINT collaboration_comments_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.collaboration_comments(id);


--
-- Name: collaboration_comments collaboration_comments_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.collaboration_comments
    ADD CONSTRAINT collaboration_comments_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.collaboration_sessions(id) ON DELETE CASCADE;


--
-- Name: collaboration_messages collaboration_messages_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.collaboration_messages
    ADD CONSTRAINT collaboration_messages_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.collaboration_sessions(id) ON DELETE CASCADE;


--
-- Name: collaboration_participants collaboration_participants_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.collaboration_participants
    ADD CONSTRAINT collaboration_participants_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.collaboration_sessions(id) ON DELETE CASCADE;


--
-- Name: collaboration_sessions collaboration_sessions_inference_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.collaboration_sessions
    ADD CONSTRAINT collaboration_sessions_inference_job_id_fkey FOREIGN KEY (inference_job_id) REFERENCES public.inference_jobs(id);


--
-- Name: collaboration_votes collaboration_votes_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.collaboration_votes
    ADD CONSTRAINT collaboration_votes_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.collaboration_sessions(id) ON DELETE CASCADE;


--
-- Name: custom_roles custom_roles_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.custom_roles
    ADD CONSTRAINT custom_roles_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.teams(id) ON DELETE CASCADE;


--
-- Name: custom_visualizations custom_visualizations_dashboard_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.custom_visualizations
    ADD CONSTRAINT custom_visualizations_dashboard_id_fkey FOREIGN KEY (dashboard_id) REFERENCES public.analytics_dashboards(id) ON DELETE CASCADE;


--
-- Name: distillation_jobs distillation_jobs_distilled_model_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.distillation_jobs
    ADD CONSTRAINT distillation_jobs_distilled_model_id_fkey FOREIGN KEY (distilled_model_id) REFERENCES public.distilled_models(id) ON DELETE CASCADE;


--
-- Name: distillation_metrics distillation_metrics_distillation_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.distillation_metrics
    ADD CONSTRAINT distillation_metrics_distillation_job_id_fkey FOREIGN KEY (distillation_job_id) REFERENCES public.distillation_jobs(id) ON DELETE CASCADE;


--
-- Name: distilled_models distilled_models_teacher_model_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.distilled_models
    ADD CONSTRAINT distilled_models_teacher_model_id_fkey FOREIGN KEY (teacher_model_id) REFERENCES public.models(id);


--
-- Name: distributed_training_jobs distributed_training_jobs_model_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.distributed_training_jobs
    ADD CONSTRAINT distributed_training_jobs_model_id_fkey FOREIGN KEY (model_id) REFERENCES public.models(id) ON DELETE SET NULL;


--
-- Name: fusion_performance_log fusion_performance_log_fused_model_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fusion_performance_log
    ADD CONSTRAINT fusion_performance_log_fused_model_id_fkey FOREIGN KEY (fused_model_id) REFERENCES public.fused_models(id) ON DELETE CASCADE;


--
-- Name: gpu_system_status gpu_system_status_active_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gpu_system_status
    ADD CONSTRAINT gpu_system_status_active_job_id_fkey FOREIGN KEY (active_job_id) REFERENCES public.gpu_jobs(id);


--
-- Name: inference_jobs inference_jobs_model_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inference_jobs
    ADD CONSTRAINT inference_jobs_model_id_fkey FOREIGN KEY (model_id) REFERENCES public.models(id) ON DELETE CASCADE;


--
-- Name: integrations integrations_plugin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.integrations
    ADD CONSTRAINT integrations_plugin_id_fkey FOREIGN KEY (plugin_id) REFERENCES public.plugins(id) ON DELETE CASCADE;


--
-- Name: job_logs job_logs_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.job_logs
    ADD CONSTRAINT job_logs_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.gpu_jobs(id) ON DELETE CASCADE;


--
-- Name: job_queue job_queue_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.job_queue
    ADD CONSTRAINT job_queue_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.gpu_jobs(id) ON DELETE CASCADE;


--
-- Name: job_results job_results_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.job_results
    ADD CONSTRAINT job_results_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.gpu_jobs(id) ON DELETE CASCADE;


--
-- Name: jobs jobs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: knowledge_transfer_logs knowledge_transfer_logs_distillation_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.knowledge_transfer_logs
    ADD CONSTRAINT knowledge_transfer_logs_distillation_job_id_fkey FOREIGN KEY (distillation_job_id) REFERENCES public.distillation_jobs(id) ON DELETE CASCADE;


--
-- Name: marketplace_transactions marketplace_transactions_plugin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.marketplace_transactions
    ADD CONSTRAINT marketplace_transactions_plugin_id_fkey FOREIGN KEY (plugin_id) REFERENCES public.plugins(id) ON DELETE SET NULL;


--
-- Name: module_locks module_locks_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.module_locks
    ADD CONSTRAINT module_locks_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.collaboration_sessions(id) ON DELETE CASCADE;


--
-- Name: module_status module_status_current_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.module_status
    ADD CONSTRAINT module_status_current_job_id_fkey FOREIGN KEY (current_job_id) REFERENCES public.inference_jobs(id) ON DELETE SET NULL;


--
-- Name: performance_metrics performance_metrics_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.performance_metrics
    ADD CONSTRAINT performance_metrics_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.inference_jobs(id) ON DELETE CASCADE;


--
-- Name: performance_metrics performance_metrics_model_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.performance_metrics
    ADD CONSTRAINT performance_metrics_model_id_fkey FOREIGN KEY (model_id) REFERENCES public.models(id) ON DELETE CASCADE;


--
-- Name: permissions permissions_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.custom_roles(id) ON DELETE CASCADE;


--
-- Name: profiles profiles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: quantum_benchmarks quantum_benchmarks_circuit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quantum_benchmarks
    ADD CONSTRAINT quantum_benchmarks_circuit_id_fkey FOREIGN KEY (circuit_id) REFERENCES public.quantum_circuits(id) ON DELETE SET NULL;


--
-- Name: quantum_jobs quantum_jobs_circuit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quantum_jobs
    ADD CONSTRAINT quantum_jobs_circuit_id_fkey FOREIGN KEY (circuit_id) REFERENCES public.quantum_circuits(id) ON DELETE CASCADE;


--
-- Name: quantum_results quantum_results_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quantum_results
    ADD CONSTRAINT quantum_results_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.quantum_jobs(id) ON DELETE CASCADE;


--
-- Name: subscriptions subscriptions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: system_metrics system_metrics_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.system_metrics
    ADD CONSTRAINT system_metrics_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.device_registry(id) ON DELETE SET NULL;


--
-- Name: team_members team_members_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.team_members
    ADD CONSTRAINT team_members_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.teams(id) ON DELETE CASCADE;


--
-- Name: usage_stats usage_stats_api_key_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usage_stats
    ADD CONSTRAINT usage_stats_api_key_id_fkey FOREIGN KEY (api_key_id) REFERENCES public.api_keys(id) ON DELETE CASCADE;


--
-- Name: usage_stats usage_stats_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usage_stats
    ADD CONSTRAINT usage_stats_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: user_roles user_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: webhook_test_log webhook_test_log_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.webhook_test_log
    ADD CONSTRAINT webhook_test_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: owner_diagnostics Admins can manage diagnostics; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Admins can manage diagnostics" ON public.owner_diagnostics USING (public.has_role(auth.uid(), 'admin'::public.app_role));


--
-- Name: agent_heartbeats Admins can view agent heartbeats; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Admins can view agent heartbeats" ON public.agent_heartbeats FOR SELECT TO authenticated USING (public.has_role(auth.uid(), 'admin'::public.app_role));


--
-- Name: agent_tokens Admins can view agent tokens; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Admins can view agent tokens" ON public.agent_tokens FOR SELECT TO authenticated USING (public.has_role(auth.uid(), 'admin'::public.app_role));


--
-- Name: payments Admins can view all payments; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Admins can view all payments" ON public.payments FOR SELECT USING (public.has_role(auth.uid(), 'admin'::public.app_role));


--
-- Name: owner_diagnostics Admins can view diagnostics; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Admins can view diagnostics" ON public.owner_diagnostics FOR SELECT USING (public.has_role(auth.uid(), 'admin'::public.app_role));


--
-- Name: gpu_system_status Admins can view gpu system status; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Admins can view gpu system status" ON public.gpu_system_status FOR SELECT USING (public.has_role(auth.uid(), 'admin'::public.app_role));


--
-- Name: system_settings Admins can view system settings; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Admins can view system settings" ON public.system_settings FOR SELECT USING (public.has_role(auth.uid(), 'admin'::public.app_role));


--
-- Name: payment_webhook_events Admins can view webhook events; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Admins can view webhook events" ON public.payment_webhook_events FOR SELECT USING (public.has_role(auth.uid(), 'admin'::public.app_role));


--
-- Name: plugins Anyone can view published plugins; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Anyone can view published plugins" ON public.plugins FOR SELECT USING (((is_published = true) OR (author_id = auth.uid())));


--
-- Name: enterprise_requests Authenticated users can submit enterprise requests; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Authenticated users can submit enterprise requests" ON public.enterprise_requests FOR INSERT TO authenticated WITH CHECK ((auth.uid() = user_id));


--
-- Name: plugins Authors can manage own plugins; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Authors can manage own plugins" ON public.plugins USING ((author_id = auth.uid()));


--
-- Name: immutable_audit_logs Block deletes from audit logs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Block deletes from audit logs" ON public.immutable_audit_logs FOR DELETE USING (false);


--
-- Name: security_events Block deletes from security events; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Block deletes from security events" ON public.security_events FOR DELETE USING (false);


--
-- Name: immutable_audit_logs Block updates to audit logs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Block updates to audit logs" ON public.immutable_audit_logs FOR UPDATE USING (false);


--
-- Name: security_events Block updates to security events; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Block updates to security events" ON public.security_events FOR UPDATE USING (false);


--
-- Name: team_members Members can view their team membership; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Members can view their team membership" ON public.team_members FOR SELECT USING ((user_id = auth.uid()));


--
-- Name: collaboration_sessions Owners can update sessions; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Owners can update sessions" ON public.collaboration_sessions FOR UPDATE USING ((owner_id = auth.uid()));


--
-- Name: collaboration_changes Participants can create changes; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Participants can create changes" ON public.collaboration_changes FOR INSERT WITH CHECK ((user_id = auth.uid()));


--
-- Name: collaboration_comments Participants can create comments; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Participants can create comments" ON public.collaboration_comments FOR INSERT WITH CHECK ((user_id = auth.uid()));


--
-- Name: module_locks Participants can manage locks; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Participants can manage locks" ON public.module_locks USING ((locked_by = auth.uid()));


--
-- Name: collaboration_messages Participants can send messages; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Participants can send messages" ON public.collaboration_messages FOR INSERT WITH CHECK ((user_id = auth.uid()));


--
-- Name: collaboration_changes Participants can view changes; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Participants can view changes" ON public.collaboration_changes FOR SELECT USING ((EXISTS ( SELECT 1
   FROM public.collaboration_participants
  WHERE ((collaboration_participants.session_id = collaboration_changes.session_id) AND (collaboration_participants.user_id = auth.uid())))));


--
-- Name: collaboration_comments Participants can view comments; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Participants can view comments" ON public.collaboration_comments FOR SELECT USING ((EXISTS ( SELECT 1
   FROM public.collaboration_participants
  WHERE ((collaboration_participants.session_id = collaboration_comments.session_id) AND (collaboration_participants.user_id = auth.uid())))));


--
-- Name: module_locks Participants can view locks; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Participants can view locks" ON public.module_locks FOR SELECT USING ((EXISTS ( SELECT 1
   FROM public.collaboration_participants
  WHERE ((collaboration_participants.session_id = module_locks.session_id) AND (collaboration_participants.user_id = auth.uid())))));


--
-- Name: collaboration_messages Participants can view messages; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Participants can view messages" ON public.collaboration_messages FOR SELECT USING ((EXISTS ( SELECT 1
   FROM public.collaboration_participants
  WHERE ((collaboration_participants.session_id = collaboration_messages.session_id) AND (collaboration_participants.user_id = auth.uid())))));


--
-- Name: collaboration_participants Participants can view participants; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Participants can view participants" ON public.collaboration_participants FOR SELECT USING ((EXISTS ( SELECT 1
   FROM public.collaboration_sessions
  WHERE ((collaboration_sessions.id = collaboration_participants.session_id) AND ((collaboration_sessions.owner_id = auth.uid()) OR (EXISTS ( SELECT 1
           FROM public.collaboration_participants p
          WHERE ((p.session_id = p.session_id) AND (p.user_id = auth.uid())))))))));


--
-- Name: collaboration_votes Participants can view votes; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Participants can view votes" ON public.collaboration_votes FOR SELECT USING ((EXISTS ( SELECT 1
   FROM public.collaboration_participants
  WHERE ((collaboration_participants.session_id = collaboration_votes.session_id) AND (collaboration_participants.user_id = auth.uid())))));


--
-- Name: collaboration_votes Participants can vote; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Participants can vote" ON public.collaboration_votes FOR INSERT WITH CHECK ((user_id = auth.uid()));


--
-- Name: permissions Permissions access; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Permissions access" ON public.permissions USING ((EXISTS ( SELECT 1
   FROM (public.custom_roles
     JOIN public.teams ON ((teams.id = custom_roles.team_id)))
  WHERE ((custom_roles.id = permissions.role_id) AND (teams.owner_id = auth.uid())))));


--
-- Name: payment_webhook_events Service can insert webhook events; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Service can insert webhook events" ON public.payment_webhook_events FOR INSERT WITH CHECK (true);


--
-- Name: gpu_jobs Service role can manage all jobs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Service role can manage all jobs" ON public.gpu_jobs USING (((auth.jwt() ->> 'role'::text) = 'service_role'::text));


--
-- Name: gpu_system_status Service role can manage system status; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Service role can manage system status" ON public.gpu_system_status USING (((auth.jwt() ->> 'role'::text) = 'service_role'::text));


--
-- Name: worker_api_keys Service role can manage worker keys; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Service role can manage worker keys" ON public.worker_api_keys USING (((auth.jwt() ->> 'role'::text) = 'service_role'::text));


--
-- Name: collaboration_participants Session owners can manage participants; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Session owners can manage participants" ON public.collaboration_participants USING ((EXISTS ( SELECT 1
   FROM public.collaboration_sessions
  WHERE ((collaboration_sessions.id = collaboration_participants.session_id) AND (collaboration_sessions.owner_id = auth.uid())))));


--
-- Name: expectation_locks System can manage locks; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "System can manage locks" ON public.expectation_locks USING (true);


--
-- Name: team_members Team access for members; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Team access for members" ON public.team_members FOR SELECT USING (((user_id = auth.uid()) OR (EXISTS ( SELECT 1
   FROM public.teams
  WHERE ((teams.id = team_members.team_id) AND (teams.owner_id = auth.uid()))))));


--
-- Name: teams Team members can view teams; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Team members can view teams" ON public.teams FOR SELECT USING (((owner_id = auth.uid()) OR (EXISTS ( SELECT 1
   FROM public.team_members
  WHERE ((team_members.team_id = teams.id) AND (team_members.user_id = auth.uid()))))));


--
-- Name: approval_workflows Team members can view workflows; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Team members can view workflows" ON public.approval_workflows FOR SELECT USING (public.is_team_member(auth.uid(), team_id));


--
-- Name: team_members Team owners can manage members; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Team owners can manage members" ON public.team_members USING ((EXISTS ( SELECT 1
   FROM public.teams
  WHERE ((teams.id = team_members.team_id) AND (teams.owner_id = auth.uid())))));


--
-- Name: teams Team owners can manage teams; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Team owners can manage teams" ON public.teams USING ((owner_id = auth.uid()));


--
-- Name: approval_workflows Team owners can manage workflows; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Team owners can manage workflows" ON public.approval_workflows USING ((EXISTS ( SELECT 1
   FROM public.teams
  WHERE ((teams.id = approval_workflows.team_id) AND (teams.owner_id = auth.uid())))));


--
-- Name: team_members Team owners manage members; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Team owners manage members" ON public.team_members USING ((EXISTS ( SELECT 1
   FROM public.teams
  WHERE ((teams.id = team_members.team_id) AND (teams.owner_id = auth.uid())))));


--
-- Name: custom_roles Team roles access; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Team roles access" ON public.custom_roles USING ((EXISTS ( SELECT 1
   FROM public.teams
  WHERE ((teams.id = custom_roles.team_id) AND (teams.owner_id = auth.uid())))));


--
-- Name: gpu_jobs Users can cancel their own pending jobs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can cancel their own pending jobs" ON public.gpu_jobs FOR UPDATE USING (((auth.uid() = user_id) AND (status = ANY (ARRAY['pending'::text, 'queued'::text]))));


--
-- Name: cache_analytics Users can create cache analytics; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can create cache analytics" ON public.cache_analytics FOR INSERT WITH CHECK ((user_id = auth.uid()));


--
-- Name: cache_metadata Users can create cache metadata; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can create cache metadata" ON public.cache_metadata FOR INSERT WITH CHECK ((user_id = auth.uid()));


--
-- Name: cloud_providers Users can create cloud providers; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can create cloud providers" ON public.cloud_providers FOR INSERT WITH CHECK ((user_id = auth.uid()));


--
-- Name: cost_analysis Users can create cost analysis; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can create cost analysis" ON public.cost_analysis FOR INSERT WITH CHECK ((user_id = auth.uid()));


--
-- Name: distillation_jobs Users can create distillation jobs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can create distillation jobs" ON public.distillation_jobs FOR INSERT WITH CHECK ((user_id = auth.uid()));


--
-- Name: distilled_models Users can create distilled models; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can create distilled models" ON public.distilled_models FOR INSERT WITH CHECK ((user_id = auth.uid()));


--
-- Name: semantic_embeddings Users can create embeddings; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can create embeddings" ON public.semantic_embeddings FOR INSERT WITH CHECK ((user_id = auth.uid()));


--
-- Name: cache_invalidation_log Users can create invalidation logs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can create invalidation logs" ON public.cache_invalidation_log FOR INSERT WITH CHECK ((user_id = auth.uid()));


--
-- Name: api_keys Users can create own api_keys; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can create own api_keys" ON public.api_keys FOR INSERT WITH CHECK ((auth.uid() = user_id));


--
-- Name: billing_subscriptions Users can create own subscriptions; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can create own subscriptions" ON public.billing_subscriptions FOR INSERT WITH CHECK ((auth.uid() = user_id));


--
-- Name: billing_usage_records Users can create own usage; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can create own usage" ON public.billing_usage_records FOR INSERT WITH CHECK ((auth.uid() = user_id));


--
-- Name: prediction_accuracy Users can create prediction accuracy; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can create prediction accuracy" ON public.prediction_accuracy FOR INSERT WITH CHECK ((user_id = auth.uid()));


--
-- Name: workload_predictions Users can create predictions; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can create predictions" ON public.workload_predictions FOR INSERT WITH CHECK ((user_id = auth.uid()));


--
-- Name: cloud_routing_rules Users can create routing rules; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can create routing rules" ON public.cloud_routing_rules FOR INSERT WITH CHECK ((user_id = auth.uid()));


--
-- Name: scaling_actions Users can create scaling actions; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can create scaling actions" ON public.scaling_actions FOR INSERT WITH CHECK ((user_id = auth.uid()));


--
-- Name: collaboration_sessions Users can create sessions; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can create sessions" ON public.collaboration_sessions FOR INSERT WITH CHECK ((owner_id = auth.uid()));


--
-- Name: api_keys Users can create their own API keys; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can create their own API keys" ON public.api_keys FOR INSERT TO authenticated WITH CHECK ((auth.uid() = user_id));


--
-- Name: alerts Users can create their own alerts; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can create their own alerts" ON public.alerts FOR INSERT WITH CHECK ((auth.uid() = user_id));


--
-- Name: gpu_jobs Users can create their own jobs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can create their own jobs" ON public.gpu_jobs FOR INSERT WITH CHECK ((auth.uid() = user_id));


--
-- Name: inference_jobs Users can create their own jobs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can create their own jobs" ON public.inference_jobs FOR INSERT WITH CHECK ((auth.uid() = user_id));


--
-- Name: jobs Users can create their own jobs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can create their own jobs" ON public.jobs FOR INSERT WITH CHECK ((auth.uid() = user_id));


--
-- Name: models Users can create their own models; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can create their own models" ON public.models FOR INSERT WITH CHECK ((auth.uid() = user_id));


--
-- Name: module_configs Users can create their own module configs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can create their own module configs" ON public.module_configs FOR INSERT WITH CHECK ((auth.uid() = user_id));


--
-- Name: cache_warming_jobs Users can create warming jobs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can create warming jobs" ON public.cache_warming_jobs FOR INSERT WITH CHECK ((user_id = auth.uid()));


--
-- Name: api_keys Users can delete own api_keys; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can delete own api_keys" ON public.api_keys FOR DELETE USING ((auth.uid() = user_id));


--
-- Name: cache_metadata Users can delete own cache metadata; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can delete own cache metadata" ON public.cache_metadata FOR DELETE USING ((user_id = auth.uid()));


--
-- Name: cloud_providers Users can delete own cloud providers; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can delete own cloud providers" ON public.cloud_providers FOR DELETE USING ((user_id = auth.uid()));


--
-- Name: distilled_models Users can delete own distilled models; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can delete own distilled models" ON public.distilled_models FOR DELETE USING ((user_id = auth.uid()));


--
-- Name: api_keys Users can delete their own API keys; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can delete their own API keys" ON public.api_keys FOR DELETE TO authenticated USING ((auth.uid() = user_id));


--
-- Name: models Users can delete their own models; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can delete their own models" ON public.models FOR DELETE USING ((auth.uid() = user_id));


--
-- Name: immutable_audit_logs Users can insert audit logs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can insert audit logs" ON public.immutable_audit_logs FOR INSERT WITH CHECK (((user_id = auth.uid()) OR (user_id IS NULL)));


--
-- Name: error_logs Users can insert error logs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can insert error logs" ON public.error_logs FOR INSERT WITH CHECK (((auth.uid() = user_id) OR (user_id IS NULL)));


--
-- Name: webhook_test_log Users can insert own webhook tests; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can insert own webhook tests" ON public.webhook_test_log FOR INSERT WITH CHECK ((auth.uid() = user_id));


--
-- Name: security_events Users can insert security events; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can insert security events" ON public.security_events FOR INSERT WITH CHECK (((user_id = auth.uid()) OR (user_id IS NULL)));


--
-- Name: analytics_events Users can insert their own analytics events; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can insert their own analytics events" ON public.analytics_events FOR INSERT WITH CHECK (((auth.uid() = user_id) OR (user_id IS NULL)));


--
-- Name: job_final_states Users can insert their own job states; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can insert their own job states" ON public.job_final_states FOR INSERT WITH CHECK ((auth.uid() = user_id));


--
-- Name: performance_metrics Users can insert their own metrics; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can insert their own metrics" ON public.performance_metrics FOR INSERT WITH CHECK ((auth.uid() = user_id));


--
-- Name: module_status Users can insert their own module status; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can insert their own module status" ON public.module_status FOR INSERT WITH CHECK ((auth.uid() = user_id));


--
-- Name: payments Users can insert their own payments; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can insert their own payments" ON public.payments FOR INSERT WITH CHECK ((auth.uid() = user_id));


--
-- Name: profiles Users can insert their own profile; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can insert their own profile" ON public.profiles FOR INSERT TO authenticated WITH CHECK ((auth.uid() = user_id));


--
-- Name: system_metrics Users can insert their own system metrics; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can insert their own system metrics" ON public.system_metrics FOR INSERT WITH CHECK ((auth.uid() = user_id));


--
-- Name: metrics_aggregated Users can manage own aggregated metrics; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own aggregated metrics" ON public.metrics_aggregated USING ((user_id = auth.uid()));


--
-- Name: anomalies Users can manage own anomalies; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own anomalies" ON public.anomalies USING ((user_id = auth.uid()));


--
-- Name: backup_metadata Users can manage own backups; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own backups" ON public.backup_metadata USING ((user_id = auth.uid()));


--
-- Name: user_behaviors Users can manage own behaviors; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own behaviors" ON public.user_behaviors USING ((user_id = auth.uid()));


--
-- Name: quantum_benchmarks Users can manage own benchmarks; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own benchmarks" ON public.quantum_benchmarks USING ((user_id = auth.uid()));


--
-- Name: budget_allocations Users can manage own budgets; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own budgets" ON public.budget_allocations USING ((user_id = auth.uid()));


--
-- Name: quantum_circuits Users can manage own circuits; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own circuits" ON public.quantum_circuits USING ((user_id = auth.uid()));


--
-- Name: compliance_checks Users can manage own compliance checks; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own compliance checks" ON public.compliance_checks USING ((user_id = auth.uid()));


--
-- Name: correlations Users can manage own correlations; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own correlations" ON public.correlations USING ((user_id = auth.uid()));


--
-- Name: cost_predictions Users can manage own cost predictions; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own cost predictions" ON public.cost_predictions USING ((user_id = auth.uid()));


--
-- Name: cost_transactions Users can manage own cost transactions; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own cost transactions" ON public.cost_transactions USING ((user_id = auth.uid()));


--
-- Name: analytics_dashboards Users can manage own dashboards; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own dashboards" ON public.analytics_dashboards USING ((user_id = auth.uid()));


--
-- Name: device_registry Users can manage own devices; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own devices" ON public.device_registry USING ((auth.uid() = user_id));


--
-- Name: failover_events Users can manage own failovers; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own failovers" ON public.failover_events USING ((user_id = auth.uid()));


--
-- Name: fused_models Users can manage own fused models; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own fused models" ON public.fused_models USING ((user_id = auth.uid()));


--
-- Name: fusion_strategies Users can manage own fusion strategies; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own fusion strategies" ON public.fusion_strategies USING ((user_id = auth.uid()));


--
-- Name: graphics_benchmarks Users can manage own graphics benchmarks; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own graphics benchmarks" ON public.graphics_benchmarks USING ((user_id = auth.uid()));


--
-- Name: system_health Users can manage own health; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own health" ON public.system_health USING ((auth.uid() = user_id));


--
-- Name: incidents Users can manage own incidents; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own incidents" ON public.incidents USING ((user_id = auth.uid()));


--
-- Name: integrations Users can manage own integrations; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own integrations" ON public.integrations USING ((user_id = auth.uid()));


--
-- Name: offline_packages Users can manage own offline packages; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own offline packages" ON public.offline_packages USING ((user_id = auth.uid()));


--
-- Name: persistent_compute_jobs Users can manage own persistent jobs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own persistent jobs" ON public.persistent_compute_jobs USING ((user_id = auth.uid()));


--
-- Name: personalization_settings Users can manage own personalization; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own personalization" ON public.personalization_settings USING ((user_id = auth.uid()));


--
-- Name: billing_cost_predictions Users can manage own predictions; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own predictions" ON public.billing_cost_predictions USING ((auth.uid() = user_id));


--
-- Name: quantum_jobs Users can manage own quantum jobs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own quantum jobs" ON public.quantum_jobs USING ((user_id = auth.uid()));


--
-- Name: metrics_raw Users can manage own raw metrics; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own raw metrics" ON public.metrics_raw USING ((user_id = auth.uid()));


--
-- Name: recommendations Users can manage own recommendations; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own recommendations" ON public.recommendations USING ((user_id = auth.uid()));


--
-- Name: analytics_reports Users can manage own reports; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own reports" ON public.analytics_reports USING ((user_id = auth.uid()));


--
-- Name: traces Users can manage own traces; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own traces" ON public.traces USING ((user_id = auth.uid()));


--
-- Name: distributed_training_jobs Users can manage own training jobs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own training jobs" ON public.distributed_training_jobs USING ((user_id = auth.uid()));


--
-- Name: marketplace_transactions Users can manage own transactions; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own transactions" ON public.marketplace_transactions USING ((user_id = auth.uid()));


--
-- Name: video_benchmarks Users can manage own video benchmarks; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own video benchmarks" ON public.video_benchmarks USING ((user_id = auth.uid()));


--
-- Name: custom_visualizations Users can manage own visualizations; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can manage own visualizations" ON public.custom_visualizations USING ((user_id = auth.uid()));


--
-- Name: profiles Users can only view own profile; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can only view own profile" ON public.profiles FOR SELECT USING ((auth.uid() = user_id));


--
-- Name: api_keys Users can update own api_keys; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can update own api_keys" ON public.api_keys FOR UPDATE USING ((auth.uid() = user_id));


--
-- Name: cache_metadata Users can update own cache metadata; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can update own cache metadata" ON public.cache_metadata FOR UPDATE USING ((user_id = auth.uid()));


--
-- Name: cloud_providers Users can update own cloud providers; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can update own cloud providers" ON public.cloud_providers FOR UPDATE USING ((user_id = auth.uid()));


--
-- Name: collaboration_comments Users can update own comments; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can update own comments" ON public.collaboration_comments FOR UPDATE USING ((user_id = auth.uid()));


--
-- Name: distillation_jobs Users can update own distillation jobs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can update own distillation jobs" ON public.distillation_jobs FOR UPDATE USING ((user_id = auth.uid()));


--
-- Name: distilled_models Users can update own distilled models; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can update own distilled models" ON public.distilled_models FOR UPDATE USING ((user_id = auth.uid()));


--
-- Name: cloud_routing_rules Users can update own routing rules; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can update own routing rules" ON public.cloud_routing_rules FOR UPDATE USING ((user_id = auth.uid()));


--
-- Name: scaling_actions Users can update own scaling actions; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can update own scaling actions" ON public.scaling_actions FOR UPDATE USING ((user_id = auth.uid()));


--
-- Name: billing_subscriptions Users can update own subscriptions; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can update own subscriptions" ON public.billing_subscriptions FOR UPDATE USING ((auth.uid() = user_id));


--
-- Name: billing_usage_records Users can update own usage; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can update own usage" ON public.billing_usage_records FOR UPDATE USING ((auth.uid() = user_id));


--
-- Name: cache_warming_jobs Users can update own warming jobs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can update own warming jobs" ON public.cache_warming_jobs FOR UPDATE USING ((user_id = auth.uid()));


--
-- Name: api_keys Users can update their own API keys; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can update their own API keys" ON public.api_keys FOR UPDATE TO authenticated USING ((auth.uid() = user_id));


--
-- Name: alerts Users can update their own alerts; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can update their own alerts" ON public.alerts FOR UPDATE USING ((auth.uid() = user_id));


--
-- Name: enterprise_requests Users can update their own enterprise requests; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can update their own enterprise requests" ON public.enterprise_requests FOR UPDATE TO authenticated USING ((auth.uid() = user_id));


--
-- Name: job_final_states Users can update their own job states; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can update their own job states" ON public.job_final_states FOR UPDATE USING ((auth.uid() = user_id));


--
-- Name: inference_jobs Users can update their own jobs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can update their own jobs" ON public.inference_jobs FOR UPDATE USING ((auth.uid() = user_id));


--
-- Name: jobs Users can update their own jobs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can update their own jobs" ON public.jobs FOR UPDATE USING ((auth.uid() = user_id));


--
-- Name: models Users can update their own models; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can update their own models" ON public.models FOR UPDATE USING ((auth.uid() = user_id));


--
-- Name: module_configs Users can update their own module configs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can update their own module configs" ON public.module_configs FOR UPDATE USING ((auth.uid() = user_id));


--
-- Name: module_status Users can update their own module status; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can update their own module status" ON public.module_status FOR UPDATE USING ((auth.uid() = user_id));


--
-- Name: profiles Users can update their own profile; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can update their own profile" ON public.profiles FOR UPDATE TO authenticated USING ((auth.uid() = user_id));


--
-- Name: subscriptions Users can update their own subscription; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can update their own subscription" ON public.subscriptions FOR UPDATE USING ((auth.uid() = user_id));


--
-- Name: cloud_costs Users can view costs for own providers; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view costs for own providers" ON public.cloud_costs FOR SELECT USING ((EXISTS ( SELECT 1
   FROM public.cloud_providers
  WHERE ((cloud_providers.id = cloud_costs.provider_id) AND (cloud_providers.user_id = auth.uid())))));


--
-- Name: fusion_performance_log Users can view fusion performance; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view fusion performance" ON public.fusion_performance_log FOR SELECT USING ((EXISTS ( SELECT 1
   FROM public.fused_models
  WHERE ((fused_models.id = fusion_performance_log.fused_model_id) AND (fused_models.user_id = auth.uid())))));


--
-- Name: cloud_latencies Users can view latencies for own providers; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view latencies for own providers" ON public.cloud_latencies FOR SELECT USING ((EXISTS ( SELECT 1
   FROM public.cloud_providers
  WHERE ((cloud_providers.id = cloud_latencies.provider_id) AND (cloud_providers.user_id = auth.uid())))));


--
-- Name: distillation_metrics Users can view metrics for own jobs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view metrics for own jobs" ON public.distillation_metrics FOR SELECT USING ((EXISTS ( SELECT 1
   FROM public.distillation_jobs
  WHERE ((distillation_jobs.id = distillation_metrics.distillation_job_id) AND (distillation_jobs.user_id = auth.uid())))));


--
-- Name: api_keys Users can view own api_keys; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view own api_keys" ON public.api_keys FOR SELECT USING ((auth.uid() = user_id));


--
-- Name: immutable_audit_logs Users can view own audit logs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view own audit logs" ON public.immutable_audit_logs FOR SELECT USING (((user_id = auth.uid()) OR (user_id IS NULL)));


--
-- Name: cache_analytics Users can view own cache analytics; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view own cache analytics" ON public.cache_analytics FOR SELECT USING ((user_id = auth.uid()));


--
-- Name: cache_metadata Users can view own cache metadata; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view own cache metadata" ON public.cache_metadata FOR SELECT USING ((user_id = auth.uid()));


--
-- Name: cloud_providers Users can view own cloud providers; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view own cloud providers" ON public.cloud_providers FOR SELECT USING ((user_id = auth.uid()));


--
-- Name: cost_analysis Users can view own cost analysis; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view own cost analysis" ON public.cost_analysis FOR SELECT USING ((user_id = auth.uid()));


--
-- Name: distillation_jobs Users can view own distillation jobs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view own distillation jobs" ON public.distillation_jobs FOR SELECT USING ((user_id = auth.uid()));


--
-- Name: distilled_models Users can view own distilled models; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view own distilled models" ON public.distilled_models FOR SELECT USING ((user_id = auth.uid()));


--
-- Name: semantic_embeddings Users can view own embeddings; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view own embeddings" ON public.semantic_embeddings FOR SELECT USING ((user_id = auth.uid()));


--
-- Name: cloud_failover_log Users can view own failover logs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view own failover logs" ON public.cloud_failover_log FOR SELECT USING ((user_id = auth.uid()));


--
-- Name: cache_invalidation_log Users can view own invalidation logs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view own invalidation logs" ON public.cache_invalidation_log FOR SELECT USING ((user_id = auth.uid()));


--
-- Name: models Users can view own models; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view own models" ON public.models FOR SELECT USING ((auth.uid() = user_id));


--
-- Name: prediction_accuracy Users can view own prediction accuracy; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view own prediction accuracy" ON public.prediction_accuracy FOR SELECT USING ((user_id = auth.uid()));


--
-- Name: workload_predictions Users can view own predictions; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view own predictions" ON public.workload_predictions FOR SELECT USING ((user_id = auth.uid()));


--
-- Name: quantum_results Users can view own quantum results; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view own quantum results" ON public.quantum_results FOR SELECT USING ((EXISTS ( SELECT 1
   FROM public.quantum_jobs
  WHERE ((quantum_jobs.id = quantum_results.job_id) AND (quantum_jobs.user_id = auth.uid())))));


--
-- Name: cloud_routing_rules Users can view own routing rules; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view own routing rules" ON public.cloud_routing_rules FOR SELECT USING ((user_id = auth.uid()));


--
-- Name: scaling_actions Users can view own scaling actions; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view own scaling actions" ON public.scaling_actions FOR SELECT USING ((user_id = auth.uid()));


--
-- Name: security_events Users can view own security events; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view own security events" ON public.security_events FOR SELECT USING (((user_id = auth.uid()) OR (user_id IS NULL)));


--
-- Name: billing_subscriptions Users can view own subscriptions; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view own subscriptions" ON public.billing_subscriptions FOR SELECT USING ((auth.uid() = user_id));


--
-- Name: threats_detected Users can view own threats; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view own threats" ON public.threats_detected FOR SELECT USING (((user_id = auth.uid()) OR (user_id IS NULL)));


--
-- Name: billing_usage_records Users can view own usage; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view own usage" ON public.billing_usage_records FOR SELECT USING ((auth.uid() = user_id));


--
-- Name: cache_warming_jobs Users can view own warming jobs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view own warming jobs" ON public.cache_warming_jobs FOR SELECT USING ((user_id = auth.uid()));


--
-- Name: webhook_test_log Users can view own webhook tests; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view own webhook tests" ON public.webhook_test_log FOR SELECT USING ((auth.uid() = user_id));


--
-- Name: models Users can view public models; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view public models" ON public.models FOR SELECT USING ((is_public = true));


--
-- Name: collaboration_sessions Users can view sessions they participate in; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view sessions they participate in" ON public.collaboration_sessions FOR SELECT TO authenticated USING (((owner_id = auth.uid()) OR (EXISTS ( SELECT 1
   FROM public.collaboration_participants
  WHERE ((collaboration_participants.session_id = collaboration_sessions.id) AND (collaboration_participants.user_id = auth.uid()))))));


--
-- Name: api_keys Users can view their own API keys safely; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view their own API keys safely" ON public.api_keys FOR SELECT USING ((auth.uid() = user_id));


--
-- Name: alerts Users can view their own alerts; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view their own alerts" ON public.alerts FOR SELECT USING ((auth.uid() = user_id));


--
-- Name: analytics_events Users can view their own analytics events; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view their own analytics events" ON public.analytics_events FOR SELECT USING ((auth.uid() = user_id));


--
-- Name: enterprise_requests Users can view their own enterprise requests; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view their own enterprise requests" ON public.enterprise_requests FOR SELECT TO authenticated USING ((auth.uid() = user_id));


--
-- Name: error_logs Users can view their own error logs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view their own error logs" ON public.error_logs FOR SELECT USING ((auth.uid() = user_id));


--
-- Name: job_logs Users can view their own job logs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view their own job logs" ON public.job_logs FOR SELECT USING ((EXISTS ( SELECT 1
   FROM public.gpu_jobs
  WHERE ((gpu_jobs.id = job_logs.job_id) AND (gpu_jobs.user_id = auth.uid())))));


--
-- Name: job_queue Users can view their own job queue entries; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view their own job queue entries" ON public.job_queue FOR SELECT USING ((EXISTS ( SELECT 1
   FROM public.gpu_jobs
  WHERE ((gpu_jobs.id = job_queue.job_id) AND (gpu_jobs.user_id = auth.uid())))));


--
-- Name: job_results Users can view their own job results; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view their own job results" ON public.job_results FOR SELECT USING ((EXISTS ( SELECT 1
   FROM public.gpu_jobs
  WHERE ((gpu_jobs.id = job_results.job_id) AND (gpu_jobs.user_id = auth.uid())))));


--
-- Name: job_final_states Users can view their own job states; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view their own job states" ON public.job_final_states FOR SELECT USING ((auth.uid() = user_id));


--
-- Name: gpu_jobs Users can view their own jobs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view their own jobs" ON public.gpu_jobs FOR SELECT USING ((auth.uid() = user_id));


--
-- Name: inference_jobs Users can view their own jobs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view their own jobs" ON public.inference_jobs FOR SELECT USING ((auth.uid() = user_id));


--
-- Name: jobs Users can view their own jobs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view their own jobs" ON public.jobs FOR SELECT USING ((auth.uid() = user_id));


--
-- Name: expectation_locks Users can view their own locks; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view their own locks" ON public.expectation_locks FOR SELECT USING ((auth.uid() = user_id));


--
-- Name: performance_metrics Users can view their own metrics; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view their own metrics" ON public.performance_metrics FOR SELECT USING ((auth.uid() = user_id));


--
-- Name: models Users can view their own models; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view their own models" ON public.models FOR SELECT USING ((auth.uid() = user_id));


--
-- Name: module_configs Users can view their own module configs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view their own module configs" ON public.module_configs FOR SELECT USING ((auth.uid() = user_id));


--
-- Name: module_status Users can view their own module status; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view their own module status" ON public.module_status FOR SELECT USING ((auth.uid() = user_id));


--
-- Name: payments Users can view their own payments; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view their own payments" ON public.payments FOR SELECT USING ((auth.uid() = user_id));


--
-- Name: profiles Users can view their own profile; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view their own profile" ON public.profiles FOR SELECT TO authenticated USING ((auth.uid() = user_id));


--
-- Name: user_roles Users can view their own roles; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view their own roles" ON public.user_roles FOR SELECT USING ((auth.uid() = user_id));


--
-- Name: subscriptions Users can view their own subscription; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view their own subscription" ON public.subscriptions FOR SELECT USING ((auth.uid() = user_id));


--
-- Name: system_metrics Users can view their own system metrics; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view their own system metrics" ON public.system_metrics FOR SELECT USING ((auth.uid() = user_id));


--
-- Name: usage_stats Users can view their own usage stats; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view their own usage stats" ON public.usage_stats FOR SELECT USING ((auth.uid() = user_id));


--
-- Name: knowledge_transfer_logs Users can view transfer logs for own jobs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view transfer logs for own jobs" ON public.knowledge_transfer_logs FOR SELECT USING ((EXISTS ( SELECT 1
   FROM public.distillation_jobs
  WHERE ((distillation_jobs.id = knowledge_transfer_logs.distillation_job_id) AND (distillation_jobs.user_id = auth.uid())))));


--
-- Name: agent_heartbeats; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.agent_heartbeats ENABLE ROW LEVEL SECURITY;

--
-- Name: agent_tokens; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.agent_tokens ENABLE ROW LEVEL SECURITY;

--
-- Name: alerts; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.alerts ENABLE ROW LEVEL SECURITY;

--
-- Name: analytics_dashboards; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.analytics_dashboards ENABLE ROW LEVEL SECURITY;

--
-- Name: analytics_events; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.analytics_events ENABLE ROW LEVEL SECURITY;

--
-- Name: analytics_reports; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.analytics_reports ENABLE ROW LEVEL SECURITY;

--
-- Name: anomalies; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.anomalies ENABLE ROW LEVEL SECURITY;

--
-- Name: api_keys; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;

--
-- Name: approval_workflows; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.approval_workflows ENABLE ROW LEVEL SECURITY;

--
-- Name: backup_metadata; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.backup_metadata ENABLE ROW LEVEL SECURITY;

--
-- Name: billing_cost_predictions; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.billing_cost_predictions ENABLE ROW LEVEL SECURITY;

--
-- Name: billing_subscriptions; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.billing_subscriptions ENABLE ROW LEVEL SECURITY;

--
-- Name: billing_usage_records; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.billing_usage_records ENABLE ROW LEVEL SECURITY;

--
-- Name: budget_allocations; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.budget_allocations ENABLE ROW LEVEL SECURITY;

--
-- Name: cache_analytics; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.cache_analytics ENABLE ROW LEVEL SECURITY;

--
-- Name: cache_invalidation_log; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.cache_invalidation_log ENABLE ROW LEVEL SECURITY;

--
-- Name: cache_metadata; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.cache_metadata ENABLE ROW LEVEL SECURITY;

--
-- Name: cache_warming_jobs; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.cache_warming_jobs ENABLE ROW LEVEL SECURITY;

--
-- Name: cloud_costs; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.cloud_costs ENABLE ROW LEVEL SECURITY;

--
-- Name: cloud_failover_log; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.cloud_failover_log ENABLE ROW LEVEL SECURITY;

--
-- Name: cloud_latencies; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.cloud_latencies ENABLE ROW LEVEL SECURITY;

--
-- Name: cloud_providers; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.cloud_providers ENABLE ROW LEVEL SECURITY;

--
-- Name: cloud_routing_rules; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.cloud_routing_rules ENABLE ROW LEVEL SECURITY;

--
-- Name: collaboration_changes; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.collaboration_changes ENABLE ROW LEVEL SECURITY;

--
-- Name: collaboration_comments; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.collaboration_comments ENABLE ROW LEVEL SECURITY;

--
-- Name: collaboration_messages; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.collaboration_messages ENABLE ROW LEVEL SECURITY;

--
-- Name: collaboration_participants; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.collaboration_participants ENABLE ROW LEVEL SECURITY;

--
-- Name: collaboration_sessions; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.collaboration_sessions ENABLE ROW LEVEL SECURITY;

--
-- Name: collaboration_votes; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.collaboration_votes ENABLE ROW LEVEL SECURITY;

--
-- Name: compliance_checks; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.compliance_checks ENABLE ROW LEVEL SECURITY;

--
-- Name: correlations; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.correlations ENABLE ROW LEVEL SECURITY;

--
-- Name: cost_analysis; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.cost_analysis ENABLE ROW LEVEL SECURITY;

--
-- Name: cost_predictions; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.cost_predictions ENABLE ROW LEVEL SECURITY;

--
-- Name: cost_transactions; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.cost_transactions ENABLE ROW LEVEL SECURITY;

--
-- Name: custom_roles; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.custom_roles ENABLE ROW LEVEL SECURITY;

--
-- Name: custom_visualizations; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.custom_visualizations ENABLE ROW LEVEL SECURITY;

--
-- Name: device_registry; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.device_registry ENABLE ROW LEVEL SECURITY;

--
-- Name: distillation_jobs; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.distillation_jobs ENABLE ROW LEVEL SECURITY;

--
-- Name: distillation_metrics; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.distillation_metrics ENABLE ROW LEVEL SECURITY;

--
-- Name: distilled_models; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.distilled_models ENABLE ROW LEVEL SECURITY;

--
-- Name: distributed_training_jobs; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.distributed_training_jobs ENABLE ROW LEVEL SECURITY;

--
-- Name: enterprise_requests; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.enterprise_requests ENABLE ROW LEVEL SECURITY;

--
-- Name: error_logs; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.error_logs ENABLE ROW LEVEL SECURITY;

--
-- Name: expectation_locks; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.expectation_locks ENABLE ROW LEVEL SECURITY;

--
-- Name: failover_events; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.failover_events ENABLE ROW LEVEL SECURITY;

--
-- Name: fused_models; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.fused_models ENABLE ROW LEVEL SECURITY;

--
-- Name: fusion_performance_log; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.fusion_performance_log ENABLE ROW LEVEL SECURITY;

--
-- Name: fusion_strategies; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.fusion_strategies ENABLE ROW LEVEL SECURITY;

--
-- Name: gpu_jobs; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.gpu_jobs ENABLE ROW LEVEL SECURITY;

--
-- Name: gpu_system_status; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.gpu_system_status ENABLE ROW LEVEL SECURITY;

--
-- Name: graphics_benchmarks; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.graphics_benchmarks ENABLE ROW LEVEL SECURITY;

--
-- Name: immutable_audit_logs; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.immutable_audit_logs ENABLE ROW LEVEL SECURITY;

--
-- Name: incidents; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.incidents ENABLE ROW LEVEL SECURITY;

--
-- Name: inference_jobs; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.inference_jobs ENABLE ROW LEVEL SECURITY;

--
-- Name: integrations; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.integrations ENABLE ROW LEVEL SECURITY;

--
-- Name: job_final_states; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.job_final_states ENABLE ROW LEVEL SECURITY;

--
-- Name: job_logs; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.job_logs ENABLE ROW LEVEL SECURITY;

--
-- Name: job_queue; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.job_queue ENABLE ROW LEVEL SECURITY;

--
-- Name: job_results; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.job_results ENABLE ROW LEVEL SECURITY;

--
-- Name: jobs; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;

--
-- Name: knowledge_transfer_logs; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.knowledge_transfer_logs ENABLE ROW LEVEL SECURITY;

--
-- Name: marketplace_transactions; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.marketplace_transactions ENABLE ROW LEVEL SECURITY;

--
-- Name: metrics_aggregated; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.metrics_aggregated ENABLE ROW LEVEL SECURITY;

--
-- Name: metrics_raw; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.metrics_raw ENABLE ROW LEVEL SECURITY;

--
-- Name: models; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.models ENABLE ROW LEVEL SECURITY;

--
-- Name: module_configs; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.module_configs ENABLE ROW LEVEL SECURITY;

--
-- Name: module_locks; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.module_locks ENABLE ROW LEVEL SECURITY;

--
-- Name: module_status; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.module_status ENABLE ROW LEVEL SECURITY;

--
-- Name: offline_packages; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.offline_packages ENABLE ROW LEVEL SECURITY;

--
-- Name: owner_diagnostics; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.owner_diagnostics ENABLE ROW LEVEL SECURITY;

--
-- Name: payment_webhook_events; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.payment_webhook_events ENABLE ROW LEVEL SECURITY;

--
-- Name: payments; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;

--
-- Name: performance_metrics; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.performance_metrics ENABLE ROW LEVEL SECURITY;

--
-- Name: permissions; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.permissions ENABLE ROW LEVEL SECURITY;

--
-- Name: persistent_compute_jobs; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.persistent_compute_jobs ENABLE ROW LEVEL SECURITY;

--
-- Name: personalization_settings; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.personalization_settings ENABLE ROW LEVEL SECURITY;

--
-- Name: plugins; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.plugins ENABLE ROW LEVEL SECURITY;

--
-- Name: prediction_accuracy; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.prediction_accuracy ENABLE ROW LEVEL SECURITY;

--
-- Name: profiles; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

--
-- Name: quantum_benchmarks; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.quantum_benchmarks ENABLE ROW LEVEL SECURITY;

--
-- Name: quantum_circuits; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.quantum_circuits ENABLE ROW LEVEL SECURITY;

--
-- Name: quantum_jobs; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.quantum_jobs ENABLE ROW LEVEL SECURITY;

--
-- Name: quantum_results; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.quantum_results ENABLE ROW LEVEL SECURITY;

--
-- Name: recommendations; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.recommendations ENABLE ROW LEVEL SECURITY;

--
-- Name: scaling_actions; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.scaling_actions ENABLE ROW LEVEL SECURITY;

--
-- Name: security_events; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.security_events ENABLE ROW LEVEL SECURITY;

--
-- Name: semantic_embeddings; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.semantic_embeddings ENABLE ROW LEVEL SECURITY;

--
-- Name: subscriptions; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;

--
-- Name: system_health; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.system_health ENABLE ROW LEVEL SECURITY;

--
-- Name: system_metrics; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.system_metrics ENABLE ROW LEVEL SECURITY;

--
-- Name: system_settings; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.system_settings ENABLE ROW LEVEL SECURITY;

--
-- Name: team_members; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.team_members ENABLE ROW LEVEL SECURITY;

--
-- Name: teams; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.teams ENABLE ROW LEVEL SECURITY;

--
-- Name: threats_detected; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.threats_detected ENABLE ROW LEVEL SECURITY;

--
-- Name: traces; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.traces ENABLE ROW LEVEL SECURITY;

--
-- Name: usage_stats; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.usage_stats ENABLE ROW LEVEL SECURITY;

--
-- Name: user_behaviors; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.user_behaviors ENABLE ROW LEVEL SECURITY;

--
-- Name: user_roles; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.user_roles ENABLE ROW LEVEL SECURITY;

--
-- Name: video_benchmarks; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.video_benchmarks ENABLE ROW LEVEL SECURITY;

--
-- Name: webhook_test_log; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.webhook_test_log ENABLE ROW LEVEL SECURITY;

--
-- Name: worker_api_keys; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.worker_api_keys ENABLE ROW LEVEL SECURITY;

--
-- Name: workload_predictions; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.workload_predictions ENABLE ROW LEVEL SECURITY;

--
-- PostgreSQL database dump complete
--




COMMIT;