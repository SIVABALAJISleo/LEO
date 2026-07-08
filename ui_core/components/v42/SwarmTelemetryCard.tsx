import React, { useEffect, useState } from 'react';
import { SelfImprovementEngine, SwarmTelemetry } from '../../src/v40/engines/selfImprovementEngine';

const swarmEngine = new SelfImprovementEngine();

export const SwarmTelemetryCard: React.FC = () => {
  const [telemetry, setTelemetry] = useState<SwarmTelemetry>(swarmEngine.swarmState);
  const [isActive, setIsActive] = useState(false);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isActive) {
      interval = setInterval(async () => {
        const data = await swarmEngine.fetchSwarmTelemetry();
        // Simulate local generation progress if active for demo
        setTelemetry(prev => ({
          ...data,
          localContributions: prev.localContributions + Math.floor(Math.random() * 3),
          vaccinesGenerated: prev.vaccinesGenerated + Math.floor(Math.random() * 2),
        }));
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [isActive]);

  const toggleSwarm = () => {
    const nextState = !isActive;
    setIsActive(nextState);
    swarmEngine.toggleSwarmTraining(nextState);
  };

  return (
    <div style={{
      background: 'rgba(20, 20, 30, 0.65)',
      backdropFilter: 'blur(16px)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: '20px',
      padding: '24px',
      color: '#fff',
      fontFamily: '"Inter", sans-serif',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
      transition: 'transform 0.3s ease',
      display: 'flex',
      flexDirection: 'column',
      gap: '16px',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Decorative Glow */}
      <div style={{
        position: 'absolute',
        top: '-50px',
        right: '-50px',
        width: '150px',
        height: '150px',
        background: isActive ? 'radial-gradient(circle, rgba(0, 255, 136, 0.2) 0%, transparent 70%)' : 'radial-gradient(circle, rgba(255, 0, 85, 0.2) 0%, transparent 70%)',
        filter: 'blur(20px)',
        zIndex: 0
      }}></div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', zIndex: 1 }}>
        <h2 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 600, letterSpacing: '0.5px' }}>
          Swarm Distillation Protocol
        </h2>
        <button 
          onClick={toggleSwarm}
          style={{
            background: isActive ? 'rgba(0, 255, 136, 0.15)' : 'rgba(255, 255, 255, 0.05)',
            border: isActive ? '1px solid rgba(0, 255, 136, 0.5)' : '1px solid rgba(255, 255, 255, 0.2)',
            color: isActive ? '#00ff88' : '#aaa',
            padding: '8px 16px',
            borderRadius: '12px',
            cursor: 'pointer',
            fontWeight: 600,
            transition: 'all 0.2s ease',
            outline: 'none'
          }}
        >
          {isActive ? '● Connected to Swarm' : '○ Join Swarm'}
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', zIndex: 1 }}>
        <StatBox label="Local Tensors Uploaded" value={telemetry.localContributions.toLocaleString()} color="#00d2ff" />
        <StatBox label="Global Model Version" value={`v42.${telemetry.globalModelVersion}`} color="#bb00ff" />
        <StatBox label="Vaccines Synthesized" value={telemetry.vaccinesGenerated.toLocaleString()} color="#ffaa00" />
        <StatBox label="Global Improvement" value={`+${telemetry.globalImprovementPercent.toFixed(2)}%`} color="#00ff88" />
      </div>

      <div style={{ zIndex: 1, marginTop: '8px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: '#aaa', marginBottom: '8px' }}>
          <span>Synthetic Data Factory Quota</span>
          <span>{(telemetry.syntheticGeneratedToday / telemetry.dailySyntheticQuota * 100).toFixed(1) || 0}%</span>
        </div>
        <div style={{ height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
          <div style={{ 
            height: '100%', 
            width: `${(telemetry.syntheticGeneratedToday / Math.max(telemetry.dailySyntheticQuota, 1)) * 100}%`, 
            background: 'linear-gradient(90deg, #00d2ff, #3a7bd5)',
            transition: 'width 1s ease-in-out'
          }}></div>
        </div>
      </div>
    </div>
  );
};

const StatBox: React.FC<{ label: string, value: string | number, color: string }> = ({ label, value, color }) => (
  <div style={{
    background: 'rgba(0,0,0,0.2)',
    borderRadius: '12px',
    padding: '16px',
    border: '1px solid rgba(255,255,255,0.05)',
    display: 'flex',
    flexDirection: 'column',
    gap: '4px'
  }}>
    <span style={{ fontSize: '0.8rem', color: '#888', textTransform: 'uppercase', letterSpacing: '1px' }}>{label}</span>
    <span style={{ fontSize: '1.5rem', fontWeight: 700, color, textShadow: `0 0 10px ${color}40` }}>{value}</span>
  </div>
);
