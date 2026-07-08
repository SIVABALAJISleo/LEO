import React, { useEffect, useState } from 'react';
import { MambaHybridEngine, MambaTelemetry, SpeculativeMode } from '../../src/v40/engines/mambaHybridEngine';
import { localInferenceRunner } from '../../src/v40/wasm/local_inference';

const mambaEngine = new MambaHybridEngine();

export const WebGPUInferenceCard: React.FC = () => {
  const [hybridRatio, setHybridRatio] = useState<number>(0.5);
  const [specMode, setSpecMode] = useState<SpeculativeMode>("PEARL");
  const [metrics, setMetrics] = useState<MambaTelemetry | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedText, setGeneratedText] = useState("");

  // Update telemetry when sliders change
  useEffect(() => {
    mambaEngine.setHybridRatio(hybridRatio);
    mambaEngine.setSpeculativeMode(specMode);
    
    mambaEngine.projectScalingMetrics().then(data => {
      setMetrics(data);
    });
  }, [hybridRatio, specMode]);

  const handleSimulate = async () => {
    setIsGenerating(true);
    setGeneratedText("");
    
    try {
      await localInferenceRunner.generateStreaming("Explain quantum optimization", (token) => {
        setGeneratedText(prev => prev + token);
      });
    } catch (e) {
      console.error(e);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div style={{
      background: 'rgba(30, 20, 40, 0.65)',
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
      gap: '20px',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Decorative Glow */}
      <div style={{
        position: 'absolute',
        bottom: '-50px',
        right: '-50px',
        width: '200px',
        height: '200px',
        background: 'radial-gradient(circle, rgba(187, 0, 255, 0.15) 0%, transparent 70%)',
        filter: 'blur(20px)',
        zIndex: 0
      }}></div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', zIndex: 1 }}>
        <h2 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 600, letterSpacing: '0.5px' }}>
          WebGPU Offline Inference
        </h2>
        <span style={{ 
          background: 'rgba(255,255,255,0.1)', 
          padding: '4px 8px', 
          borderRadius: '6px', 
          fontSize: '0.75rem',
          border: '1px solid rgba(255,255,255,0.2)'
        }}>
          BitNet 1.58b + Mamba
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', zIndex: 1 }}>
        {/* Controls */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: '#ccc' }}>
            <span>Hybrid Ratio (Transformer ↔ Mamba)</span>
            <span>{Math.round(hybridRatio * 100)}% Mamba</span>
          </div>
          <input 
            type="range" 
            min="0" max="1" step="0.1" 
            value={hybridRatio}
            onChange={(e) => setHybridRatio(parseFloat(e.target.value))}
            style={{ width: '100%', cursor: 'pointer', accentColor: '#bb00ff' }}
          />
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <span style={{ fontSize: '0.85rem', color: '#ccc' }}>Speculative Decoding Mode</span>
          <div style={{ display: 'flex', gap: '8px' }}>
            {['OFF', 'EAGLE-3', 'PEARL'].map(mode => (
              <button 
                key={mode}
                onClick={() => setSpecMode(mode as SpeculativeMode)}
                style={{
                  flex: 1,
                  background: specMode === mode ? 'rgba(187, 0, 255, 0.3)' : 'rgba(255,255,255,0.05)',
                  border: specMode === mode ? '1px solid #bb00ff' : '1px solid rgba(255,255,255,0.1)',
                  color: specMode === mode ? '#fff' : '#aaa',
                  padding: '8px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: specMode === mode ? 600 : 400,
                  transition: 'all 0.2s ease'
                }}
              >
                {mode}
              </button>
            ))}
          </div>
        </div>

        {/* Live Metrics */}
        {metrics && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginTop: '8px' }}>
            <div style={{ background: 'rgba(0,0,0,0.2)', padding: '12px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
              <div style={{ fontSize: '0.7rem', color: '#888', textTransform: 'uppercase' }}>Speed</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#00d2ff' }}>{metrics.tokensPerSec.toFixed(1)} <span style={{fontSize:'0.8rem', color:'#aaa'}}>t/s</span></div>
            </div>
            <div style={{ background: 'rgba(0,0,0,0.2)', padding: '12px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
              <div style={{ fontSize: '0.7rem', color: '#888', textTransform: 'uppercase' }}>Complexity vs Attn</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#00ff88' }}>{metrics.speedupVsTransformer.toFixed(1)}x <span style={{fontSize:'0.8rem', color:'#aaa'}}>faster</span></div>
            </div>
          </div>
        )}

        {/* Demo Output */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '4px' }}>
          <button 
            onClick={handleSimulate} 
            disabled={isGenerating}
            style={{
              background: 'linear-gradient(90deg, #bb00ff, #3a7bd5)',
              border: 'none',
              color: '#fff',
              padding: '12px',
              borderRadius: '8px',
              cursor: isGenerating ? 'not-allowed' : 'pointer',
              fontWeight: 600,
              opacity: isGenerating ? 0.7 : 1
            }}
          >
            {isGenerating ? 'Generating...' : 'Run WebGPU Inference'}
          </button>
          
          <div style={{ 
            minHeight: '60px', 
            background: 'rgba(0,0,0,0.4)', 
            padding: '12px', 
            borderRadius: '8px',
            border: '1px solid rgba(255,255,255,0.05)',
            fontSize: '0.9rem',
            lineHeight: '1.5',
            color: '#ddd'
          }}>
            {generatedText || <span style={{ color: '#666', fontStyle: 'italic' }}>Output will appear here...</span>}
          </div>
        </div>
      </div>
    </div>
  );
};
