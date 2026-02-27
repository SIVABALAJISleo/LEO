import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

const SUPABASE_URL = Deno.env.get('SUPABASE_URL')!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);
    const { action, jobId, jobType } = await req.json();
    
    console.log(`[JobProcessor] Action: ${action}, JobId: ${jobId}, Type: ${jobType}`);

    let result: any = {};

    switch (action) {
      case 'process_next':
        result = await processNextJob(supabase);
        break;
      case 'process_job':
        result = await processSpecificJob(supabase, jobId);
        break;
      case 'process_gpu_job':
        result = await processGpuJob(supabase, jobId);
        break;
      case 'process_inference_job':
        result = await processInferenceJob(supabase, jobId);
        break;
      case 'check_queue':
        result = await checkAndProcessQueue(supabase);
        break;
      case 'update_progress':
        result = await simulateProgress(supabase, jobId);
        break;
      default:
        return new Response(JSON.stringify({ error: 'Unknown action' }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        });
    }

    return new Response(JSON.stringify({ success: true, ...result }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });

  } catch (error: unknown) {
    console.error('[JobProcessor] Error:', error);
    // Return generic error to client, log details server-side only
    return new Response(JSON.stringify({ error: 'An internal error occurred' }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
});

async function processNextJob(supabase: any) {
  // Check GPU jobs first
  const { data: gpuJob } = await supabase
    .from('gpu_jobs')
    .select('*')
    .in('status', ['pending', 'queued'])
    .order('priority', { ascending: false })
    .order('created_at', { ascending: true })
    .limit(1)
    .single();

  if (gpuJob) {
    return await processGpuJob(supabase, gpuJob.id);
  }

  // Then check inference jobs
  const { data: inferenceJob } = await supabase
    .from('inference_jobs')
    .select('*')
    .eq('status', 'queued')
    .order('priority', { ascending: false })
    .order('created_at', { ascending: true })
    .limit(1)
    .single();

  if (inferenceJob) {
    return await processInferenceJob(supabase, inferenceJob.id);
  }

  return { message: 'No jobs in queue' };
}

async function processSpecificJob(supabase: any, jobId: string) {
  // Determine job type
  const { data: gpuJob } = await supabase
    .from('gpu_jobs')
    .select('*')
    .eq('id', jobId)
    .single();

  if (gpuJob) {
    return await processGpuJob(supabase, jobId);
  }

  const { data: inferenceJob } = await supabase
    .from('inference_jobs')
    .select('*')
    .eq('id', jobId)
    .single();

  if (inferenceJob) {
    return await processInferenceJob(supabase, jobId);
  }

  return { error: 'Job not found' };
}

async function processGpuJob(supabase: any, jobId: string) {
  console.log(`[JobProcessor] Processing GPU job: ${jobId}`);

  // Mark as running
  const { error: startError } = await supabase
    .from('gpu_jobs')
    .update({
      status: 'running',
      started_at: new Date().toISOString(),
      progress: 0,
      worker_id: 'gpu-worker-primary',
    })
    .eq('id', jobId);

  if (startError) {
    console.error('[JobProcessor] Start error:', startError);
    return { error: startError.message };
  }

  // Get job details
  const { data: job } = await supabase
    .from('gpu_jobs')
    .select('*')
    .eq('id', jobId)
    .single();

  if (!job) {
    return { error: 'Job not found after starting' };
  }

  // Simulate processing with progress updates
  const totalSteps = 10;
  const stepDuration = Math.floor((job.estimated_duration_sec || 30) * 100 / totalSteps); // ms per step

  for (let step = 1; step <= totalSteps; step++) {
    await new Promise(resolve => setTimeout(resolve, Math.min(stepDuration, 500))); // Max 500ms per step for demo
    
    const progress = Math.floor((step / totalSteps) * 100);
    const eta = Math.floor((totalSteps - step) * (job.estimated_duration_sec || 30) / totalSteps);

    await supabase
      .from('gpu_jobs')
      .update({
        progress,
        eta_seconds: eta,
        checkpoint_at: step % 3 === 0 ? new Date().toISOString() : undefined,
      })
      .eq('id', jobId);

    console.log(`[JobProcessor] GPU Job ${jobId} progress: ${progress}%`);
  }

  // Complete the job
  const resultData = generateJobResult(job.job_type, job.payload);
  
  const { error: completeError } = await supabase
    .from('gpu_jobs')
    .update({
      status: 'completed',
      progress: 100,
      eta_seconds: 0,
      completed_at: new Date().toISOString(),
      result_data: resultData,
    })
    .eq('id', jobId);

  if (completeError) {
    console.error('[JobProcessor] Complete error:', completeError);
    return { error: completeError.message };
  }

  // Update system status
  await supabase
    .from('gpu_system_status')
    .update({
      jobs_completed_today: supabase.sql`jobs_completed_today + 1`,
      active_job_id: null,
      last_heartbeat_at: new Date().toISOString(),
    })
    .eq('worker_id', 'gpu-worker-primary');

  // Log completion
  await supabase
    .from('job_logs')
    .insert({
      job_id: jobId,
      user_id: job.user_id,
      log_level: 'info',
      message: `Job completed successfully. Type: ${job.job_type}`,
      metadata: { result_summary: resultData.summary || 'Processing complete' },
    });

  return { 
    status: 'completed', 
    jobId, 
    result: resultData,
    processingTime: job.estimated_duration_sec || 30
  };
}

async function processInferenceJob(supabase: any, jobId: string) {
  console.log(`[JobProcessor] Processing inference job: ${jobId}`);

  // Mark as running
  const { error: startError } = await supabase
    .from('inference_jobs')
    .update({
      status: 'running',
      started_at: new Date().toISOString(),
      progress: 0,
    })
    .eq('id', jobId);

  if (startError) {
    return { error: startError.message };
  }

  // Get job with model info
  const { data: job } = await supabase
    .from('inference_jobs')
    .select('*, models(name, model_type)')
    .eq('id', jobId)
    .single();

  if (!job) {
    return { error: 'Job not found' };
  }

  // Simulate processing
  const totalSteps = 10;
  for (let step = 1; step <= totalSteps; step++) {
    await new Promise(resolve => setTimeout(resolve, 200));
    
    const progress = Math.floor((step / totalSteps) * 100);
    
    await supabase
      .from('inference_jobs')
      .update({ progress })
      .eq('id', jobId);

    console.log(`[JobProcessor] Inference Job ${jobId} progress: ${progress}%`);
  }

  // Generate realistic results based on enabled modules
  const enabledModules = job.enabled_modules || [];
  const baseLatency = 100 + Math.random() * 200;
  const speedup = 1 + (enabledModules.length * 0.3) + Math.random() * 0.5;
  const compressionRatio = enabledModules.includes('quantization') || enabledModules.includes('pruning') 
    ? 0.3 + Math.random() * 0.3 
    : null;

  const outputData = {
    model_output: generateModelOutput(job.models?.model_type || 'transformer'),
    optimization_results: {
      modules_applied: enabledModules,
      original_latency_ms: baseLatency * speedup,
      optimized_latency_ms: baseLatency,
      memory_saved_mb: Math.floor(100 + Math.random() * 500),
    },
    metadata: {
      processed_at: new Date().toISOString(),
      worker: 'inference-worker-1',
    },
  };

  // Complete the job
  const { error: completeError } = await supabase
    .from('inference_jobs')
    .update({
      status: 'completed',
      progress: 100,
      completed_at: new Date().toISOString(),
      output_data: outputData,
      latency_ms: Math.floor(baseLatency),
      speedup: Math.round(speedup * 100) / 100,
      compression_ratio: compressionRatio ? Math.round(compressionRatio * 100) / 100 : null,
    })
    .eq('id', jobId);

  if (completeError) {
    return { error: completeError.message };
  }

  // Record performance metrics
  await supabase
    .from('performance_metrics')
    .insert({
      user_id: job.user_id,
      job_id: jobId,
      model_id: job.model_id,
      metric_name: 'inference_complete',
      metric_value: speedup,
      latency_ms: baseLatency,
      throughput_rps: Math.floor(1000 / baseLatency * 10),
      cache_hit_ratio: Math.random() * 0.4 + 0.6,
    });

  return {
    status: 'completed',
    jobId,
    latency_ms: baseLatency,
    speedup,
    compression_ratio: compressionRatio,
  };
}

async function checkAndProcessQueue(supabase: any) {
  // Count jobs in queue
  const { count: gpuCount } = await supabase
    .from('gpu_jobs')
    .select('*', { count: 'exact', head: true })
    .in('status', ['pending', 'queued']);

  const { count: inferenceCount } = await supabase
    .from('inference_jobs')
    .select('*', { count: 'exact', head: true })
    .eq('status', 'queued');

  const { count: runningCount } = await supabase
    .from('gpu_jobs')
    .select('*', { count: 'exact', head: true })
    .eq('status', 'running');

  // Process up to 2 jobs if none are running
  const processed: any[] = [];
  if ((runningCount || 0) < 2 && ((gpuCount || 0) > 0 || (inferenceCount || 0) > 0)) {
    const result = await processNextJob(supabase);
    if ('status' in result && result.status === 'completed') {
      processed.push(result);
    }
  }

  return {
    queue: {
      gpu_pending: gpuCount || 0,
      inference_pending: inferenceCount || 0,
      currently_running: runningCount || 0,
    },
    processed,
  };
}

async function simulateProgress(supabase: any, jobId: string) {
  // Get current progress
  const { data: job } = await supabase
    .from('gpu_jobs')
    .select('progress, status')
    .eq('id', jobId)
    .single();

  if (!job || job.status !== 'running') {
    return { message: 'Job not running' };
  }

  const newProgress = Math.min(100, (job.progress || 0) + Math.floor(Math.random() * 15) + 5);

  if (newProgress >= 100) {
    return await processGpuJob(supabase, jobId);
  }

  await supabase
    .from('gpu_jobs')
    .update({ progress: newProgress })
    .eq('id', jobId);

  return { jobId, progress: newProgress };
}

function generateJobResult(jobType: string, payload: any) {
  const baseResult = {
    summary: `${jobType} completed successfully`,
    processed_at: new Date().toISOString(),
    performance: {
      processing_time_ms: Math.floor(1000 + Math.random() * 5000),
      gpu_memory_peak_mb: Math.floor(2000 + Math.random() * 6000),
      efficiency_score: Math.round((0.7 + Math.random() * 0.3) * 100) / 100,
    },
  };

  switch (jobType) {
    case 'training':
      return {
        ...baseResult,
        epochs_completed: payload?.epochs || 10,
        final_loss: Math.round((0.01 + Math.random() * 0.1) * 1000) / 1000,
        accuracy: Math.round((0.85 + Math.random() * 0.14) * 100) / 100,
        model_path: `/models/trained_${Date.now()}.pt`,
      };
    case 'inference':
      return {
        ...baseResult,
        predictions: Array.from({ length: 5 }, () => ({
          label: ['cat', 'dog', 'bird', 'car', 'plane'][Math.floor(Math.random() * 5)],
          confidence: Math.round((0.7 + Math.random() * 0.3) * 100) / 100,
        })),
        tokens_processed: Math.floor(100 + Math.random() * 1000),
      };
    case 'optimization':
      return {
        ...baseResult,
        original_size_mb: Math.floor(500 + Math.random() * 2000),
        optimized_size_mb: Math.floor(200 + Math.random() * 500),
        speedup_factor: Math.round((1.5 + Math.random() * 2.5) * 100) / 100,
        optimizations_applied: ['quantization', 'pruning', 'fusion'].filter(() => Math.random() > 0.3),
      };
    case 'rendering':
      return {
        ...baseResult,
        frames_rendered: Math.floor(100 + Math.random() * 500),
        resolution: '1920x1080',
        fps: Math.floor(24 + Math.random() * 36),
        output_path: `/renders/output_${Date.now()}.mp4`,
      };
    default:
      return baseResult;
  }
}

function generateModelOutput(modelType: string) {
  switch (modelType) {
    case 'transformer':
      return {
        generated_text: 'This is a sample output from the optimized transformer model.',
        tokens: Math.floor(50 + Math.random() * 150),
        logprobs: [-0.1, -0.05, -0.2, -0.08],
      };
    case 'vision':
      return {
        predictions: [
          { class: 'object_1', confidence: 0.95 },
          { class: 'object_2', confidence: 0.82 },
        ],
        bounding_boxes: [[10, 20, 100, 150]],
      };
    case 'audio':
      return {
        transcript: 'Sample transcription from audio processing.',
        confidence: 0.94,
        segments: [{ start: 0, end: 5.2, text: 'Sample segment' }],
      };
    default:
      return { result: 'Processing complete', confidence: 0.9 };
  }
}
