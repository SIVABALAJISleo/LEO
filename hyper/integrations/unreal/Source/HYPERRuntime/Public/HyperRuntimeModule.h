// Copyright 2026 LEO / HYPER Project. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"
#include "UObject/NoExportTypes.h"
#include "HyperRuntimeModule.generated.h"

class FHyperRuntimeModule : public IModuleInterface
{
public:
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;
};

/**
 * UHyperFrameAnalyzer: Evaluates scene state, camera motion, delta changes, and cost maps.
 */
UCLASS(BlueprintType)
class HYPERRUNTIME_API UHyperFrameAnalyzer : public UObject
{
	GENERATED_BODY()
public:
	UFUNCTION(BlueprintCallable, Category = "HYPER|Analysis")
	void AnalyzeFrame(const FVector& CameraPosition, const FRotator& CameraRotation, float DeltaSeconds);

	UPROPERTY(BlueprintReadOnly, Category = "HYPER|Analysis")
	float CalculatedChangeRatio = 0.0f;
};

/**
 * UHyperVisibility: Frustum, distance, and hierarchical occlusion culling.
 */
UCLASS(BlueprintType)
class HYPERRUNTIME_API UHyperVisibility : public UObject
{
	GENERATED_BODY()
public:
	UFUNCTION(BlueprintCallable, Category = "HYPER|Visibility")
	bool EvaluateVisibility(const FVector& BoundsOrigin, const FVector& BoundsExtent, float MaxDistance);
};

/**
 * UHyperTemporalCache: History management for color, depth, and motion buffers.
 */
UCLASS(BlueprintType)
class HYPERRUNTIME_API UHyperTemporalCache : public UObject
{
	GENERATED_BODY()
public:
	UFUNCTION(BlueprintCallable, Category = "HYPER|Temporal")
	void StoreFrameHistory(int32 FrameIndex);

	UFUNCTION(BlueprintCallable, Category = "HYPER|Temporal")
	void InvalidateHistory(const FString& Reason);
};

/**
 * UHyperImportance: Evaluates spatial & object importance in [0, 1].
 */
UCLASS(BlueprintType)
class HYPERRUNTIME_API UHyperImportance : public UObject
{
	GENERATED_BODY()
public:
	UFUNCTION(BlueprintCallable, Category = "HYPER|Importance")
	float GetObjectImportance(AActor* TargetActor);
};

/**
 * UHyperResolutionController: Dynamic Variable Rate Shading and resolution scaling per tile.
 */
UCLASS(BlueprintType)
class HYPERRUNTIME_API UHyperResolutionController : public UObject
{
	GENERATED_BODY()
public:
	UFUNCTION(BlueprintCallable, Category = "HYPER|Resolution")
	float GetTileResolutionScale(float ImportanceScore, float UncertaintyScore);
};

/**
 * UHyperReconstruction: Motion-vector reprojection, variance-guided neighborhood clamping, and bilateral filtering.
 */
UCLASS(BlueprintType)
class HYPERRUNTIME_API UHyperReconstruction : public UObject
{
	GENERATED_BODY()
public:
	UFUNCTION(BlueprintCallable, Category = "HYPER|Reconstruction")
	void ReconstructFrame(float ConfidenceThreshold);
};

/**
 * UHyperScheduler: CPU Strategic Controller + Intel UHD iGPU Parallel Executor dispatch.
 */
UCLASS(BlueprintType)
class HYPERRUNTIME_API UHyperScheduler : public UObject
{
	GENERATED_BODY()
public:
	UFUNCTION(BlueprintCallable, Category = "HYPER|Scheduler")
	FString DecideExecutionRoute(int32 EstimatedPixelCount, float ConfidenceScore);
};

/**
 * UHyperMemoryManager: Manages logical L1 through L5 software memory hierarchy in UE5.
 */
UCLASS(BlueprintType)
class HYPERRUNTIME_API UHyperMemoryManager : public UObject
{
	GENERATED_BODY()
public:
	UFUNCTION(BlueprintCallable, Category = "HYPER|Memory")
	void EnforceBudgetLimits(float MaxRAMBudgetMB);
};

/**
 * UHyperTelemetry: Performance traces, eliminated work counters, and frame timers.
 */
UCLASS(BlueprintType)
class HYPERRUNTIME_API UHyperTelemetry : public UObject
{
	GENERATED_BODY()
public:
	UFUNCTION(BlueprintCallable, Category = "HYPER|Telemetry")
	void RecordFrameMetrics(float FrameTimeMS, float WorkEliminatedPct, float TemporalReusePct);
};

/**
 * UHyperQualityVerifier: Automated PSNR, SSIM, and artifact detection with fallback trigger.
 */
UCLASS(BlueprintType)
class HYPERRUNTIME_API UHyperQualityVerifier : public UObject
{
	GENERATED_BODY()
public:
	UFUNCTION(BlueprintCallable, Category = "HYPER|Verifier")
	bool VerifyContract(float PSNRThreshold, float SSIMThreshold);
};
