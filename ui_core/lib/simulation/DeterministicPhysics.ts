/**
 * Deterministic Physics Engine
 *
 * Replaces complex, nondeterministic physics calculations with
 * baked state machines and interpolation.
 */

interface PhysicsState {
  position: { x: number; y: number; z: number };
  rotation: { x: number; y: number; z: number };
  velocity: { x: number; y: number; z: number };
  timestamp: number;
}

interface BakedAnimation {
  id: string;
  duration: number;
  keyframes: PhysicsState[];
}

export class DeterministicPhysics {
  private static instance: DeterministicPhysics;
  private bakedAnimations: Map<string, BakedAnimation> = new Map();
  private activeObjects: Map<string, { animId: string; startTime: number }> = new Map();

  private constructor() {}

  static getInstance(): DeterministicPhysics {
    if (!DeterministicPhysics.instance) {
      DeterministicPhysics.instance = new DeterministicPhysics();
    }
    return DeterministicPhysics.instance;
  }

  // Register a baked animation (e.g. "explosion", "walk_cycle")
  registerAnimation(id: string, keyframes: PhysicsState[]) {
    const duration = keyframes[keyframes.length - 1].timestamp - keyframes[0].timestamp;
    this.bakedAnimations.set(id, { id, duration, keyframes });
  }

  // Start an object on a deterministic path
  spawnObject(objectId: string, animationId: string) {
    if (!this.bakedAnimations.has(animationId)) {
      console.warn(`[Physics] Animation ${animationId} not found`);
      return;
    }
    this.activeObjects.set(objectId, { animId: animationId, startTime: Date.now() });
  }

  // Get current state without computing physics
  getState(objectId: string): PhysicsState | null {
    const obj = this.activeObjects.get(objectId);
    if (!obj) return null;

    const anim = this.bakedAnimations.get(obj.animId);
    if (!anim) return null;

    const elapsed = Date.now() - obj.startTime;

    // Loop animation
    const timeInAnim = elapsed % anim.duration;

    // Find keyframes to interpolate between
    // Binary search would be faster, linear for now
    let prevFrame = anim.keyframes[0];
    let nextFrame = anim.keyframes[anim.keyframes.length - 1];

    for (let i = 0; i < anim.keyframes.length - 1; i++) {
      if (
        anim.keyframes[i].timestamp <= timeInAnim &&
        anim.keyframes[i + 1].timestamp >= timeInAnim
      ) {
        prevFrame = anim.keyframes[i];
        nextFrame = anim.keyframes[i + 1];
        break;
      }
    }

    // Linear Interpolation
    const t = (timeInAnim - prevFrame.timestamp) / (nextFrame.timestamp - prevFrame.timestamp);

    return this.lerpState(prevFrame, nextFrame, t);
  }

  private lerpState(a: PhysicsState, b: PhysicsState, t: number): PhysicsState {
    return {
      position: {
        x: a.position.x + (b.position.x - a.position.x) * t,
        y: a.position.y + (b.position.y - a.position.y) * t,
        z: a.position.z + (b.position.z - a.position.z) * t,
      },
      rotation: {
        x: a.rotation.x + (b.rotation.x - a.rotation.x) * t,
        y: a.rotation.y + (b.rotation.y - a.rotation.y) * t,
        z: a.rotation.z + (b.rotation.z - a.rotation.z) * t,
      },
      velocity: {
        x: a.velocity.x + (b.velocity.x - a.velocity.x) * t,
        y: a.velocity.y + (b.velocity.y - a.velocity.y) * t,
        z: a.velocity.z + (b.velocity.z - a.velocity.z) * t,
      },
      timestamp: Date.now(),
    };
  }
}
