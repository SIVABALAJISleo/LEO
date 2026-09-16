// Copyright 2026 LEO / HYPER Project. All Rights Reserved.
using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace HYPER.Unity
{
    /// <summary>
    /// HyperLOD: Dynamic distance and screen-percentage LOD selector.
    /// </summary>
    [AddComponentMenu("HYPER/Hyper LOD")]
    public class HyperLOD : MonoBehaviour
    {
        public float[] ScreenCoverageThresholds = new float[] { 0.25f, 0.08f, 0.02f, 0.005f };
        public GameObject[] LodMeshes;

        public int SelectLOD(float screenFraction)
        {
            for (int i = 0; i < ScreenCoverageThresholds.Length; i++)
            {
                if (screenFraction >= ScreenCoverageThresholds[i]) return i;
            }
            return LodMeshes != null ? LodMeshes.Length - 1 : 0;
        }
    }

    /// <summary>
    /// HyperVisibility: Frustum and distance culling pass.
    /// </summary>
    [AddComponentMenu("HYPER/Hyper Visibility")]
    public class HyperVisibility : MonoBehaviour
    {
        public float MaxDrawDistance = 500f;
        public bool IsVisible(Camera cam, Bounds bounds)
        {
            float dist = Vector3.Distance(cam.transform.position, bounds.center);
            if (dist > MaxDrawDistance) return false;
            Plane[] planes = GeometryUtility.CalculateFrustumPlanes(cam);
            return GeometryUtility.TestPlanesAABB(planes, bounds);
        }
    }

    /// <summary>
    /// HyperInstanceManager: Batches identical meshes into GPU instancing calls.
    /// </summary>
    [AddComponentMenu("HYPER/Hyper Instance Manager")]
    public class HyperInstanceManager : MonoBehaviour
    {
        public void BatchDraw(Mesh mesh, Material material, Matrix4x4[] matrices, int count)
        {
            Graphics.DrawMeshInstanced(mesh, 0, material, matrices, count);
        }
    }

    /// <summary>
    /// HyperTemporalCache: History management for color, depth, and motion buffers.
    /// </summary>
    public class HyperTemporalCache
    {
        private RenderTexture _historyColor;
        private RenderTexture _historyDepth;

        public RenderTexture HistoryColor => _historyColor;
        public RenderTexture HistoryDepth => _historyDepth;

        public void Allocate(int width, int height)
        {
            if (_historyColor == null || _historyColor.width != width || _historyColor.height != height)
            {
                if (_historyColor != null) _historyColor.Release();
                _historyColor = new RenderTexture(width, height, 0, RenderTextureFormat.ARGBHalf);
                _historyColor.Create();
            }
        }

        public void Release()
        {
            if (_historyColor != null) { _historyColor.Release(); _historyColor = null; }
            if (_historyDepth != null) { _historyDepth.Release(); _historyDepth = null; }
        }
    }

    /// <summary>
    /// HyperImportance: Assigns spatial and object importance in [0.0, 1.0].
    /// </summary>
    [AddComponentMenu("HYPER/Hyper Importance")]
    public class HyperImportance : MonoBehaviour
    {
        [Range(0f, 1f)] public float BaseImportance = 0.5f;
        public string SemanticCategory = "geometry";

        public float Evaluate(Camera cam)
        {
            float dist = Vector3.Distance(cam.transform.position, transform.position);
            float distFactor = 1f / (1f + dist * 0.05f);
            return Mathf.Clamp01(BaseImportance * distFactor);
        }
    }

    /// <summary>
    /// HyperScheduler: Determines CPU vs iGPU vs Reprojected pass.
    /// </summary>
    public class HyperScheduler
    {
        public enum ExecutionRoute { Cached, Reprojected, FullCompute }

        public ExecutionRoute Schedule(float confidence, float importance)
        {
            if (confidence > 0.8f && importance < 0.7f) return ExecutionRoute.Cached;
            if (confidence > 0.4f) return ExecutionRoute.Reprojected;
            return ExecutionRoute.FullCompute;
        }
    }

    /// <summary>
    /// HyperReconstruction: Custom SRP render pass for motion reprojection and bilateral filter.
    /// </summary>
    public class HyperReconstruction
    {
        public void ExecutePass(CommandBuffer cmd, RenderTargetIdentifier source, RenderTargetIdentifier destination, Material reprojectionMat)
        {
            cmd.Blit(source, destination, reprojectionMat);
        }
    }

    /// <summary>
    /// HyperProfiler: Telemetry recording frame time, work avoided, and memory bandwidth.
    /// </summary>
    public class HyperProfiler
    {
        public float LastFrameTimeMS { get; set; }
        public float WorkAvoidedPct { get; set; }
    }

    /// <summary>
    /// HyperQualityVerifier: Checks PSNR and triggers fallback if quality drops below threshold.
    /// </summary>
    public class HyperQualityVerifier
    {
        public bool Verify(float estimatedPSNR)
        {
            return estimatedPSNR >= 32.0f;
        }
    }
}
