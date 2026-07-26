export type Json = string | number | boolean | null | { [key: string]: Json | undefined } | Json[];

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "14.1";
  };
  public: {
    Tables: {
      agent_heartbeats: {
        Row: {
          agent_token_id: string | null;
          cpu_temp_celsius: number | null;
          cpu_usage_percent: number | null;
          current_job_id: string | null;
          gpu_temp_celsius: number | null;
          gpu_vram_total_mb: number | null;
          gpu_vram_used_mb: number | null;
          id: string;
          is_processing: boolean | null;
          recorded_at: string;
          worker_id: string;
        };
        Insert: {
          agent_token_id?: string | null;
          cpu_temp_celsius?: number | null;
          cpu_usage_percent?: number | null;
          current_job_id?: string | null;
          gpu_temp_celsius?: number | null;
          gpu_vram_total_mb?: number | null;
          gpu_vram_used_mb?: number | null;
          id?: string;
          is_processing?: boolean | null;
          recorded_at?: string;
          worker_id: string;
        };
        Update: {
          agent_token_id?: string | null;
          cpu_temp_celsius?: number | null;
          cpu_usage_percent?: number | null;
          current_job_id?: string | null;
          gpu_temp_celsius?: number | null;
          gpu_vram_total_mb?: number | null;
          gpu_vram_used_mb?: number | null;
          id?: string;
          is_processing?: boolean | null;
          recorded_at?: string;
          worker_id?: string;
        };
        Relationships: [
          {
            foreignKeyName: "agent_heartbeats_agent_token_id_fkey";
            columns: ["agent_token_id"];
            isOneToOne: false;
            referencedRelation: "agent_tokens";
            referencedColumns: ["id"];
          },
          {
            foreignKeyName: "agent_heartbeats_current_job_id_fkey";
            columns: ["current_job_id"];
            isOneToOne: false;
            referencedRelation: "gpu_jobs";
            referencedColumns: ["id"];
          },
        ];
      };
      agent_tokens: {
        Row: {
          agent_name: string;
          allowed_until: string | null;
          capabilities: Json | null;
          created_at: string;
          id: string;
          is_active: boolean | null;
          last_used_at: string | null;
          secret_hash: string;
        };
        Insert: {
          agent_name: string;
          allowed_until?: string | null;
          capabilities?: Json | null;
          created_at?: string;
          id?: string;
          is_active?: boolean | null;
          last_used_at?: string | null;
          secret_hash: string;
        };
        Update: {
          agent_name?: string;
          allowed_until?: string | null;
          capabilities?: Json | null;
          created_at?: string;
          id?: string;
          is_active?: boolean | null;
          last_used_at?: string | null;
          secret_hash?: string;
        };
        Relationships: [];
      };
      alert_rules: {
        Row: {
          condition: string;
          cooldown_minutes: number | null;
          created_at: string;
          description: string | null;
          id: string;
          is_active: boolean | null;
          last_triggered_at: string | null;
          metric_name: string;
          name: string;
          notification_channels: Json | null;
          severity: string;
          threshold: number;
          updated_at: string;
        };
        Insert: {
          condition: string;
          cooldown_minutes?: number | null;
          created_at?: string;
          description?: string | null;
          id?: string;
          is_active?: boolean | null;
          last_triggered_at?: string | null;
          metric_name: string;
          name: string;
          notification_channels?: Json | null;
          severity?: string;
          threshold: number;
          updated_at?: string;
        };
        Update: {
          condition?: string;
          cooldown_minutes?: number | null;
          created_at?: string;
          description?: string | null;
          id?: string;
          is_active?: boolean | null;
          last_triggered_at?: string | null;
          metric_name?: string;
          name?: string;
          notification_channels?: Json | null;
          severity?: string;
          threshold?: number;
          updated_at?: string;
        };
        Relationships: [];
      };
      alerts: {
        Row: {
          alert_type: string;
          created_at: string;
          id: string;
          message: string;
          metadata: Json | null;
          module_name: string | null;
          resolved: boolean;
          resolved_at: string | null;
          severity: string;
          title: string;
          user_id: string;
        };
        Insert: {
          alert_type: string;
          created_at?: string;
          id?: string;
          message: string;
          metadata?: Json | null;
          module_name?: string | null;
          resolved?: boolean;
          resolved_at?: string | null;
          severity?: string;
          title: string;
          user_id: string;
        };
        Update: {
          alert_type?: string;
          created_at?: string;
          id?: string;
          message?: string;
          metadata?: Json | null;
          module_name?: string | null;
          resolved?: boolean;
          resolved_at?: string | null;
          severity?: string;
          title?: string;
          user_id?: string;
        };
        Relationships: [];
      };
      analytics_dashboards: {
        Row: {
          created_at: string;
          description: string | null;
          id: string;
          is_default: boolean | null;
          is_shared: boolean | null;
          layout: Json | null;
          name: string;
          updated_at: string;
          user_id: string;
          widgets: Json | null;
        };
        Insert: {
          created_at?: string;
          description?: string | null;
          id?: string;
          is_default?: boolean | null;
          is_shared?: boolean | null;
          layout?: Json | null;
          name: string;
          updated_at?: string;
          user_id: string;
          widgets?: Json | null;
        };
        Update: {
          created_at?: string;
          description?: string | null;
          id?: string;
          is_default?: boolean | null;
          is_shared?: boolean | null;
          layout?: Json | null;
          name?: string;
          updated_at?: string;
          user_id?: string;
          widgets?: Json | null;
        };
        Relationships: [];
      };
      analytics_events: {
        Row: {
          created_at: string;
          event_data: Json | null;
          event_type: string;
          id: string;
          page_path: string | null;
          user_id: string | null;
        };
        Insert: {
          created_at?: string;
          event_data?: Json | null;
          event_type: string;
          id?: string;
          page_path?: string | null;
          user_id?: string | null;
        };
        Update: {
          created_at?: string;
          event_data?: Json | null;
          event_type?: string;
          id?: string;
          page_path?: string | null;
          user_id?: string | null;
        };
        Relationships: [];
      };
      analytics_reports: {
        Row: {
          config: Json | null;
          created_at: string;
          description: string | null;
          id: string;
          last_generated_at: string | null;
          name: string;
          report_type: string;
          schedule: string | null;
          updated_at: string;
          user_id: string;
        };
        Insert: {
          config?: Json | null;
          created_at?: string;
          description?: string | null;
          id?: string;
          last_generated_at?: string | null;
          name: string;
          report_type: string;
          schedule?: string | null;
          updated_at?: string;
          user_id: string;
        };
        Update: {
          config?: Json | null;
          created_at?: string;
          description?: string | null;
          id?: string;
          last_generated_at?: string | null;
          name?: string;
          report_type?: string;
          schedule?: string | null;
          updated_at?: string;
          user_id?: string;
        };
        Relationships: [];
      };
      anomalies: {
        Row: {
          actual_value: number | null;
          anomaly_type: string;
          detected_at: string;
          deviation_percent: number | null;
          expected_value: number | null;
          id: string;
          is_resolved: boolean | null;
          metric_name: string;
          resolved_at: string | null;
          severity: string;
          user_id: string;
        };
        Insert: {
          actual_value?: number | null;
          anomaly_type: string;
          detected_at?: string;
          deviation_percent?: number | null;
          expected_value?: number | null;
          id?: string;
          is_resolved?: boolean | null;
          metric_name: string;
          resolved_at?: string | null;
          severity?: string;
          user_id: string;
        };
        Update: {
          actual_value?: number | null;
          anomaly_type?: string;
          detected_at?: string;
          deviation_percent?: number | null;
          expected_value?: number | null;
          id?: string;
          is_resolved?: boolean | null;
          metric_name?: string;
          resolved_at?: string | null;
          severity?: string;
          user_id?: string;
        };
        Relationships: [];
      };
      api_keys: {
        Row: {
          created_at: string;
          expires_at: string | null;
          id: string;
          is_active: boolean;
          key_hash: string | null;
          key_name: string;
          key_prefix: string | null;
          last_used_at: string | null;
          user_id: string;
        };
        Insert: {
          created_at?: string;
          expires_at?: string | null;
          id?: string;
          is_active?: boolean;
          key_hash?: string | null;
          key_name: string;
          key_prefix?: string | null;
          last_used_at?: string | null;
          user_id: string;
        };
        Update: {
          created_at?: string;
          expires_at?: string | null;
          id?: string;
          is_active?: boolean;
          key_hash?: string | null;
          key_name?: string;
          key_prefix?: string | null;
          last_used_at?: string | null;
          user_id?: string;
        };
        Relationships: [];
      };
      approval_workflows: {
        Row: {
          created_at: string;
          description: string | null;
          id: string;
          is_active: boolean | null;
          name: string;
          steps: Json | null;
          team_id: string | null;
          workflow_type: string;
        };
        Insert: {
          created_at?: string;
          description?: string | null;
          id?: string;
          is_active?: boolean | null;
          name: string;
          steps?: Json | null;
          team_id?: string | null;
          workflow_type: string;
        };
        Update: {
          created_at?: string;
          description?: string | null;
          id?: string;
          is_active?: boolean | null;
          name?: string;
          steps?: Json | null;
          team_id?: string | null;
          workflow_type?: string;
        };
        Relationships: [
          {
            foreignKeyName: "approval_workflows_team_id_fkey";
            columns: ["team_id"];
            isOneToOne: false;
            referencedRelation: "teams";
            referencedColumns: ["id"];
          },
        ];
      };
      automated_alerts: {
        Row: {
          acknowledged: boolean | null;
          acknowledged_at: string | null;
          acknowledged_by: string | null;
          created_at: string;
          id: string;
          message: string;
          metric_name: string;
          metric_value: number;
          resolved: boolean | null;
          resolved_at: string | null;
          rule_id: string | null;
          severity: string;
          threshold: number;
        };
        Insert: {
          acknowledged?: boolean | null;
          acknowledged_at?: string | null;
          acknowledged_by?: string | null;
          created_at?: string;
          id?: string;
          message: string;
          metric_name: string;
          metric_value: number;
          resolved?: boolean | null;
          resolved_at?: string | null;
          rule_id?: string | null;
          severity: string;
          threshold: number;
        };
        Update: {
          acknowledged?: boolean | null;
          acknowledged_at?: string | null;
          acknowledged_by?: string | null;
          created_at?: string;
          id?: string;
          message?: string;
          metric_name?: string;
          metric_value?: number;
          resolved?: boolean | null;
          resolved_at?: string | null;
          rule_id?: string | null;
          severity?: string;
          threshold?: number;
        };
        Relationships: [
          {
            foreignKeyName: "automated_alerts_rule_id_fkey";
            columns: ["rule_id"];
            isOneToOne: false;
            referencedRelation: "alert_rules";
            referencedColumns: ["id"];
          },
        ];
      };
      backup_metadata: {
        Row: {
          backup_type: string;
          created_at: string;
          encrypted: boolean | null;
          expires_at: string | null;
          id: string;
          location: string | null;
          region: string | null;
          retention_days: number | null;
          size_bytes: number | null;
          status: string | null;
          user_id: string;
        };
        Insert: {
          backup_type: string;
          created_at?: string;
          encrypted?: boolean | null;
          expires_at?: string | null;
          id?: string;
          location?: string | null;
          region?: string | null;
          retention_days?: number | null;
          size_bytes?: number | null;
          status?: string | null;
          user_id: string;
        };
        Update: {
          backup_type?: string;
          created_at?: string;
          encrypted?: boolean | null;
          expires_at?: string | null;
          id?: string;
          location?: string | null;
          region?: string | null;
          retention_days?: number | null;
          size_bytes?: number | null;
          status?: string | null;
          user_id?: string;
        };
        Relationships: [];
      };
      billing_cost_predictions: {
        Row: {
          created_at: string;
          id: string;
          month: string;
          predicted_cost: number;
          user_id: string;
        };
        Insert: {
          created_at?: string;
          id?: string;
          month: string;
          predicted_cost?: number;
          user_id: string;
        };
        Update: {
          created_at?: string;
          id?: string;
          month?: string;
          predicted_cost?: number;
          user_id?: string;
        };
        Relationships: [];
      };
      billing_subscriptions: {
        Row: {
          cancelled_at: string | null;
          created_at: string;
          id: string;
          plan: string;
          renewed_at: string | null;
          started_at: string;
          status: string;
          user_id: string;
        };
        Insert: {
          cancelled_at?: string | null;
          created_at?: string;
          id?: string;
          plan?: string;
          renewed_at?: string | null;
          started_at?: string;
          status?: string;
          user_id: string;
        };
        Update: {
          cancelled_at?: string | null;
          created_at?: string;
          id?: string;
          plan?: string;
          renewed_at?: string | null;
          started_at?: string;
          status?: string;
          user_id?: string;
        };
        Relationships: [];
      };
      billing_usage_records: {
        Row: {
          computed_cost: number | null;
          created_at: string;
          id: string;
          inference_tokens: number | null;
          month: string;
          rendering_hours: number | null;
          storage_gb: number | null;
          training_hours: number | null;
          user_id: string;
        };
        Insert: {
          computed_cost?: number | null;
          created_at?: string;
          id?: string;
          inference_tokens?: number | null;
          month: string;
          rendering_hours?: number | null;
          storage_gb?: number | null;
          training_hours?: number | null;
          user_id: string;
        };
        Update: {
          computed_cost?: number | null;
          created_at?: string;
          id?: string;
          inference_tokens?: number | null;
          month?: string;
          rendering_hours?: number | null;
          storage_gb?: number | null;
          training_hours?: number | null;
          user_id?: string;
        };
        Relationships: [];
      };
      budget_allocations: {
        Row: {
          alert_threshold: number | null;
          category: string | null;
          created_at: string;
          id: string;
          is_active: boolean | null;
          name: string;
          period_end: string;
          period_start: string;
          spent_amount: number | null;
          total_budget: number;
          user_id: string;
        };
        Insert: {
          alert_threshold?: number | null;
          category?: string | null;
          created_at?: string;
          id?: string;
          is_active?: boolean | null;
          name: string;
          period_end: string;
          period_start: string;
          spent_amount?: number | null;
          total_budget: number;
          user_id: string;
        };
        Update: {
          alert_threshold?: number | null;
          category?: string | null;
          created_at?: string;
          id?: string;
          is_active?: boolean | null;
          name?: string;
          period_end?: string;
          period_start?: string;
          spent_amount?: number | null;
          total_budget?: number;
          user_id?: string;
        };
        Relationships: [];
      };
      cache_analytics: {
        Row: {
          avg_response_time_saved_ms: number | null;
          cache_level: string;
          evictions: number | null;
          hits: number | null;
          id: string;
          misses: number | null;
          recorded_at: string;
          total_size_bytes: number | null;
          user_id: string;
        };
        Insert: {
          avg_response_time_saved_ms?: number | null;
          cache_level: string;
          evictions?: number | null;
          hits?: number | null;
          id?: string;
          misses?: number | null;
          recorded_at?: string;
          total_size_bytes?: number | null;
          user_id: string;
        };
        Update: {
          avg_response_time_saved_ms?: number | null;
          cache_level?: string;
          evictions?: number | null;
          hits?: number | null;
          id?: string;
          misses?: number | null;
          recorded_at?: string;
          total_size_bytes?: number | null;
          user_id?: string;
        };
        Relationships: [];
      };
      cache_invalidation_log: {
        Row: {
          affected_keys: number | null;
          cache_level: string;
          created_at: string;
          id: string;
          invalidation_type: string;
          reason: string | null;
          user_id: string;
        };
        Insert: {
          affected_keys?: number | null;
          cache_level: string;
          created_at?: string;
          id?: string;
          invalidation_type: string;
          reason?: string | null;
          user_id: string;
        };
        Update: {
          affected_keys?: number | null;
          cache_level?: string;
          created_at?: string;
          id?: string;
          invalidation_type?: string;
          reason?: string | null;
          user_id?: string;
        };
        Relationships: [];
      };
      cache_metadata: {
        Row: {
          cache_key: string;
          cache_level: string;
          content_type: string | null;
          created_at: string;
          expires_at: string | null;
          hit_count: number | null;
          id: string;
          last_accessed_at: string | null;
          size_bytes: number | null;
          user_id: string;
        };
        Insert: {
          cache_key: string;
          cache_level: string;
          content_type?: string | null;
          created_at?: string;
          expires_at?: string | null;
          hit_count?: number | null;
          id?: string;
          last_accessed_at?: string | null;
          size_bytes?: number | null;
          user_id: string;
        };
        Update: {
          cache_key?: string;
          cache_level?: string;
          content_type?: string | null;
          created_at?: string;
          expires_at?: string | null;
          hit_count?: number | null;
          id?: string;
          last_accessed_at?: string | null;
          size_bytes?: number | null;
          user_id?: string;
        };
        Relationships: [];
      };
      cache_warming_jobs: {
        Row: {
          completed_at: string | null;
          created_at: string;
          id: string;
          items_to_warm: number | null;
          items_warmed: number | null;
          job_type: string;
          started_at: string | null;
          status: string;
          target_cache_level: string | null;
          trigger_reason: string | null;
          user_id: string;
        };
        Insert: {
          completed_at?: string | null;
          created_at?: string;
          id?: string;
          items_to_warm?: number | null;
          items_warmed?: number | null;
          job_type: string;
          started_at?: string | null;
          status?: string;
          target_cache_level?: string | null;
          trigger_reason?: string | null;
          user_id: string;
        };
        Update: {
          completed_at?: string | null;
          created_at?: string;
          id?: string;
          items_to_warm?: number | null;
          items_warmed?: number | null;
          job_type?: string;
          started_at?: string | null;
          status?: string;
          target_cache_level?: string | null;
          trigger_reason?: string | null;
          user_id?: string;
        };
        Relationships: [];
      };
      cloud_costs: {
        Row: {
          cost_per_hour: number | null;
          cost_per_request: number | null;
          id: string;
          provider_id: string | null;
          recorded_at: string;
          resource_type: string;
        };
        Insert: {
          cost_per_hour?: number | null;
          cost_per_request?: number | null;
          id?: string;
          provider_id?: string | null;
          recorded_at?: string;
          resource_type: string;
        };
        Update: {
          cost_per_hour?: number | null;
          cost_per_request?: number | null;
          id?: string;
          provider_id?: string | null;
          recorded_at?: string;
          resource_type?: string;
        };
        Relationships: [
          {
            foreignKeyName: "cloud_costs_provider_id_fkey";
            columns: ["provider_id"];
            isOneToOne: false;
            referencedRelation: "cloud_providers";
            referencedColumns: ["id"];
          },
        ];
      };
      cloud_failover_log: {
        Row: {
          created_at: string;
          duration_ms: number | null;
          from_provider_id: string | null;
          id: string;
          reason: string;
          success: boolean | null;
          to_provider_id: string | null;
          user_id: string;
        };
        Insert: {
          created_at?: string;
          duration_ms?: number | null;
          from_provider_id?: string | null;
          id?: string;
          reason: string;
          success?: boolean | null;
          to_provider_id?: string | null;
          user_id: string;
        };
        Update: {
          created_at?: string;
          duration_ms?: number | null;
          from_provider_id?: string | null;
          id?: string;
          reason?: string;
          success?: boolean | null;
          to_provider_id?: string | null;
          user_id?: string;
        };
        Relationships: [
          {
            foreignKeyName: "cloud_failover_log_from_provider_id_fkey";
            columns: ["from_provider_id"];
            isOneToOne: false;
            referencedRelation: "cloud_providers";
            referencedColumns: ["id"];
          },
          {
            foreignKeyName: "cloud_failover_log_to_provider_id_fkey";
            columns: ["to_provider_id"];
            isOneToOne: false;
            referencedRelation: "cloud_providers";
            referencedColumns: ["id"];
          },
        ];
      };
      cloud_latencies: {
        Row: {
          endpoint_type: string;
          id: string;
          latency_ms: number;
          provider_id: string | null;
          recorded_at: string;
          success: boolean | null;
        };
        Insert: {
          endpoint_type: string;
          id?: string;
          latency_ms: number;
          provider_id?: string | null;
          recorded_at?: string;
          success?: boolean | null;
        };
        Update: {
          endpoint_type?: string;
          id?: string;
          latency_ms?: number;
          provider_id?: string | null;
          recorded_at?: string;
          success?: boolean | null;
        };
        Relationships: [
          {
            foreignKeyName: "cloud_latencies_provider_id_fkey";
            columns: ["provider_id"];
            isOneToOne: false;
            referencedRelation: "cloud_providers";
            referencedColumns: ["id"];
          },
        ];
      };
      cloud_providers: {
        Row: {
          capabilities: Json | null;
          created_at: string;
          credentials_configured: boolean | null;
          id: string;
          is_active: boolean | null;
          priority: number | null;
          provider_name: string;
          region: string;
          updated_at: string;
          user_id: string;
        };
        Insert: {
          capabilities?: Json | null;
          created_at?: string;
          credentials_configured?: boolean | null;
          id?: string;
          is_active?: boolean | null;
          priority?: number | null;
          provider_name: string;
          region: string;
          updated_at?: string;
          user_id: string;
        };
        Update: {
          capabilities?: Json | null;
          created_at?: string;
          credentials_configured?: boolean | null;
          id?: string;
          is_active?: boolean | null;
          priority?: number | null;
          provider_name?: string;
          region?: string;
          updated_at?: string;
          user_id?: string;
        };
        Relationships: [];
      };
      cloud_routing_rules: {
        Row: {
          conditions: Json | null;
          created_at: string;
          id: string;
          is_active: boolean | null;
          mode: string;
          name: string;
          user_id: string;
        };
        Insert: {
          conditions?: Json | null;
          created_at?: string;
          id?: string;
          is_active?: boolean | null;
          mode?: string;
          name: string;
          user_id: string;
        };
        Update: {
          conditions?: Json | null;
          created_at?: string;
          id?: string;
          is_active?: boolean | null;
          mode?: string;
          name?: string;
          user_id?: string;
        };
        Relationships: [];
      };
      collaboration_changes: {
        Row: {
          change_type: string;
          created_at: string;
          id: string;
          new_value: Json | null;
          previous_value: Json | null;
          session_id: string;
          target_module: string | null;
          user_id: string;
        };
        Insert: {
          change_type: string;
          created_at?: string;
          id?: string;
          new_value?: Json | null;
          previous_value?: Json | null;
          session_id: string;
          target_module?: string | null;
          user_id: string;
        };
        Update: {
          change_type?: string;
          created_at?: string;
          id?: string;
          new_value?: Json | null;
          previous_value?: Json | null;
          session_id?: string;
          target_module?: string | null;
          user_id?: string;
        };
        Relationships: [
          {
            foreignKeyName: "collaboration_changes_session_id_fkey";
            columns: ["session_id"];
            isOneToOne: false;
            referencedRelation: "collaboration_sessions";
            referencedColumns: ["id"];
          },
        ];
      };
      collaboration_comments: {
        Row: {
          content: string;
          created_at: string;
          id: string;
          mentions: string[] | null;
          module_name: string | null;
          parent_id: string | null;
          session_id: string;
          updated_at: string;
          user_id: string;
        };
        Insert: {
          content: string;
          created_at?: string;
          id?: string;
          mentions?: string[] | null;
          module_name?: string | null;
          parent_id?: string | null;
          session_id: string;
          updated_at?: string;
          user_id: string;
        };
        Update: {
          content?: string;
          created_at?: string;
          id?: string;
          mentions?: string[] | null;
          module_name?: string | null;
          parent_id?: string | null;
          session_id?: string;
          updated_at?: string;
          user_id?: string;
        };
        Relationships: [
          {
            foreignKeyName: "collaboration_comments_parent_id_fkey";
            columns: ["parent_id"];
            isOneToOne: false;
            referencedRelation: "collaboration_comments";
            referencedColumns: ["id"];
          },
          {
            foreignKeyName: "collaboration_comments_session_id_fkey";
            columns: ["session_id"];
            isOneToOne: false;
            referencedRelation: "collaboration_sessions";
            referencedColumns: ["id"];
          },
        ];
      };
      collaboration_messages: {
        Row: {
          content: string;
          created_at: string;
          id: string;
          mentions: string[] | null;
          session_id: string;
          user_id: string;
        };
        Insert: {
          content: string;
          created_at?: string;
          id?: string;
          mentions?: string[] | null;
          session_id: string;
          user_id: string;
        };
        Update: {
          content?: string;
          created_at?: string;
          id?: string;
          mentions?: string[] | null;
          session_id?: string;
          user_id?: string;
        };
        Relationships: [
          {
            foreignKeyName: "collaboration_messages_session_id_fkey";
            columns: ["session_id"];
            isOneToOne: false;
            referencedRelation: "collaboration_sessions";
            referencedColumns: ["id"];
          },
        ];
      };
      collaboration_participants: {
        Row: {
          cursor_position: Json | null;
          id: string;
          is_online: boolean | null;
          joined_at: string;
          last_active_at: string | null;
          role: string;
          session_id: string;
          user_id: string;
        };
        Insert: {
          cursor_position?: Json | null;
          id?: string;
          is_online?: boolean | null;
          joined_at?: string;
          last_active_at?: string | null;
          role?: string;
          session_id: string;
          user_id: string;
        };
        Update: {
          cursor_position?: Json | null;
          id?: string;
          is_online?: boolean | null;
          joined_at?: string;
          last_active_at?: string | null;
          role?: string;
          session_id?: string;
          user_id?: string;
        };
        Relationships: [
          {
            foreignKeyName: "collaboration_participants_session_id_fkey";
            columns: ["session_id"];
            isOneToOne: false;
            referencedRelation: "collaboration_sessions";
            referencedColumns: ["id"];
          },
        ];
      };
      collaboration_sessions: {
        Row: {
          archived_at: string | null;
          created_at: string;
          description: string | null;
          id: string;
          inference_job_id: string | null;
          name: string;
          owner_id: string;
          room_id: string;
          settings: Json | null;
          status: string;
          updated_at: string;
        };
        Insert: {
          archived_at?: string | null;
          created_at?: string;
          description?: string | null;
          id?: string;
          inference_job_id?: string | null;
          name: string;
          owner_id: string;
          room_id: string;
          settings?: Json | null;
          status?: string;
          updated_at?: string;
        };
        Update: {
          archived_at?: string | null;
          created_at?: string;
          description?: string | null;
          id?: string;
          inference_job_id?: string | null;
          name?: string;
          owner_id?: string;
          room_id?: string;
          settings?: Json | null;
          status?: string;
          updated_at?: string;
        };
        Relationships: [
          {
            foreignKeyName: "collaboration_sessions_inference_job_id_fkey";
            columns: ["inference_job_id"];
            isOneToOne: false;
            referencedRelation: "inference_jobs";
            referencedColumns: ["id"];
          },
        ];
      };
      collaboration_votes: {
        Row: {
          created_at: string;
          id: string;
          session_id: string;
          target_id: string | null;
          user_id: string;
          value: number;
          vote_type: string;
        };
        Insert: {
          created_at?: string;
          id?: string;
          session_id: string;
          target_id?: string | null;
          user_id: string;
          value?: number;
          vote_type: string;
        };
        Update: {
          created_at?: string;
          id?: string;
          session_id?: string;
          target_id?: string | null;
          user_id?: string;
          value?: number;
          vote_type?: string;
        };
        Relationships: [
          {
            foreignKeyName: "collaboration_votes_session_id_fkey";
            columns: ["session_id"];
            isOneToOne: false;
            referencedRelation: "collaboration_sessions";
            referencedColumns: ["id"];
          },
        ];
      };
      compliance_checks: {
        Row: {
          check_name: string;
          created_at: string;
          findings: Json | null;
          framework: string;
          id: string;
          last_run_at: string | null;
          next_run_at: string | null;
          score: number | null;
          status: string;
          user_id: string;
        };
        Insert: {
          check_name: string;
          created_at?: string;
          findings?: Json | null;
          framework: string;
          id?: string;
          last_run_at?: string | null;
          next_run_at?: string | null;
          score?: number | null;
          status?: string;
          user_id: string;
        };
        Update: {
          check_name?: string;
          created_at?: string;
          findings?: Json | null;
          framework?: string;
          id?: string;
          last_run_at?: string | null;
          next_run_at?: string | null;
          score?: number | null;
          status?: string;
          user_id?: string;
        };
        Relationships: [];
      };
      correlations: {
        Row: {
          calculated_at: string;
          confidence: number | null;
          correlation_coefficient: number | null;
          id: string;
          metric_a: string;
          metric_b: string;
          relationship_type: string | null;
          sample_size: number | null;
          user_id: string;
        };
        Insert: {
          calculated_at?: string;
          confidence?: number | null;
          correlation_coefficient?: number | null;
          id?: string;
          metric_a: string;
          metric_b: string;
          relationship_type?: string | null;
          sample_size?: number | null;
          user_id: string;
        };
        Update: {
          calculated_at?: string;
          confidence?: number | null;
          correlation_coefficient?: number | null;
          id?: string;
          metric_a?: string;
          metric_b?: string;
          relationship_type?: string | null;
          sample_size?: number | null;
          user_id?: string;
        };
        Relationships: [];
      };
      cost_analysis: {
        Row: {
          actual_cost: number | null;
          created_at: string;
          id: string;
          optimized_cost: number | null;
          period_end: string;
          period_start: string;
          recommendations: Json | null;
          resource_type: string;
          roi: number | null;
          savings: number | null;
          user_id: string;
        };
        Insert: {
          actual_cost?: number | null;
          created_at?: string;
          id?: string;
          optimized_cost?: number | null;
          period_end: string;
          period_start: string;
          recommendations?: Json | null;
          resource_type: string;
          roi?: number | null;
          savings?: number | null;
          user_id: string;
        };
        Update: {
          actual_cost?: number | null;
          created_at?: string;
          id?: string;
          optimized_cost?: number | null;
          period_end?: string;
          period_start?: string;
          recommendations?: Json | null;
          resource_type?: string;
          roi?: number | null;
          savings?: number | null;
          user_id?: string;
        };
        Relationships: [];
      };
      cost_predictions: {
        Row: {
          confidence_lower: number | null;
          confidence_upper: number | null;
          created_at: string;
          id: string;
          model_version: string | null;
          predicted_amount: number;
          prediction_date: string;
          prediction_period: string;
          resource_type: string;
          user_id: string;
        };
        Insert: {
          confidence_lower?: number | null;
          confidence_upper?: number | null;
          created_at?: string;
          id?: string;
          model_version?: string | null;
          predicted_amount: number;
          prediction_date: string;
          prediction_period: string;
          resource_type: string;
          user_id: string;
        };
        Update: {
          confidence_lower?: number | null;
          confidence_upper?: number | null;
          created_at?: string;
          id?: string;
          model_version?: string | null;
          predicted_amount?: number;
          prediction_date?: string;
          prediction_period?: string;
          resource_type?: string;
          user_id?: string;
        };
        Relationships: [];
      };
      cost_transactions: {
        Row: {
          amount: number;
          category: string | null;
          currency: string | null;
          id: string;
          provider: string | null;
          resource_id: string | null;
          resource_type: string;
          tags: Json | null;
          transaction_at: string;
          user_id: string;
        };
        Insert: {
          amount: number;
          category?: string | null;
          currency?: string | null;
          id?: string;
          provider?: string | null;
          resource_id?: string | null;
          resource_type: string;
          tags?: Json | null;
          transaction_at?: string;
          user_id: string;
        };
        Update: {
          amount?: number;
          category?: string | null;
          currency?: string | null;
          id?: string;
          provider?: string | null;
          resource_id?: string | null;
          resource_type?: string;
          tags?: Json | null;
          transaction_at?: string;
          user_id?: string;
        };
        Relationships: [];
      };
      custom_roles: {
        Row: {
          created_at: string;
          description: string | null;
          id: string;
          name: string;
          permissions: Json | null;
          team_id: string | null;
        };
        Insert: {
          created_at?: string;
          description?: string | null;
          id?: string;
          name: string;
          permissions?: Json | null;
          team_id?: string | null;
        };
        Update: {
          created_at?: string;
          description?: string | null;
          id?: string;
          name?: string;
          permissions?: Json | null;
          team_id?: string | null;
        };
        Relationships: [
          {
            foreignKeyName: "custom_roles_team_id_fkey";
            columns: ["team_id"];
            isOneToOne: false;
            referencedRelation: "teams";
            referencedColumns: ["id"];
          },
        ];
      };
      custom_visualizations: {
        Row: {
          config: Json | null;
          created_at: string;
          dashboard_id: string | null;
          data_source: Json | null;
          id: string;
          name: string;
          position: Json | null;
          user_id: string;
          visualization_type: string;
        };
        Insert: {
          config?: Json | null;
          created_at?: string;
          dashboard_id?: string | null;
          data_source?: Json | null;
          id?: string;
          name: string;
          position?: Json | null;
          user_id: string;
          visualization_type: string;
        };
        Update: {
          config?: Json | null;
          created_at?: string;
          dashboard_id?: string | null;
          data_source?: Json | null;
          id?: string;
          name?: string;
          position?: Json | null;
          user_id?: string;
          visualization_type?: string;
        };
        Relationships: [
          {
            foreignKeyName: "custom_visualizations_dashboard_id_fkey";
            columns: ["dashboard_id"];
            isOneToOne: false;
            referencedRelation: "analytics_dashboards";
            referencedColumns: ["id"];
          },
        ];
      };
      device_registry: {
        Row: {
          capabilities: Json | null;
          device_name: string;
          device_token: string;
          device_type: string;
          id: string;
          is_active: boolean | null;
          last_seen_at: string | null;
          metadata: Json | null;
          registered_at: string | null;
          user_id: string;
        };
        Insert: {
          capabilities?: Json | null;
          device_name: string;
          device_token: string;
          device_type?: string;
          id?: string;
          is_active?: boolean | null;
          last_seen_at?: string | null;
          metadata?: Json | null;
          registered_at?: string | null;
          user_id: string;
        };
        Update: {
          capabilities?: Json | null;
          device_name?: string;
          device_token?: string;
          device_type?: string;
          id?: string;
          is_active?: boolean | null;
          last_seen_at?: string | null;
          metadata?: Json | null;
          registered_at?: string | null;
          user_id?: string;
        };
        Relationships: [];
      };
      distillation_jobs: {
        Row: {
          completed_at: string | null;
          config: Json | null;
          created_at: string;
          distillation_type: string;
          distilled_model_id: string | null;
          error_message: string | null;
          id: string;
          metrics: Json | null;
          priority: number;
          progress: number | null;
          stage: number;
          started_at: string | null;
          status: string;
          user_id: string;
        };
        Insert: {
          completed_at?: string | null;
          config?: Json | null;
          created_at?: string;
          distillation_type: string;
          distilled_model_id?: string | null;
          error_message?: string | null;
          id?: string;
          metrics?: Json | null;
          priority?: number;
          progress?: number | null;
          stage?: number;
          started_at?: string | null;
          status?: string;
          user_id: string;
        };
        Update: {
          completed_at?: string | null;
          config?: Json | null;
          created_at?: string;
          distillation_type?: string;
          distilled_model_id?: string | null;
          error_message?: string | null;
          id?: string;
          metrics?: Json | null;
          priority?: number;
          progress?: number | null;
          stage?: number;
          started_at?: string | null;
          status?: string;
          user_id?: string;
        };
        Relationships: [
          {
            foreignKeyName: "distillation_jobs_distilled_model_id_fkey";
            columns: ["distilled_model_id"];
            isOneToOne: false;
            referencedRelation: "distilled_models";
            referencedColumns: ["id"];
          },
        ];
      };
      distillation_metrics: {
        Row: {
          accuracy: number | null;
          alignment_score: number | null;
          distillation_job_id: string | null;
          epoch: number;
          id: string;
          loss: number | null;
          recorded_at: string;
          student_latency_ms: number | null;
          teacher_latency_ms: number | null;
        };
        Insert: {
          accuracy?: number | null;
          alignment_score?: number | null;
          distillation_job_id?: string | null;
          epoch: number;
          id?: string;
          loss?: number | null;
          recorded_at?: string;
          student_latency_ms?: number | null;
          teacher_latency_ms?: number | null;
        };
        Update: {
          accuracy?: number | null;
          alignment_score?: number | null;
          distillation_job_id?: string | null;
          epoch?: number;
          id?: string;
          loss?: number | null;
          recorded_at?: string;
          student_latency_ms?: number | null;
          teacher_latency_ms?: number | null;
        };
        Relationships: [
          {
            foreignKeyName: "distillation_metrics_distillation_job_id_fkey";
            columns: ["distillation_job_id"];
            isOneToOne: false;
            referencedRelation: "distillation_jobs";
            referencedColumns: ["id"];
          },
        ];
      };
      distilled_models: {
        Row: {
          accuracy: number | null;
          compression_ratio: number | null;
          created_at: string;
          current_stage: number;
          description: string | null;
          id: string;
          latency_ms: number | null;
          memory_mb: number | null;
          model_type: string;
          name: string;
          parameters: Json | null;
          specialization: string | null;
          status: string;
          teacher_model_id: string | null;
          updated_at: string;
          user_id: string;
        };
        Insert: {
          accuracy?: number | null;
          compression_ratio?: number | null;
          created_at?: string;
          current_stage?: number;
          description?: string | null;
          id?: string;
          latency_ms?: number | null;
          memory_mb?: number | null;
          model_type?: string;
          name: string;
          parameters?: Json | null;
          specialization?: string | null;
          status?: string;
          teacher_model_id?: string | null;
          updated_at?: string;
          user_id: string;
        };
        Update: {
          accuracy?: number | null;
          compression_ratio?: number | null;
          created_at?: string;
          current_stage?: number;
          description?: string | null;
          id?: string;
          latency_ms?: number | null;
          memory_mb?: number | null;
          model_type?: string;
          name?: string;
          parameters?: Json | null;
          specialization?: string | null;
          status?: string;
          teacher_model_id?: string | null;
          updated_at?: string;
          user_id?: string;
        };
        Relationships: [
          {
            foreignKeyName: "distilled_models_teacher_model_id_fkey";
            columns: ["teacher_model_id"];
            isOneToOne: false;
            referencedRelation: "models";
            referencedColumns: ["id"];
          },
        ];
      };
      distributed_training_jobs: {
        Row: {
          completed_at: string | null;
          config: Json | null;
          created_at: string;
          gradient_compression: boolean | null;
          id: string;
          mixed_precision: boolean | null;
          model_id: string | null;
          model_sharding: boolean | null;
          name: string;
          node_count: number | null;
          progress: number | null;
          speedup_vs_rtx5090: number | null;
          started_at: string | null;
          status: string | null;
          user_id: string;
        };
        Insert: {
          completed_at?: string | null;
          config?: Json | null;
          created_at?: string;
          gradient_compression?: boolean | null;
          id?: string;
          mixed_precision?: boolean | null;
          model_id?: string | null;
          model_sharding?: boolean | null;
          name: string;
          node_count?: number | null;
          progress?: number | null;
          speedup_vs_rtx5090?: number | null;
          started_at?: string | null;
          status?: string | null;
          user_id: string;
        };
        Update: {
          completed_at?: string | null;
          config?: Json | null;
          created_at?: string;
          gradient_compression?: boolean | null;
          id?: string;
          mixed_precision?: boolean | null;
          model_id?: string | null;
          model_sharding?: boolean | null;
          name?: string;
          node_count?: number | null;
          progress?: number | null;
          speedup_vs_rtx5090?: number | null;
          started_at?: string | null;
          status?: string | null;
          user_id?: string;
        };
        Relationships: [
          {
            foreignKeyName: "distributed_training_jobs_model_id_fkey";
            columns: ["model_id"];
            isOneToOne: false;
            referencedRelation: "models";
            referencedColumns: ["id"];
          },
        ];
      };
      enterprise_requests: {
        Row: {
          budget_range: string | null;
          company: string | null;
          created_at: string;
          email: string;
          expected_workload: string | null;
          id: string;
          message: string | null;
          name: string;
          role: string | null;
          status: string;
          user_id: string;
        };
        Insert: {
          budget_range?: string | null;
          company?: string | null;
          created_at?: string;
          email: string;
          expected_workload?: string | null;
          id?: string;
          message?: string | null;
          name: string;
          role?: string | null;
          status?: string;
          user_id: string;
        };
        Update: {
          budget_range?: string | null;
          company?: string | null;
          created_at?: string;
          email?: string;
          expected_workload?: string | null;
          id?: string;
          message?: string | null;
          name?: string;
          role?: string | null;
          status?: string;
          user_id?: string;
        };
        Relationships: [];
      };
      error_logs: {
        Row: {
          component_name: string | null;
          created_at: string;
          error_message: string;
          id: string;
          job_id: string | null;
          metadata: Json | null;
          module_name: string | null;
          severity: string;
          stack_trace: string | null;
          user_id: string | null;
        };
        Insert: {
          component_name?: string | null;
          created_at?: string;
          error_message: string;
          id?: string;
          job_id?: string | null;
          metadata?: Json | null;
          module_name?: string | null;
          severity?: string;
          stack_trace?: string | null;
          user_id?: string | null;
        };
        Update: {
          component_name?: string | null;
          created_at?: string;
          error_message?: string;
          id?: string;
          job_id?: string | null;
          metadata?: Json | null;
          module_name?: string | null;
          severity?: string;
          stack_trace?: string | null;
          user_id?: string | null;
        };
        Relationships: [];
      };
      execution_audit_log: {
        Row: {
          authority_required: boolean | null;
          authority_status: string | null;
          confidence: number;
          created_at: string;
          gpu_avoided: boolean | null;
          id: string;
          input_hash: string;
          latency_ms: number;
          outcome: string;
          outcome_reason: string;
          output_hash: string | null;
          path_reason: string;
          selected_path: string;
          surrogate_used: boolean | null;
          user_id: string | null;
          workload_id: string;
          workload_type: string;
        };
        Insert: {
          authority_required?: boolean | null;
          authority_status?: string | null;
          confidence: number;
          created_at?: string;
          gpu_avoided?: boolean | null;
          id?: string;
          input_hash: string;
          latency_ms: number;
          outcome: string;
          outcome_reason: string;
          output_hash?: string | null;
          path_reason: string;
          selected_path: string;
          surrogate_used?: boolean | null;
          user_id?: string | null;
          workload_id: string;
          workload_type: string;
        };
        Update: {
          authority_required?: boolean | null;
          authority_status?: string | null;
          confidence?: number;
          created_at?: string;
          gpu_avoided?: boolean | null;
          id?: string;
          input_hash?: string;
          latency_ms?: number;
          outcome?: string;
          outcome_reason?: string;
          output_hash?: string | null;
          path_reason?: string;
          selected_path?: string;
          surrogate_used?: boolean | null;
          user_id?: string | null;
          workload_id?: string;
          workload_type?: string;
        };
        Relationships: [];
      };
      expectation_locks: {
        Row: {
          created_at: string;
          id: string;
          lock_count: number | null;
          lock_message: string | null;
          lock_type: string;
          locked_at: string | null;
          unlocked_at: string | null;
          user_id: string;
        };
        Insert: {
          created_at?: string;
          id?: string;
          lock_count?: number | null;
          lock_message?: string | null;
          lock_type: string;
          locked_at?: string | null;
          unlocked_at?: string | null;
          user_id: string;
        };
        Update: {
          created_at?: string;
          id?: string;
          lock_count?: number | null;
          lock_message?: string | null;
          lock_type?: string;
          locked_at?: string | null;
          unlocked_at?: string | null;
          user_id?: string;
        };
        Relationships: [];
      };
      failover_events: {
        Row: {
          created_at: string;
          data_loss_bytes: number | null;
          duration_ms: number | null;
          from_region: string;
          id: string;
          success: boolean | null;
          to_region: string;
          trigger_reason: string;
          user_id: string;
        };
        Insert: {
          created_at?: string;
          data_loss_bytes?: number | null;
          duration_ms?: number | null;
          from_region: string;
          id?: string;
          success?: boolean | null;
          to_region: string;
          trigger_reason: string;
          user_id: string;
        };
        Update: {
          created_at?: string;
          data_loss_bytes?: number | null;
          duration_ms?: number | null;
          from_region?: string;
          id?: string;
          success?: boolean | null;
          to_region?: string;
          trigger_reason?: string;
          user_id?: string;
        };
        Relationships: [];
      };
      feature_flags: {
        Row: {
          applies_to_roles: Database["public"]["Enums"]["app_role"][] | null;
          created_at: string;
          description: string | null;
          flag_key: string;
          flag_value: boolean;
          id: string;
          updated_at: string;
        };
        Insert: {
          applies_to_roles?: Database["public"]["Enums"]["app_role"][] | null;
          created_at?: string;
          description?: string | null;
          flag_key: string;
          flag_value?: boolean;
          id?: string;
          updated_at?: string;
        };
        Update: {
          applies_to_roles?: Database["public"]["Enums"]["app_role"][] | null;
          created_at?: string;
          description?: string | null;
          flag_key?: string;
          flag_value?: boolean;
          id?: string;
          updated_at?: string;
        };
        Relationships: [];
      };
      fused_models: {
        Row: {
          accuracy: number | null;
          created_at: string;
          description: string | null;
          fusion_strategy: string;
          id: string;
          latency_ms: number | null;
          name: string;
          parameters: Json | null;
          source_model_ids: string[] | null;
          status: string;
          updated_at: string;
          user_id: string;
        };
        Insert: {
          accuracy?: number | null;
          created_at?: string;
          description?: string | null;
          fusion_strategy?: string;
          id?: string;
          latency_ms?: number | null;
          name: string;
          parameters?: Json | null;
          source_model_ids?: string[] | null;
          status?: string;
          updated_at?: string;
          user_id: string;
        };
        Update: {
          accuracy?: number | null;
          created_at?: string;
          description?: string | null;
          fusion_strategy?: string;
          id?: string;
          latency_ms?: number | null;
          name?: string;
          parameters?: Json | null;
          source_model_ids?: string[] | null;
          status?: string;
          updated_at?: string;
          user_id?: string;
        };
        Relationships: [];
      };
      fusion_performance_log: {
        Row: {
          accuracy_after: number | null;
          accuracy_before: number | null;
          fused_model_id: string | null;
          id: string;
          improvement_percent: number | null;
          latency_after_ms: number | null;
          latency_before_ms: number | null;
          recorded_at: string;
        };
        Insert: {
          accuracy_after?: number | null;
          accuracy_before?: number | null;
          fused_model_id?: string | null;
          id?: string;
          improvement_percent?: number | null;
          latency_after_ms?: number | null;
          latency_before_ms?: number | null;
          recorded_at?: string;
        };
        Update: {
          accuracy_after?: number | null;
          accuracy_before?: number | null;
          fused_model_id?: string | null;
          id?: string;
          improvement_percent?: number | null;
          latency_after_ms?: number | null;
          latency_before_ms?: number | null;
          recorded_at?: string;
        };
        Relationships: [
          {
            foreignKeyName: "fusion_performance_log_fused_model_id_fkey";
            columns: ["fused_model_id"];
            isOneToOne: false;
            referencedRelation: "fused_models";
            referencedColumns: ["id"];
          },
        ];
      };
      fusion_strategies: {
        Row: {
          config: Json | null;
          conflict_resolution: string | null;
          created_at: string;
          id: string;
          is_active: boolean | null;
          name: string;
          strategy_type: string;
          user_id: string;
          weight_distribution: Json | null;
        };
        Insert: {
          config?: Json | null;
          conflict_resolution?: string | null;
          created_at?: string;
          id?: string;
          is_active?: boolean | null;
          name: string;
          strategy_type: string;
          user_id: string;
          weight_distribution?: Json | null;
        };
        Update: {
          config?: Json | null;
          conflict_resolution?: string | null;
          created_at?: string;
          id?: string;
          is_active?: boolean | null;
          name?: string;
          strategy_type?: string;
          user_id?: string;
          weight_distribution?: Json | null;
        };
        Relationships: [];
      };
      gpu_jobs: {
        Row: {
          checkpoint_at: string | null;
          checkpoint_data: Json | null;
          completed_at: string | null;
          created_at: string;
          error_message: string | null;
          estimated_duration_sec: number | null;
          eta_seconds: number | null;
          id: string;
          job_name: string | null;
          job_tier: string | null;
          job_type: string;
          max_retries: number | null;
          memory_required_mb: number | null;
          payload: Json;
          priority: number;
          progress: number | null;
          result_data: Json | null;
          result_url: string | null;
          retry_count: number | null;
          started_at: string | null;
          status: string;
          thermal_paused: boolean | null;
          updated_at: string;
          user_id: string;
          worker_id: string | null;
          worker_signature: string | null;
        };
        Insert: {
          checkpoint_at?: string | null;
          checkpoint_data?: Json | null;
          completed_at?: string | null;
          created_at?: string;
          error_message?: string | null;
          estimated_duration_sec?: number | null;
          eta_seconds?: number | null;
          id?: string;
          job_name?: string | null;
          job_tier?: string | null;
          job_type: string;
          max_retries?: number | null;
          memory_required_mb?: number | null;
          payload?: Json;
          priority?: number;
          progress?: number | null;
          result_data?: Json | null;
          result_url?: string | null;
          retry_count?: number | null;
          started_at?: string | null;
          status?: string;
          thermal_paused?: boolean | null;
          updated_at?: string;
          user_id: string;
          worker_id?: string | null;
          worker_signature?: string | null;
        };
        Update: {
          checkpoint_at?: string | null;
          checkpoint_data?: Json | null;
          completed_at?: string | null;
          created_at?: string;
          error_message?: string | null;
          estimated_duration_sec?: number | null;
          eta_seconds?: number | null;
          id?: string;
          job_name?: string | null;
          job_tier?: string | null;
          job_type?: string;
          max_retries?: number | null;
          memory_required_mb?: number | null;
          payload?: Json;
          priority?: number;
          progress?: number | null;
          result_data?: Json | null;
          result_url?: string | null;
          retry_count?: number | null;
          started_at?: string | null;
          status?: string;
          thermal_paused?: boolean | null;
          updated_at?: string;
          user_id?: string;
          worker_id?: string | null;
          worker_signature?: string | null;
        };
        Relationships: [];
      };
      gpu_system_status: {
        Row: {
          active_job_id: string | null;
          cpu_temperature_celsius: number | null;
          cpu_utilization_percent: number | null;
          created_at: string;
          gpu_memory_total_mb: number | null;
          gpu_memory_used_mb: number | null;
          gpu_temperature_celsius: number | null;
          gpu_utilization_percent: number | null;
          id: string;
          is_online: boolean | null;
          is_thermal_throttled: boolean | null;
          jobs_completed_today: number | null;
          jobs_failed_today: number | null;
          last_heartbeat_at: string | null;
          updated_at: string;
          worker_id: string;
        };
        Insert: {
          active_job_id?: string | null;
          cpu_temperature_celsius?: number | null;
          cpu_utilization_percent?: number | null;
          created_at?: string;
          gpu_memory_total_mb?: number | null;
          gpu_memory_used_mb?: number | null;
          gpu_temperature_celsius?: number | null;
          gpu_utilization_percent?: number | null;
          id?: string;
          is_online?: boolean | null;
          is_thermal_throttled?: boolean | null;
          jobs_completed_today?: number | null;
          jobs_failed_today?: number | null;
          last_heartbeat_at?: string | null;
          updated_at?: string;
          worker_id: string;
        };
        Update: {
          active_job_id?: string | null;
          cpu_temperature_celsius?: number | null;
          cpu_utilization_percent?: number | null;
          created_at?: string;
          gpu_memory_total_mb?: number | null;
          gpu_memory_used_mb?: number | null;
          gpu_temperature_celsius?: number | null;
          gpu_utilization_percent?: number | null;
          id?: string;
          is_online?: boolean | null;
          is_thermal_throttled?: boolean | null;
          jobs_completed_today?: number | null;
          jobs_failed_today?: number | null;
          last_heartbeat_at?: string | null;
          updated_at?: string;
          worker_id?: string;
        };
        Relationships: [
          {
            foreignKeyName: "gpu_system_status_active_job_id_fkey";
            columns: ["active_job_id"];
            isOneToOne: false;
            referencedRelation: "gpu_jobs";
            referencedColumns: ["id"];
          },
        ];
      };
      graphics_benchmarks: {
        Row: {
          ai_enhancement_enabled: boolean | null;
          comparison_percent: number | null;
          created_at: string;
          id: string;
          name: string;
          resolution: string | null;
          rtx5090_fps: number | null;
          scene_complexity: string | null;
          settings: Json | null;
          user_id: string;
          your_engine_fps: number | null;
        };
        Insert: {
          ai_enhancement_enabled?: boolean | null;
          comparison_percent?: number | null;
          created_at?: string;
          id?: string;
          name: string;
          resolution?: string | null;
          rtx5090_fps?: number | null;
          scene_complexity?: string | null;
          settings?: Json | null;
          user_id: string;
          your_engine_fps?: number | null;
        };
        Update: {
          ai_enhancement_enabled?: boolean | null;
          comparison_percent?: number | null;
          created_at?: string;
          id?: string;
          name?: string;
          resolution?: string | null;
          rtx5090_fps?: number | null;
          scene_complexity?: string | null;
          settings?: Json | null;
          user_id?: string;
          your_engine_fps?: number | null;
        };
        Relationships: [];
      };
      immutable_audit_logs: {
        Row: {
          action: string;
          created_at: string;
          id: string;
          ip_address: string | null;
          new_value: Json | null;
          old_value: Json | null;
          resource_id: string | null;
          resource_type: string;
          user_agent: string | null;
          user_id: string | null;
        };
        Insert: {
          action: string;
          created_at?: string;
          id?: string;
          ip_address?: string | null;
          new_value?: Json | null;
          old_value?: Json | null;
          resource_id?: string | null;
          resource_type: string;
          user_agent?: string | null;
          user_id?: string | null;
        };
        Update: {
          action?: string;
          created_at?: string;
          id?: string;
          ip_address?: string | null;
          new_value?: Json | null;
          old_value?: Json | null;
          resource_id?: string | null;
          resource_type?: string;
          user_agent?: string | null;
          user_id?: string | null;
        };
        Relationships: [];
      };
      incident_log: {
        Row: {
          action_result: string | null;
          auto_action: string | null;
          created_at: string;
          id: string;
          incident_type: string;
          metadata: Json | null;
          reason: string;
          request_id: string | null;
          resolved: boolean | null;
          resolved_at: string | null;
          resolved_by: string | null;
          severity: string;
          user_id: string | null;
        };
        Insert: {
          action_result?: string | null;
          auto_action?: string | null;
          created_at?: string;
          id?: string;
          incident_type: string;
          metadata?: Json | null;
          reason: string;
          request_id?: string | null;
          resolved?: boolean | null;
          resolved_at?: string | null;
          resolved_by?: string | null;
          severity: string;
          user_id?: string | null;
        };
        Update: {
          action_result?: string | null;
          auto_action?: string | null;
          created_at?: string;
          id?: string;
          incident_type?: string;
          metadata?: Json | null;
          reason?: string;
          request_id?: string | null;
          resolved?: boolean | null;
          resolved_at?: string | null;
          resolved_by?: string | null;
          severity?: string;
          user_id?: string | null;
        };
        Relationships: [];
      };
      incidents: {
        Row: {
          affected_services: Json | null;
          created_at: string;
          description: string | null;
          id: string;
          resolution: string | null;
          resolved_at: string | null;
          root_cause: string | null;
          severity: string;
          started_at: string;
          status: string;
          title: string;
          user_id: string;
        };
        Insert: {
          affected_services?: Json | null;
          created_at?: string;
          description?: string | null;
          id?: string;
          resolution?: string | null;
          resolved_at?: string | null;
          root_cause?: string | null;
          severity?: string;
          started_at?: string;
          status?: string;
          title: string;
          user_id: string;
        };
        Update: {
          affected_services?: Json | null;
          created_at?: string;
          description?: string | null;
          id?: string;
          resolution?: string | null;
          resolved_at?: string | null;
          root_cause?: string | null;
          severity?: string;
          started_at?: string;
          status?: string;
          title?: string;
          user_id?: string;
        };
        Relationships: [];
      };
      inference_jobs: {
        Row: {
          completed_at: string | null;
          compression_ratio: number | null;
          created_at: string;
          enabled_modules: Json | null;
          error_message: string | null;
          id: string;
          input_data: Json;
          latency_ms: number | null;
          model_id: string;
          optimization_options: Json | null;
          output_data: Json | null;
          priority: number;
          progress: number | null;
          speedup: number | null;
          started_at: string | null;
          status: string;
          updated_at: string;
          user_id: string;
        };
        Insert: {
          completed_at?: string | null;
          compression_ratio?: number | null;
          created_at?: string;
          enabled_modules?: Json | null;
          error_message?: string | null;
          id?: string;
          input_data: Json;
          latency_ms?: number | null;
          model_id: string;
          optimization_options?: Json | null;
          output_data?: Json | null;
          priority?: number;
          progress?: number | null;
          speedup?: number | null;
          started_at?: string | null;
          status?: string;
          updated_at?: string;
          user_id: string;
        };
        Update: {
          completed_at?: string | null;
          compression_ratio?: number | null;
          created_at?: string;
          enabled_modules?: Json | null;
          error_message?: string | null;
          id?: string;
          input_data?: Json;
          latency_ms?: number | null;
          model_id?: string;
          optimization_options?: Json | null;
          output_data?: Json | null;
          priority?: number;
          progress?: number | null;
          speedup?: number | null;
          started_at?: string | null;
          status?: string;
          updated_at?: string;
          user_id?: string;
        };
        Relationships: [
          {
            foreignKeyName: "inference_jobs_model_id_fkey";
            columns: ["model_id"];
            isOneToOne: false;
            referencedRelation: "models";
            referencedColumns: ["id"];
          },
        ];
      };
      integrations: {
        Row: {
          config: Json | null;
          created_at: string;
          credentials_configured: boolean | null;
          id: string;
          integration_type: string;
          is_active: boolean | null;
          last_sync_at: string | null;
          name: string;
          plugin_id: string | null;
          user_id: string;
        };
        Insert: {
          config?: Json | null;
          created_at?: string;
          credentials_configured?: boolean | null;
          id?: string;
          integration_type: string;
          is_active?: boolean | null;
          last_sync_at?: string | null;
          name: string;
          plugin_id?: string | null;
          user_id: string;
        };
        Update: {
          config?: Json | null;
          created_at?: string;
          credentials_configured?: boolean | null;
          id?: string;
          integration_type?: string;
          is_active?: boolean | null;
          last_sync_at?: string | null;
          name?: string;
          plugin_id?: string | null;
          user_id?: string;
        };
        Relationships: [
          {
            foreignKeyName: "integrations_plugin_id_fkey";
            columns: ["plugin_id"];
            isOneToOne: false;
            referencedRelation: "plugins";
            referencedColumns: ["id"];
          },
        ];
      };
      job_final_states: {
        Row: {
          checkpoint_available: boolean | null;
          confidence_score: number | null;
          created_at: string;
          final_state: string;
          id: string;
          is_approximate: boolean | null;
          job_id: string;
          processing_method: string | null;
          resolved_at: string | null;
          user_id: string;
        };
        Insert: {
          checkpoint_available?: boolean | null;
          confidence_score?: number | null;
          created_at?: string;
          final_state: string;
          id?: string;
          is_approximate?: boolean | null;
          job_id: string;
          processing_method?: string | null;
          resolved_at?: string | null;
          user_id: string;
        };
        Update: {
          checkpoint_available?: boolean | null;
          confidence_score?: number | null;
          created_at?: string;
          final_state?: string;
          id?: string;
          is_approximate?: boolean | null;
          job_id?: string;
          processing_method?: string | null;
          resolved_at?: string | null;
          user_id?: string;
        };
        Relationships: [];
      };
      job_logs: {
        Row: {
          id: string;
          job_id: string;
          level: string;
          message: string;
          metadata: Json | null;
          ts: string;
        };
        Insert: {
          id?: string;
          job_id: string;
          level?: string;
          message: string;
          metadata?: Json | null;
          ts?: string;
        };
        Update: {
          id?: string;
          job_id?: string;
          level?: string;
          message?: string;
          metadata?: Json | null;
          ts?: string;
        };
        Relationships: [
          {
            foreignKeyName: "job_logs_job_id_fkey";
            columns: ["job_id"];
            isOneToOne: false;
            referencedRelation: "gpu_jobs";
            referencedColumns: ["id"];
          },
        ];
      };
      job_queue: {
        Row: {
          enqueued_at: string;
          id: string;
          job_id: string;
          priority: number;
        };
        Insert: {
          enqueued_at?: string;
          id?: string;
          job_id: string;
          priority?: number;
        };
        Update: {
          enqueued_at?: string;
          id?: string;
          job_id?: string;
          priority?: number;
        };
        Relationships: [
          {
            foreignKeyName: "job_queue_job_id_fkey";
            columns: ["job_id"];
            isOneToOne: true;
            referencedRelation: "gpu_jobs";
            referencedColumns: ["id"];
          },
        ];
      };
      job_results: {
        Row: {
          artifacts_json: Json | null;
          created_at: string;
          id: string;
          job_id: string;
          log: string | null;
        };
        Insert: {
          artifacts_json?: Json | null;
          created_at?: string;
          id?: string;
          job_id: string;
          log?: string | null;
        };
        Update: {
          artifacts_json?: Json | null;
          created_at?: string;
          id?: string;
          job_id?: string;
          log?: string | null;
        };
        Relationships: [
          {
            foreignKeyName: "job_results_job_id_fkey";
            columns: ["job_id"];
            isOneToOne: true;
            referencedRelation: "gpu_jobs";
            referencedColumns: ["id"];
          },
        ];
      };
      jobs: {
        Row: {
          completed_at: string | null;
          created_at: string;
          error_message: string | null;
          id: string;
          input_data: Json | null;
          job_type: string;
          output_data: Json | null;
          priority: string;
          progress: number | null;
          started_at: string | null;
          status: string;
          user_id: string;
        };
        Insert: {
          completed_at?: string | null;
          created_at?: string;
          error_message?: string | null;
          id?: string;
          input_data?: Json | null;
          job_type: string;
          output_data?: Json | null;
          priority?: string;
          progress?: number | null;
          started_at?: string | null;
          status?: string;
          user_id: string;
        };
        Update: {
          completed_at?: string | null;
          created_at?: string;
          error_message?: string | null;
          id?: string;
          input_data?: Json | null;
          job_type?: string;
          output_data?: Json | null;
          priority?: string;
          progress?: number | null;
          started_at?: string | null;
          status?: string;
          user_id?: string;
        };
        Relationships: [];
      };
      knowledge_transfer_logs: {
        Row: {
          alignment_after: number | null;
          alignment_before: number | null;
          created_at: string;
          distillation_job_id: string | null;
          id: string;
          layer_name: string;
          loss_reduction: number | null;
          transfer_type: string;
        };
        Insert: {
          alignment_after?: number | null;
          alignment_before?: number | null;
          created_at?: string;
          distillation_job_id?: string | null;
          id?: string;
          layer_name: string;
          loss_reduction?: number | null;
          transfer_type: string;
        };
        Update: {
          alignment_after?: number | null;
          alignment_before?: number | null;
          created_at?: string;
          distillation_job_id?: string | null;
          id?: string;
          layer_name?: string;
          loss_reduction?: number | null;
          transfer_type?: string;
        };
        Relationships: [
          {
            foreignKeyName: "knowledge_transfer_logs_distillation_job_id_fkey";
            columns: ["distillation_job_id"];
            isOneToOne: false;
            referencedRelation: "distillation_jobs";
            referencedColumns: ["id"];
          },
        ];
      };
      marketplace_transactions: {
        Row: {
          amount: number;
          created_at: string;
          currency: string | null;
          id: string;
          plugin_id: string | null;
          status: string | null;
          transaction_type: string;
          user_id: string;
        };
        Insert: {
          amount: number;
          created_at?: string;
          currency?: string | null;
          id?: string;
          plugin_id?: string | null;
          status?: string | null;
          transaction_type: string;
          user_id: string;
        };
        Update: {
          amount?: number;
          created_at?: string;
          currency?: string | null;
          id?: string;
          plugin_id?: string | null;
          status?: string | null;
          transaction_type?: string;
          user_id?: string;
        };
        Relationships: [
          {
            foreignKeyName: "marketplace_transactions_plugin_id_fkey";
            columns: ["plugin_id"];
            isOneToOne: false;
            referencedRelation: "plugins";
            referencedColumns: ["id"];
          },
        ];
      };
      metrics_aggregated: {
        Row: {
          aggregation_type: string;
          created_at: string;
          id: string;
          metric_name: string;
          period_end: string;
          period_start: string;
          sample_count: number | null;
          user_id: string;
          value_avg: number | null;
          value_max: number | null;
          value_min: number | null;
          value_sum: number | null;
        };
        Insert: {
          aggregation_type?: string;
          created_at?: string;
          id?: string;
          metric_name: string;
          period_end: string;
          period_start: string;
          sample_count?: number | null;
          user_id: string;
          value_avg?: number | null;
          value_max?: number | null;
          value_min?: number | null;
          value_sum?: number | null;
        };
        Update: {
          aggregation_type?: string;
          created_at?: string;
          id?: string;
          metric_name?: string;
          period_end?: string;
          period_start?: string;
          sample_count?: number | null;
          user_id?: string;
          value_avg?: number | null;
          value_max?: number | null;
          value_min?: number | null;
          value_sum?: number | null;
        };
        Relationships: [];
      };
      metrics_raw: {
        Row: {
          id: string;
          metric_name: string;
          metric_value: number;
          recorded_at: string;
          source: string | null;
          tags: Json | null;
          user_id: string;
        };
        Insert: {
          id?: string;
          metric_name: string;
          metric_value: number;
          recorded_at?: string;
          source?: string | null;
          tags?: Json | null;
          user_id: string;
        };
        Update: {
          id?: string;
          metric_name?: string;
          metric_value?: number;
          recorded_at?: string;
          source?: string | null;
          tags?: Json | null;
          user_id?: string;
        };
        Relationships: [];
      };
      models: {
        Row: {
          created_at: string;
          description: string | null;
          file_path: string | null;
          id: string;
          is_public: boolean | null;
          model_type: string;
          name: string;
          parameters: Json | null;
          size_mb: number | null;
          status: string;
          storage_path: string | null;
          updated_at: string;
          user_id: string;
          version: string;
        };
        Insert: {
          created_at?: string;
          description?: string | null;
          file_path?: string | null;
          id?: string;
          is_public?: boolean | null;
          model_type: string;
          name: string;
          parameters?: Json | null;
          size_mb?: number | null;
          status?: string;
          storage_path?: string | null;
          updated_at?: string;
          user_id: string;
          version: string;
        };
        Update: {
          created_at?: string;
          description?: string | null;
          file_path?: string | null;
          id?: string;
          is_public?: boolean | null;
          model_type?: string;
          name?: string;
          parameters?: Json | null;
          size_mb?: number | null;
          status?: string;
          storage_path?: string | null;
          updated_at?: string;
          user_id?: string;
          version?: string;
        };
        Relationships: [];
      };
      module_configs: {
        Row: {
          compression_ratio_achieved: number | null;
          config: Json;
          created_at: string;
          enabled: boolean;
          id: string;
          module_name: string;
          module_type: string;
          settings: Json | null;
          speedup_achieved: number | null;
          updated_at: string;
          user_id: string;
        };
        Insert: {
          compression_ratio_achieved?: number | null;
          config?: Json;
          created_at?: string;
          enabled?: boolean;
          id?: string;
          module_name: string;
          module_type: string;
          settings?: Json | null;
          speedup_achieved?: number | null;
          updated_at?: string;
          user_id: string;
        };
        Update: {
          compression_ratio_achieved?: number | null;
          config?: Json;
          created_at?: string;
          enabled?: boolean;
          id?: string;
          module_name?: string;
          module_type?: string;
          settings?: Json | null;
          speedup_achieved?: number | null;
          updated_at?: string;
          user_id?: string;
        };
        Relationships: [];
      };
      module_locks: {
        Row: {
          expires_at: string;
          id: string;
          locked_at: string;
          locked_by: string;
          module_name: string;
          session_id: string;
        };
        Insert: {
          expires_at?: string;
          id?: string;
          locked_at?: string;
          locked_by: string;
          module_name: string;
          session_id: string;
        };
        Update: {
          expires_at?: string;
          id?: string;
          locked_at?: string;
          locked_by?: string;
          module_name?: string;
          session_id?: string;
        };
        Relationships: [
          {
            foreignKeyName: "module_locks_session_id_fkey";
            columns: ["session_id"];
            isOneToOne: false;
            referencedRelation: "collaboration_sessions";
            referencedColumns: ["id"];
          },
        ];
      };
      module_status: {
        Row: {
          config: Json | null;
          current_job_id: string | null;
          error_count: number | null;
          error_message: string | null;
          health_score: number | null;
          id: string;
          last_checked: string | null;
          metadata: Json | null;
          module_name: string;
          status: string;
          success_count: number | null;
          updated_at: string;
          user_id: string;
          version: string | null;
        };
        Insert: {
          config?: Json | null;
          current_job_id?: string | null;
          error_count?: number | null;
          error_message?: string | null;
          health_score?: number | null;
          id?: string;
          last_checked?: string | null;
          metadata?: Json | null;
          module_name: string;
          status?: string;
          success_count?: number | null;
          updated_at?: string;
          user_id: string;
          version?: string | null;
        };
        Update: {
          config?: Json | null;
          current_job_id?: string | null;
          error_count?: number | null;
          error_message?: string | null;
          health_score?: number | null;
          id?: string;
          last_checked?: string | null;
          metadata?: Json | null;
          module_name?: string;
          status?: string;
          success_count?: number | null;
          updated_at?: string;
          user_id?: string;
          version?: string | null;
        };
        Relationships: [
          {
            foreignKeyName: "module_status_current_job_id_fkey";
            columns: ["current_job_id"];
            isOneToOne: false;
            referencedRelation: "inference_jobs";
            referencedColumns: ["id"];
          },
        ];
      };
      offline_packages: {
        Row: {
          compression_level: string | null;
          created_at: string;
          description: string | null;
          download_url: string | null;
          estimated_latency_ms: number | null;
          expires_at: string | null;
          id: string;
          models: Json | null;
          name: string;
          status: string | null;
          total_size_mb: number | null;
          user_id: string;
        };
        Insert: {
          compression_level?: string | null;
          created_at?: string;
          description?: string | null;
          download_url?: string | null;
          estimated_latency_ms?: number | null;
          expires_at?: string | null;
          id?: string;
          models?: Json | null;
          name: string;
          status?: string | null;
          total_size_mb?: number | null;
          user_id: string;
        };
        Update: {
          compression_level?: string | null;
          created_at?: string;
          description?: string | null;
          download_url?: string | null;
          estimated_latency_ms?: number | null;
          expires_at?: string | null;
          id?: string;
          models?: Json | null;
          name?: string;
          status?: string | null;
          total_size_mb?: number | null;
          user_id?: string;
        };
        Relationships: [];
      };
      owner_diagnostics: {
        Row: {
          approximate_percent: number | null;
          compression_ratio: number | null;
          created_at: string;
          deferred_percent: number | null;
          diagnostic_date: string;
          exact_percent: number | null;
          id: string;
          instant_percent: number | null;
          notes: string | null;
          total_requests: number | null;
        };
        Insert: {
          approximate_percent?: number | null;
          compression_ratio?: number | null;
          created_at?: string;
          deferred_percent?: number | null;
          diagnostic_date?: string;
          exact_percent?: number | null;
          id?: string;
          instant_percent?: number | null;
          notes?: string | null;
          total_requests?: number | null;
        };
        Update: {
          approximate_percent?: number | null;
          compression_ratio?: number | null;
          created_at?: string;
          deferred_percent?: number | null;
          diagnostic_date?: string;
          exact_percent?: number | null;
          id?: string;
          instant_percent?: number | null;
          notes?: string | null;
          total_requests?: number | null;
        };
        Relationships: [];
      };
      payment_webhook_events: {
        Row: {
          created_at: string;
          error_message: string | null;
          event_id: string;
          event_type: string;
          id: string;
          payload: Json;
          processed: boolean | null;
          processed_at: string | null;
          provider: string;
          signature_verified: boolean | null;
        };
        Insert: {
          created_at?: string;
          error_message?: string | null;
          event_id: string;
          event_type: string;
          id?: string;
          payload: Json;
          processed?: boolean | null;
          processed_at?: string | null;
          provider: string;
          signature_verified?: boolean | null;
        };
        Update: {
          created_at?: string;
          error_message?: string | null;
          event_id?: string;
          event_type?: string;
          id?: string;
          payload?: Json;
          processed?: boolean | null;
          processed_at?: string | null;
          provider?: string;
          signature_verified?: boolean | null;
        };
        Relationships: [];
      };
      payments: {
        Row: {
          amount: number;
          billing_cycle: string | null;
          created_at: string;
          currency: string;
          id: string;
          metadata: Json | null;
          plan: string;
          provider: string;
          provider_customer_id: string | null;
          provider_payment_id: string | null;
          status: string;
          transaction_id: string | null;
          updated_at: string;
          user_id: string;
          webhook_received_at: string | null;
        };
        Insert: {
          amount: number;
          billing_cycle?: string | null;
          created_at?: string;
          currency?: string;
          id?: string;
          metadata?: Json | null;
          plan: string;
          provider: string;
          provider_customer_id?: string | null;
          provider_payment_id?: string | null;
          status?: string;
          transaction_id?: string | null;
          updated_at?: string;
          user_id: string;
          webhook_received_at?: string | null;
        };
        Update: {
          amount?: number;
          billing_cycle?: string | null;
          created_at?: string;
          currency?: string;
          id?: string;
          metadata?: Json | null;
          plan?: string;
          provider?: string;
          provider_customer_id?: string | null;
          provider_payment_id?: string | null;
          status?: string;
          transaction_id?: string | null;
          updated_at?: string;
          user_id?: string;
          webhook_received_at?: string | null;
        };
        Relationships: [];
      };
      performance_metrics: {
        Row: {
          cache_hit_ratio: number | null;
          cpu_usage_percent: number | null;
          id: string;
          job_id: string | null;
          latency_ms: number | null;
          memory_mb: number | null;
          metadata: Json | null;
          metric_name: string;
          metric_value: number;
          model_id: string | null;
          module_name: string | null;
          recorded_at: string;
          throughput_rps: number | null;
          user_id: string;
        };
        Insert: {
          cache_hit_ratio?: number | null;
          cpu_usage_percent?: number | null;
          id?: string;
          job_id?: string | null;
          latency_ms?: number | null;
          memory_mb?: number | null;
          metadata?: Json | null;
          metric_name: string;
          metric_value: number;
          model_id?: string | null;
          module_name?: string | null;
          recorded_at?: string;
          throughput_rps?: number | null;
          user_id: string;
        };
        Update: {
          cache_hit_ratio?: number | null;
          cpu_usage_percent?: number | null;
          id?: string;
          job_id?: string | null;
          latency_ms?: number | null;
          memory_mb?: number | null;
          metadata?: Json | null;
          metric_name?: string;
          metric_value?: number;
          model_id?: string | null;
          module_name?: string | null;
          recorded_at?: string;
          throughput_rps?: number | null;
          user_id?: string;
        };
        Relationships: [
          {
            foreignKeyName: "performance_metrics_job_id_fkey";
            columns: ["job_id"];
            isOneToOne: false;
            referencedRelation: "inference_jobs";
            referencedColumns: ["id"];
          },
          {
            foreignKeyName: "performance_metrics_model_id_fkey";
            columns: ["model_id"];
            isOneToOne: false;
            referencedRelation: "models";
            referencedColumns: ["id"];
          },
        ];
      };
      permissions: {
        Row: {
          action: string;
          conditions: Json | null;
          created_at: string;
          id: string;
          resource: string;
          role_id: string | null;
        };
        Insert: {
          action: string;
          conditions?: Json | null;
          created_at?: string;
          id?: string;
          resource: string;
          role_id?: string | null;
        };
        Update: {
          action?: string;
          conditions?: Json | null;
          created_at?: string;
          id?: string;
          resource?: string;
          role_id?: string | null;
        };
        Relationships: [
          {
            foreignKeyName: "permissions_role_id_fkey";
            columns: ["role_id"];
            isOneToOne: false;
            referencedRelation: "custom_roles";
            referencedColumns: ["id"];
          },
        ];
      };
      persistent_compute_jobs: {
        Row: {
          checkpoint_interval_min: number | null;
          completed_at: string | null;
          created_at: string;
          current_checkpoint: Json | null;
          failure_tolerance: string | null;
          id: string;
          job_type: string;
          last_checkpoint_at: string | null;
          max_duration_hours: number | null;
          name: string;
          recovery_count: number | null;
          started_at: string | null;
          status: string | null;
          user_id: string;
        };
        Insert: {
          checkpoint_interval_min?: number | null;
          completed_at?: string | null;
          created_at?: string;
          current_checkpoint?: Json | null;
          failure_tolerance?: string | null;
          id?: string;
          job_type: string;
          last_checkpoint_at?: string | null;
          max_duration_hours?: number | null;
          name: string;
          recovery_count?: number | null;
          started_at?: string | null;
          status?: string | null;
          user_id: string;
        };
        Update: {
          checkpoint_interval_min?: number | null;
          completed_at?: string | null;
          created_at?: string;
          current_checkpoint?: Json | null;
          failure_tolerance?: string | null;
          id?: string;
          job_type?: string;
          last_checkpoint_at?: string | null;
          max_duration_hours?: number | null;
          name?: string;
          recovery_count?: number | null;
          started_at?: string | null;
          status?: string | null;
          user_id?: string;
        };
        Relationships: [];
      };
      personalization_settings: {
        Row: {
          dashboard_config: Json | null;
          feature_flags: Json | null;
          id: string;
          layout_preference: string | null;
          notification_preferences: Json | null;
          theme_preference: string | null;
          updated_at: string;
          user_id: string;
        };
        Insert: {
          dashboard_config?: Json | null;
          feature_flags?: Json | null;
          id?: string;
          layout_preference?: string | null;
          notification_preferences?: Json | null;
          theme_preference?: string | null;
          updated_at?: string;
          user_id: string;
        };
        Update: {
          dashboard_config?: Json | null;
          feature_flags?: Json | null;
          id?: string;
          layout_preference?: string | null;
          notification_preferences?: Json | null;
          theme_preference?: string | null;
          updated_at?: string;
          user_id?: string;
        };
        Relationships: [];
      };
      plugins: {
        Row: {
          author_id: string;
          category: string | null;
          config_schema: Json | null;
          created_at: string;
          description: string | null;
          download_count: number | null;
          icon_url: string | null;
          id: string;
          is_published: boolean | null;
          name: string;
          price: number | null;
          rating: number | null;
          updated_at: string;
          version: string;
        };
        Insert: {
          author_id: string;
          category?: string | null;
          config_schema?: Json | null;
          created_at?: string;
          description?: string | null;
          download_count?: number | null;
          icon_url?: string | null;
          id?: string;
          is_published?: boolean | null;
          name: string;
          price?: number | null;
          rating?: number | null;
          updated_at?: string;
          version?: string;
        };
        Update: {
          author_id?: string;
          category?: string | null;
          config_schema?: Json | null;
          created_at?: string;
          description?: string | null;
          download_count?: number | null;
          icon_url?: string | null;
          id?: string;
          is_published?: boolean | null;
          name?: string;
          price?: number | null;
          rating?: number | null;
          updated_at?: string;
          version?: string;
        };
        Relationships: [];
      };
      policy_violations: {
        Row: {
          created_at: string;
          details: Json | null;
          id: string;
          resolved: boolean;
          resolved_at: string | null;
          resource_id: string | null;
          resource_type: string | null;
          severity: string;
          user_id: string | null;
          violation_type: string;
        };
        Insert: {
          created_at?: string;
          details?: Json | null;
          id?: string;
          resolved?: boolean;
          resolved_at?: string | null;
          resource_id?: string | null;
          resource_type?: string | null;
          severity: string;
          user_id?: string | null;
          violation_type: string;
        };
        Update: {
          created_at?: string;
          details?: Json | null;
          id?: string;
          resolved?: boolean;
          resolved_at?: string | null;
          resource_id?: string | null;
          resource_type?: string | null;
          severity?: string;
          user_id?: string | null;
          violation_type?: string;
        };
        Relationships: [];
      };
      prediction_accuracy: {
        Row: {
          accuracy_percent: number | null;
          id: string;
          mape: number | null;
          prediction_type: string;
          recorded_at: string;
          rmse: number | null;
          sample_count: number | null;
          time_horizon: string;
          user_id: string;
        };
        Insert: {
          accuracy_percent?: number | null;
          id?: string;
          mape?: number | null;
          prediction_type: string;
          recorded_at?: string;
          rmse?: number | null;
          sample_count?: number | null;
          time_horizon: string;
          user_id: string;
        };
        Update: {
          accuracy_percent?: number | null;
          id?: string;
          mape?: number | null;
          prediction_type?: string;
          recorded_at?: string;
          rmse?: number | null;
          sample_count?: number | null;
          time_horizon?: string;
          user_id?: string;
        };
        Relationships: [];
      };
      profiles: {
        Row: {
          avatar_url: string | null;
          company: string | null;
          created_at: string;
          full_name: string | null;
          id: string;
          updated_at: string;
          user_id: string;
        };
        Insert: {
          avatar_url?: string | null;
          company?: string | null;
          created_at?: string;
          full_name?: string | null;
          id?: string;
          updated_at?: string;
          user_id: string;
        };
        Update: {
          avatar_url?: string | null;
          company?: string | null;
          created_at?: string;
          full_name?: string | null;
          id?: string;
          updated_at?: string;
          user_id?: string;
        };
        Relationships: [];
      };
      quantum_benchmarks: {
        Row: {
          circuit_id: string | null;
          classical_time_ms: number | null;
          created_at: string;
          id: string;
          quantum_time_ms: number | null;
          resource_usage: Json | null;
          speedup_factor: number | null;
          user_id: string;
        };
        Insert: {
          circuit_id?: string | null;
          classical_time_ms?: number | null;
          created_at?: string;
          id?: string;
          quantum_time_ms?: number | null;
          resource_usage?: Json | null;
          speedup_factor?: number | null;
          user_id: string;
        };
        Update: {
          circuit_id?: string | null;
          classical_time_ms?: number | null;
          created_at?: string;
          id?: string;
          quantum_time_ms?: number | null;
          resource_usage?: Json | null;
          speedup_factor?: number | null;
          user_id?: string;
        };
        Relationships: [
          {
            foreignKeyName: "quantum_benchmarks_circuit_id_fkey";
            columns: ["circuit_id"];
            isOneToOne: false;
            referencedRelation: "quantum_circuits";
            referencedColumns: ["id"];
          },
        ];
      };
      quantum_circuits: {
        Row: {
          algorithm_type: string;
          circuit_data: Json;
          created_at: string;
          description: string | null;
          gate_count: number | null;
          id: string;
          name: string;
          qubit_count: number;
          updated_at: string;
          user_id: string;
        };
        Insert: {
          algorithm_type?: string;
          circuit_data?: Json;
          created_at?: string;
          description?: string | null;
          gate_count?: number | null;
          id?: string;
          name: string;
          qubit_count?: number;
          updated_at?: string;
          user_id: string;
        };
        Update: {
          algorithm_type?: string;
          circuit_data?: Json;
          created_at?: string;
          description?: string | null;
          gate_count?: number | null;
          id?: string;
          name?: string;
          qubit_count?: number;
          updated_at?: string;
          user_id?: string;
        };
        Relationships: [];
      };
      quantum_jobs: {
        Row: {
          backend_type: string | null;
          circuit_id: string | null;
          completed_at: string | null;
          created_at: string;
          error_message: string | null;
          id: string;
          priority: number;
          shots: number | null;
          started_at: string | null;
          status: string;
          user_id: string;
        };
        Insert: {
          backend_type?: string | null;
          circuit_id?: string | null;
          completed_at?: string | null;
          created_at?: string;
          error_message?: string | null;
          id?: string;
          priority?: number;
          shots?: number | null;
          started_at?: string | null;
          status?: string;
          user_id: string;
        };
        Update: {
          backend_type?: string | null;
          circuit_id?: string | null;
          completed_at?: string | null;
          created_at?: string;
          error_message?: string | null;
          id?: string;
          priority?: number;
          shots?: number | null;
          started_at?: string | null;
          status?: string;
          user_id?: string;
        };
        Relationships: [
          {
            foreignKeyName: "quantum_jobs_circuit_id_fkey";
            columns: ["circuit_id"];
            isOneToOne: false;
            referencedRelation: "quantum_circuits";
            referencedColumns: ["id"];
          },
        ];
      };
      quantum_results: {
        Row: {
          created_at: string;
          execution_time_ms: number | null;
          fidelity: number | null;
          id: string;
          job_id: string | null;
          measurement_counts: Json | null;
          probabilities: Json | null;
        };
        Insert: {
          created_at?: string;
          execution_time_ms?: number | null;
          fidelity?: number | null;
          id?: string;
          job_id?: string | null;
          measurement_counts?: Json | null;
          probabilities?: Json | null;
        };
        Update: {
          created_at?: string;
          execution_time_ms?: number | null;
          fidelity?: number | null;
          id?: string;
          job_id?: string | null;
          measurement_counts?: Json | null;
          probabilities?: Json | null;
        };
        Relationships: [
          {
            foreignKeyName: "quantum_results_job_id_fkey";
            columns: ["job_id"];
            isOneToOne: false;
            referencedRelation: "quantum_jobs";
            referencedColumns: ["id"];
          },
        ];
      };
      rate_limit_events: {
        Row: {
          action_count: number;
          action_type: string;
          blocked: boolean;
          created_at: string;
          id: string;
          user_id: string | null;
          window_start: string;
        };
        Insert: {
          action_count?: number;
          action_type: string;
          blocked?: boolean;
          created_at?: string;
          id?: string;
          user_id?: string | null;
          window_start?: string;
        };
        Update: {
          action_count?: number;
          action_type?: string;
          blocked?: boolean;
          created_at?: string;
          id?: string;
          user_id?: string | null;
          window_start?: string;
        };
        Relationships: [];
      };
      recommendations: {
        Row: {
          action_url: string | null;
          created_at: string;
          description: string | null;
          dismissed_at: string | null;
          expires_at: string | null;
          id: string;
          is_dismissed: boolean | null;
          priority: number | null;
          recommendation_type: string;
          score: number | null;
          title: string;
          user_id: string;
        };
        Insert: {
          action_url?: string | null;
          created_at?: string;
          description?: string | null;
          dismissed_at?: string | null;
          expires_at?: string | null;
          id?: string;
          is_dismissed?: boolean | null;
          priority?: number | null;
          recommendation_type: string;
          score?: number | null;
          title: string;
          user_id: string;
        };
        Update: {
          action_url?: string | null;
          created_at?: string;
          description?: string | null;
          dismissed_at?: string | null;
          expires_at?: string | null;
          id?: string;
          is_dismissed?: boolean | null;
          priority?: number | null;
          recommendation_type?: string;
          score?: number | null;
          title?: string;
          user_id?: string;
        };
        Relationships: [];
      };
      releases: {
        Row: {
          created_at: string;
          deployed_at: string | null;
          feature_flags: Json | null;
          health_check_passed: boolean | null;
          health_metrics: Json | null;
          id: string;
          previous_version: string | null;
          rollback_reason: string | null;
          rolled_back_at: string | null;
          rollout_percentage: number | null;
          schema_changes: Json | null;
          status: string;
          updated_at: string;
          version: string;
        };
        Insert: {
          created_at?: string;
          deployed_at?: string | null;
          feature_flags?: Json | null;
          health_check_passed?: boolean | null;
          health_metrics?: Json | null;
          id?: string;
          previous_version?: string | null;
          rollback_reason?: string | null;
          rolled_back_at?: string | null;
          rollout_percentage?: number | null;
          schema_changes?: Json | null;
          status?: string;
          updated_at?: string;
          version: string;
        };
        Update: {
          created_at?: string;
          deployed_at?: string | null;
          feature_flags?: Json | null;
          health_check_passed?: boolean | null;
          health_metrics?: Json | null;
          id?: string;
          previous_version?: string | null;
          rollback_reason?: string | null;
          rolled_back_at?: string | null;
          rollout_percentage?: number | null;
          schema_changes?: Json | null;
          status?: string;
          updated_at?: string;
          version?: string;
        };
        Relationships: [];
      };
      scaling_actions: {
        Row: {
          action_type: string;
          cost_impact: number | null;
          created_at: string;
          executed_at: string | null;
          id: string;
          latency_impact: number | null;
          new_count: number | null;
          previous_count: number | null;
          resource_type: string;
          status: string;
          trigger_reason: string | null;
          user_id: string;
        };
        Insert: {
          action_type: string;
          cost_impact?: number | null;
          created_at?: string;
          executed_at?: string | null;
          id?: string;
          latency_impact?: number | null;
          new_count?: number | null;
          previous_count?: number | null;
          resource_type: string;
          status?: string;
          trigger_reason?: string | null;
          user_id: string;
        };
        Update: {
          action_type?: string;
          cost_impact?: number | null;
          created_at?: string;
          executed_at?: string | null;
          id?: string;
          latency_impact?: number | null;
          new_count?: number | null;
          previous_count?: number | null;
          resource_type?: string;
          status?: string;
          trigger_reason?: string | null;
          user_id?: string;
        };
        Relationships: [];
      };
      security_audit_log: {
        Row: {
          action: string;
          created_at: string;
          id: string;
          ip_address: string | null;
          metadata: Json | null;
          reason: string | null;
          resource_id: string | null;
          resource_type: string;
          result: string;
          user_id: string | null;
        };
        Insert: {
          action: string;
          created_at?: string;
          id?: string;
          ip_address?: string | null;
          metadata?: Json | null;
          reason?: string | null;
          resource_id?: string | null;
          resource_type: string;
          result: string;
          user_id?: string | null;
        };
        Update: {
          action?: string;
          created_at?: string;
          id?: string;
          ip_address?: string | null;
          metadata?: Json | null;
          reason?: string | null;
          resource_id?: string | null;
          resource_type?: string;
          result?: string;
          user_id?: string | null;
        };
        Relationships: [];
      };
      security_events: {
        Row: {
          action: string | null;
          created_at: string;
          event_type: string;
          id: string;
          metadata: Json | null;
          outcome: string | null;
          resource: string | null;
          severity: string;
          source_ip: string | null;
          user_agent: string | null;
          user_id: string | null;
        };
        Insert: {
          action?: string | null;
          created_at?: string;
          event_type: string;
          id?: string;
          metadata?: Json | null;
          outcome?: string | null;
          resource?: string | null;
          severity?: string;
          source_ip?: string | null;
          user_agent?: string | null;
          user_id?: string | null;
        };
        Update: {
          action?: string | null;
          created_at?: string;
          event_type?: string;
          id?: string;
          metadata?: Json | null;
          outcome?: string | null;
          resource?: string | null;
          severity?: string;
          source_ip?: string | null;
          user_agent?: string | null;
          user_id?: string | null;
        };
        Relationships: [];
      };
      semantic_embeddings: {
        Row: {
          cache_key: string | null;
          created_at: string;
          embedding: number[] | null;
          hit_count: number | null;
          id: string;
          query_hash: string;
          similarity_threshold: number | null;
          user_id: string;
        };
        Insert: {
          cache_key?: string | null;
          created_at?: string;
          embedding?: number[] | null;
          hit_count?: number | null;
          id?: string;
          query_hash: string;
          similarity_threshold?: number | null;
          user_id: string;
        };
        Update: {
          cache_key?: string | null;
          created_at?: string;
          embedding?: number[] | null;
          hit_count?: number | null;
          id?: string;
          query_hash?: string;
          similarity_threshold?: number | null;
          user_id?: string;
        };
        Relationships: [];
      };
      subscriptions: {
        Row: {
          api_calls_limit: number;
          api_calls_used: number;
          created_at: string;
          id: string;
          reset_at: string;
          status: string;
          tier: string;
          updated_at: string;
          user_id: string;
        };
        Insert: {
          api_calls_limit?: number;
          api_calls_used?: number;
          created_at?: string;
          id?: string;
          reset_at?: string;
          status?: string;
          tier?: string;
          updated_at?: string;
          user_id: string;
        };
        Update: {
          api_calls_limit?: number;
          api_calls_used?: number;
          created_at?: string;
          id?: string;
          reset_at?: string;
          status?: string;
          tier?: string;
          updated_at?: string;
          user_id?: string;
        };
        Relationships: [];
      };
      system_health: {
        Row: {
          checks_failed: number | null;
          checks_passed: number | null;
          created_at: string | null;
          health_score: number | null;
          id: string;
          issues: Json | null;
          last_check_at: string | null;
          recommendations: Json | null;
          status: string | null;
          user_id: string;
        };
        Insert: {
          checks_failed?: number | null;
          checks_passed?: number | null;
          created_at?: string | null;
          health_score?: number | null;
          id?: string;
          issues?: Json | null;
          last_check_at?: string | null;
          recommendations?: Json | null;
          status?: string | null;
          user_id: string;
        };
        Update: {
          checks_failed?: number | null;
          checks_passed?: number | null;
          created_at?: string | null;
          health_score?: number | null;
          id?: string;
          issues?: Json | null;
          last_check_at?: string | null;
          recommendations?: Json | null;
          status?: string | null;
          user_id?: string;
        };
        Relationships: [];
      };
      system_limits: {
        Row: {
          applies_to_role: Database["public"]["Enums"]["app_role"] | null;
          created_at: string;
          description: string | null;
          id: string;
          limit_key: string;
          limit_type: string;
          limit_value: number;
          scope: string;
          updated_at: string;
        };
        Insert: {
          applies_to_role?: Database["public"]["Enums"]["app_role"] | null;
          created_at?: string;
          description?: string | null;
          id?: string;
          limit_key: string;
          limit_type: string;
          limit_value: number;
          scope: string;
          updated_at?: string;
        };
        Update: {
          applies_to_role?: Database["public"]["Enums"]["app_role"] | null;
          created_at?: string;
          description?: string | null;
          id?: string;
          limit_key?: string;
          limit_type?: string;
          limit_value?: number;
          scope?: string;
          updated_at?: string;
        };
        Relationships: [];
      };
      system_metrics: {
        Row: {
          active_jobs: number | null;
          cpu_percent: number | null;
          device_id: string | null;
          disk_gb: number | null;
          gpu_utilization: number | null;
          id: string;
          memory_usage: number | null;
          metadata: Json | null;
          power_draw: number | null;
          recorded_at: string;
          status: string | null;
          temperature: number | null;
          throughput: number | null;
          total_requests: number | null;
          user_id: string;
        };
        Insert: {
          active_jobs?: number | null;
          cpu_percent?: number | null;
          device_id?: string | null;
          disk_gb?: number | null;
          gpu_utilization?: number | null;
          id?: string;
          memory_usage?: number | null;
          metadata?: Json | null;
          power_draw?: number | null;
          recorded_at?: string;
          status?: string | null;
          temperature?: number | null;
          throughput?: number | null;
          total_requests?: number | null;
          user_id: string;
        };
        Update: {
          active_jobs?: number | null;
          cpu_percent?: number | null;
          device_id?: string | null;
          disk_gb?: number | null;
          gpu_utilization?: number | null;
          id?: string;
          memory_usage?: number | null;
          metadata?: Json | null;
          power_draw?: number | null;
          recorded_at?: string;
          status?: string | null;
          temperature?: number | null;
          throughput?: number | null;
          total_requests?: number | null;
          user_id?: string;
        };
        Relationships: [
          {
            foreignKeyName: "system_metrics_device_id_fkey";
            columns: ["device_id"];
            isOneToOne: false;
            referencedRelation: "device_registry";
            referencedColumns: ["id"];
          },
        ];
      };
      system_settings: {
        Row: {
          key: string;
          updated_at: string;
          value: Json;
        };
        Insert: {
          key: string;
          updated_at?: string;
          value: Json;
        };
        Update: {
          key?: string;
          updated_at?: string;
          value?: Json;
        };
        Relationships: [];
      };
      team_members: {
        Row: {
          id: string;
          joined_at: string;
          role: string;
          team_id: string | null;
          user_id: string;
        };
        Insert: {
          id?: string;
          joined_at?: string;
          role?: string;
          team_id?: string | null;
          user_id: string;
        };
        Update: {
          id?: string;
          joined_at?: string;
          role?: string;
          team_id?: string | null;
          user_id?: string;
        };
        Relationships: [
          {
            foreignKeyName: "team_members_team_id_fkey";
            columns: ["team_id"];
            isOneToOne: false;
            referencedRelation: "teams";
            referencedColumns: ["id"];
          },
        ];
      };
      teams: {
        Row: {
          created_at: string;
          description: string | null;
          id: string;
          name: string;
          owner_id: string;
          settings: Json | null;
          updated_at: string;
        };
        Insert: {
          created_at?: string;
          description?: string | null;
          id?: string;
          name: string;
          owner_id: string;
          settings?: Json | null;
          updated_at?: string;
        };
        Update: {
          created_at?: string;
          description?: string | null;
          id?: string;
          name?: string;
          owner_id?: string;
          settings?: Json | null;
          updated_at?: string;
        };
        Relationships: [];
      };
      threats_detected: {
        Row: {
          auto_mitigated: boolean | null;
          description: string | null;
          detected_at: string;
          id: string;
          mitigated_at: string | null;
          mitigation_status: string | null;
          severity: string;
          source: string | null;
          target: string | null;
          threat_type: string;
          user_id: string | null;
        };
        Insert: {
          auto_mitigated?: boolean | null;
          description?: string | null;
          detected_at?: string;
          id?: string;
          mitigated_at?: string | null;
          mitigation_status?: string | null;
          severity: string;
          source?: string | null;
          target?: string | null;
          threat_type: string;
          user_id?: string | null;
        };
        Update: {
          auto_mitigated?: boolean | null;
          description?: string | null;
          detected_at?: string;
          id?: string;
          mitigated_at?: string | null;
          mitigation_status?: string | null;
          severity?: string;
          source?: string | null;
          target?: string | null;
          threat_type?: string;
          user_id?: string | null;
        };
        Relationships: [];
      };
      traces: {
        Row: {
          duration_ms: number | null;
          ended_at: string | null;
          id: string;
          logs: Json | null;
          operation_name: string;
          parent_span_id: string | null;
          service_name: string | null;
          span_id: string;
          started_at: string;
          status: string | null;
          tags: Json | null;
          trace_id: string;
          user_id: string;
        };
        Insert: {
          duration_ms?: number | null;
          ended_at?: string | null;
          id?: string;
          logs?: Json | null;
          operation_name: string;
          parent_span_id?: string | null;
          service_name?: string | null;
          span_id: string;
          started_at: string;
          status?: string | null;
          tags?: Json | null;
          trace_id: string;
          user_id: string;
        };
        Update: {
          duration_ms?: number | null;
          ended_at?: string | null;
          id?: string;
          logs?: Json | null;
          operation_name?: string;
          parent_span_id?: string | null;
          service_name?: string | null;
          span_id?: string;
          started_at?: string;
          status?: string | null;
          tags?: Json | null;
          trace_id?: string;
          user_id?: string;
        };
        Relationships: [];
      };
      usage_stats: {
        Row: {
          api_key_id: string | null;
          created_at: string;
          credits_used: number;
          id: string;
          operation_count: number;
          operation_type: string;
          user_id: string;
        };
        Insert: {
          api_key_id?: string | null;
          created_at?: string;
          credits_used?: number;
          id?: string;
          operation_count?: number;
          operation_type: string;
          user_id: string;
        };
        Update: {
          api_key_id?: string | null;
          created_at?: string;
          credits_used?: number;
          id?: string;
          operation_count?: number;
          operation_type?: string;
          user_id?: string;
        };
        Relationships: [
          {
            foreignKeyName: "usage_stats_api_key_id_fkey";
            columns: ["api_key_id"];
            isOneToOne: false;
            referencedRelation: "api_keys";
            referencedColumns: ["id"];
          },
          {
            foreignKeyName: "usage_stats_api_key_id_fkey";
            columns: ["api_key_id"];
            isOneToOne: false;
            referencedRelation: "api_keys_safe";
            referencedColumns: ["id"];
          },
        ];
      };
      user_behaviors: {
        Row: {
          action: string;
          behavior_type: string;
          id: string;
          metadata: Json | null;
          recorded_at: string;
          session_id: string | null;
          target: string | null;
          user_id: string;
        };
        Insert: {
          action: string;
          behavior_type: string;
          id?: string;
          metadata?: Json | null;
          recorded_at?: string;
          session_id?: string | null;
          target?: string | null;
          user_id: string;
        };
        Update: {
          action?: string;
          behavior_type?: string;
          id?: string;
          metadata?: Json | null;
          recorded_at?: string;
          session_id?: string | null;
          target?: string | null;
          user_id?: string;
        };
        Relationships: [];
      };
      user_roles: {
        Row: {
          created_at: string;
          id: string;
          role: Database["public"]["Enums"]["app_role"];
          user_id: string;
        };
        Insert: {
          created_at?: string;
          id?: string;
          role?: Database["public"]["Enums"]["app_role"];
          user_id: string;
        };
        Update: {
          created_at?: string;
          id?: string;
          role?: Database["public"]["Enums"]["app_role"];
          user_id?: string;
        };
        Relationships: [];
      };
      video_benchmarks: {
        Row: {
          codec: string | null;
          created_at: string;
          framerate: number | null;
          id: string;
          keyframe_interval: number | null;
          latency_ms: number | null;
          name: string;
          pipeline_config: Json | null;
          quality_score: number | null;
          resolution: string | null;
          user_id: string;
        };
        Insert: {
          codec?: string | null;
          created_at?: string;
          framerate?: number | null;
          id?: string;
          keyframe_interval?: number | null;
          latency_ms?: number | null;
          name: string;
          pipeline_config?: Json | null;
          quality_score?: number | null;
          resolution?: string | null;
          user_id: string;
        };
        Update: {
          codec?: string | null;
          created_at?: string;
          framerate?: number | null;
          id?: string;
          keyframe_interval?: number | null;
          latency_ms?: number | null;
          name?: string;
          pipeline_config?: Json | null;
          quality_score?: number | null;
          resolution?: string | null;
          user_id?: string;
        };
        Relationships: [];
      };
      webhook_test_log: {
        Row: {
          created_at: string;
          id: string;
          status_code: number | null;
          success: boolean | null;
          user_id: string;
          webhook_url: string;
        };
        Insert: {
          created_at?: string;
          id?: string;
          status_code?: number | null;
          success?: boolean | null;
          user_id: string;
          webhook_url: string;
        };
        Update: {
          created_at?: string;
          id?: string;
          status_code?: number | null;
          success?: boolean | null;
          user_id?: string;
          webhook_url?: string;
        };
        Relationships: [];
      };
      worker_api_keys: {
        Row: {
          created_at: string;
          id: string;
          is_active: boolean | null;
          key_hash: string;
          key_prefix: string;
          last_used_at: string | null;
          worker_name: string;
        };
        Insert: {
          created_at?: string;
          id?: string;
          is_active?: boolean | null;
          key_hash: string;
          key_prefix: string;
          last_used_at?: string | null;
          worker_name: string;
        };
        Update: {
          created_at?: string;
          id?: string;
          is_active?: boolean | null;
          key_hash?: string;
          key_prefix?: string;
          last_used_at?: string | null;
          worker_name?: string;
        };
        Relationships: [];
      };
      workload_predictions: {
        Row: {
          actual_value: number | null;
          confidence_lower: number | null;
          confidence_upper: number | null;
          created_at: string;
          id: string;
          is_anomaly: boolean | null;
          model_version: string | null;
          predicted_value: number;
          prediction_type: string;
          target_time: string;
          time_horizon: string;
          user_id: string;
        };
        Insert: {
          actual_value?: number | null;
          confidence_lower?: number | null;
          confidence_upper?: number | null;
          created_at?: string;
          id?: string;
          is_anomaly?: boolean | null;
          model_version?: string | null;
          predicted_value: number;
          prediction_type: string;
          target_time: string;
          time_horizon: string;
          user_id: string;
        };
        Update: {
          actual_value?: number | null;
          confidence_lower?: number | null;
          confidence_upper?: number | null;
          created_at?: string;
          id?: string;
          is_anomaly?: boolean | null;
          model_version?: string | null;
          predicted_value?: number;
          prediction_type?: string;
          target_time?: string;
          time_horizon?: string;
          user_id?: string;
        };
        Relationships: [];
      };
    };
    Views: {
      api_keys_safe: {
        Row: {
          created_at: string | null;
          expires_at: string | null;
          id: string | null;
          is_active: boolean | null;
          key_name: string | null;
          key_prefix: string | null;
          last_used_at: string | null;
          user_id: string | null;
        };
        Insert: {
          created_at?: string | null;
          expires_at?: string | null;
          id?: string | null;
          is_active?: boolean | null;
          key_name?: string | null;
          key_prefix?: string | null;
          last_used_at?: string | null;
          user_id?: string | null;
        };
        Update: {
          created_at?: string | null;
          expires_at?: string | null;
          id?: string | null;
          is_active?: boolean | null;
          key_name?: string | null;
          key_prefix?: string | null;
          last_used_at?: string | null;
          user_id?: string | null;
        };
        Relationships: [];
      };
    };
    Functions: {
      check_rate_limit: {
        Args: {
          _action_type: string;
          _user_id: string;
          _window_minutes?: number;
        };
        Returns: boolean;
      };
      has_role: {
        Args: {
          _role: Database["public"]["Enums"]["app_role"];
          _user_id: string;
        };
        Returns: boolean;
      };
      hash_api_key: { Args: { key_value: string }; Returns: string };
      is_feature_enabled: {
        Args: { _flag_key: string; _user_id?: string };
        Returns: boolean;
      };
      is_team_member: {
        Args: { _team_id: string; _user_id: string };
        Returns: boolean;
      };
      log_security_event: {
        Args: {
          _action: string;
          _metadata?: Json;
          _reason?: string;
          _resource_id: string;
          _resource_type: string;
          _result: string;
          _user_id: string;
        };
        Returns: string;
      };
      validate_api_key: { Args: { key_to_validate: string }; Returns: string };
      verify_api_key: {
        Args: { provided_key: string; stored_hash: string };
        Returns: boolean;
      };
    };
    Enums: {
      app_role: "admin" | "user" | "enterprise";
      job_tier: "light" | "medium" | "heavy";
    };
    CompositeTypes: {
      [_ in never]: never;
    };
  };
};

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">;

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">];

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals;
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals;
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R;
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] & DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R;
      }
      ? R
      : never
    : never;

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    keyof DefaultSchema["Tables"] | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals;
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals;
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I;
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I;
      }
      ? I
      : never
    : never;

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    keyof DefaultSchema["Tables"] | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals;
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals;
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U;
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U;
      }
      ? U
      : never
    : never;

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    keyof DefaultSchema["Enums"] | { schema: keyof DatabaseWithoutInternals },
  EnumName extends (DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals;
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never) = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals;
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never;

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    keyof DefaultSchema["CompositeTypes"] | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends (PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals;
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never) = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals;
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never;

export const Constants = {
  public: {
    Enums: {
      app_role: ["admin", "user", "enterprise"],
      job_tier: ["light", "medium", "heavy"],
    },
  },
} as const;
