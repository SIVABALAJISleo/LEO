import { ReliabilityOrchestrator } from './core/ReliabilityOrchestrator';
import { MoERouter } from './intelligence/MoERouter';
import { HealthMonitor } from './core/HealthMonitor';
import { BackgroundJobQueue } from './core/BackgroundJobQueue';
import { PrecomputationWorker } from './intelligence/PrecomputationWorker';
import { VisionDeltaProcessor } from './vision/VisionDeltaProcessor';
import { DeterministicPhysics } from './simulation/DeterministicPhysics';

export const initializeEngine = () => {
    console.log('[Engine] Initializing Production SaaS Layer...');

    const orchestrator = ReliabilityOrchestrator.getInstance();
    const router = MoERouter.getInstance();
    const queue = BackgroundJobQueue.getInstance();
    const precomp = PrecomputationWorker.getInstance();
    const vision = VisionDeltaProcessor.getInstance();
    const physics = DeterministicPhysics.getInstance();

    // 1. Initialise Baked Data
    physics.registerAnimation('idle_hover', [
        { position: { x: 0, y: 0, z: 0 }, rotation: { x: 0, y: 0, z: 0 }, velocity: { x: 0, y: 0, z: 0 }, timestamp: 0 },
        { position: { x: 0, y: 0.5, z: 0 }, rotation: { x: 0, y: 10, z: 0 }, velocity: { x: 0, y: 0, z: 0 }, timestamp: 1000 },
        { position: { x: 0, y: 0, z: 0 }, rotation: { x: 0, y: 0, z: 0 }, velocity: { x: 0, y: 0, z: 0 }, timestamp: 2000 }
    ]);

    // 2. Register Core Engine Handlers
    orchestrator.register('ai_inference', async (payload: any) => {
        return await router.process(payload.query || 'general query');
    }, async () => {
        return '[Fallback] AI Expert is temporarily unavailable. Using base knowledge.';
    });

    orchestrator.register('vision_process', async (payload: any) => {
        console.log('[Engine] Processing Vision Delta...');
        if (payload.frame) return vision.detectDelta(payload.frame);
        return { changeDetected: false, changeMagnitude: 0, changedRegions: [] };
    });

    orchestrator.register('physics_sim', async (payload: any) => {
        if (payload.action === 'spawn') {
            physics.spawnObject(payload.id, payload.animId);
            return { status: 'spawned' };
        }
        return physics.getState(payload.id);
    });

    orchestrator.register('system_update', async (payload: any) => {
        console.log('[Engine] Processing system update:', payload);
        await new Promise(r => setTimeout(r, 1000));
        return { success: true, timestamp: Date.now() };
    });

    // 3. Start Background Workers
    precomp.start();

    console.log('[Engine] All layers active.');
};
