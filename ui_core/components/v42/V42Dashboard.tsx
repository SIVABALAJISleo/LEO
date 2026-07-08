import React from 'react';
import { SwarmTelemetryCard } from './SwarmTelemetryCard';
import { InfiniteCacheCard } from './InfiniteCacheCard';
import { WebGPUInferenceCard } from './WebGPUInferenceCard';

export const V42Dashboard: React.FC = () => {
  return (
    <div style={{
      width: '100%',
      minHeight: '100vh',
      background: '#0a0a0f',
      padding: '40px 24px',
      color: '#fff',
      fontFamily: '"Inter", sans-serif',
      display: 'flex',
      flexDirection: 'column',
      gap: '32px',
      boxSizing: 'border-box'
    }}>
      <div style={{ textAlign: 'center', marginBottom: '16px' }}>
        <h1 style={{ 
          fontSize: '2.5rem', 
          fontWeight: 800, 
          margin: 0,
          background: 'linear-gradient(90deg, #00d2ff, #bb00ff)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          letterSpacing: '-1px'
        }}>
          LEO V42 "The Irrelevance Engine"
        </h1>
        <p style={{ color: '#888', fontSize: '1.1rem', maxWidth: '600px', margin: '16px auto 0' }}>
          Real-time visualization of the Swarm Distillation Protocol, Infinite Cache Layer, and Local WebGPU Inference stack.
        </p>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))',
        gap: '24px',
        maxWidth: '1400px',
        margin: '0 auto',
        width: '100%'
      }}>
        {/* Swarm & Distillation Visualizer */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <SwarmTelemetryCard />
        </div>

        {/* Cache & Compute Avoidance Visualizer */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <InfiniteCacheCard />
        </div>

        {/* Local WebGPU & Speculative Decoding Visualizer */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <WebGPUInferenceCard />
        </div>
      </div>
    </div>
  );
};
