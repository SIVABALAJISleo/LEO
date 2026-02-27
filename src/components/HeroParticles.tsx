import { useEffect, useState, useRef } from "react";

interface Particle {
  id: number;
  x: number;
  y: number;
  baseX: number;
  baseY: number;
  size: number;
  duration: number;
  delay: number;
  opacity: number;
  velocityX: number;
  velocityY: number;
}

type ExplosionType = 'radial' | 'spiral' | 'wave';

export const HeroParticles = () => {
  const [particles, setParticles] = useState<Particle[]>([]);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isMouseDown, setIsMouseDown] = useState(false);
  const [explosionPoint, setExplosionPoint] = useState<{ x: number; y: number; time: number; type: ExplosionType } | null>(null);
  const [explosionRings, setExplosionRings] = useState<Array<{ id: number; x: number; y: number; time: number; type: ExplosionType }>>([]);
  const [explosionType, setExplosionType] = useState<ExplosionType>('radial');
  const containerRef = useRef<HTMLDivElement>(null);
  const animationRef = useRef<number>();

  useEffect(() => {
    // Generate random particles - increased count for denser network
    const newParticles: Particle[] = Array.from({ length: 60 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      baseX: Math.random() * 100,
      baseY: Math.random() * 100,
      size: Math.random() * 4 + 2,
      duration: Math.random() * 10 + 15,
      delay: Math.random() * 5,
      opacity: Math.random() * 0.5 + 0.3,
      velocityX: 0,
      velocityY: 0,
    }));
    setParticles(newParticles);
  }, []);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;
      setMousePosition({ x, y });
    };

    const handleMouseDown = () => setIsMouseDown(true);
    const handleMouseUp = () => setIsMouseDown(false);
    
    const handleDoubleClick = (e: MouseEvent) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;
      
      // Cycle through explosion types
      const types: ExplosionType[] = ['radial', 'spiral', 'wave'];
      const currentIndex = types.indexOf(explosionType);
      const nextType = types[(currentIndex + 1) % types.length];
      setExplosionType(nextType);
      
      setExplosionPoint({ x, y, time: Date.now(), type: nextType });
      
      // Add explosion rings for visual effect
      const ringId = Date.now();
      setExplosionRings(prev => [...prev, { id: ringId, x, y, time: Date.now(), type: nextType }]);
      
      // Remove ring after animation
      setTimeout(() => {
        setExplosionRings(prev => prev.filter(ring => ring.id !== ringId));
      }, 1000);
    };

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mousedown", handleMouseDown);
    window.addEventListener("mouseup", handleMouseUp);
    window.addEventListener("dblclick", handleDoubleClick);
    
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mousedown", handleMouseDown);
      window.removeEventListener("mouseup", handleMouseUp);
      window.removeEventListener("dblclick", handleDoubleClick);
    };
  }, []);

  useEffect(() => {
    const animate = () => {
      setParticles((prevParticles) =>
        prevParticles.map((particle) => {
          // Check for explosion effect
          if (explosionPoint && Date.now() - explosionPoint.time < 800) {
            const dx = particle.x - explosionPoint.x;
            const dy = particle.y - explosionPoint.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            const explosionRadius = 50;
            
            if (distance < explosionRadius) {
              const force = (explosionRadius - distance) / explosionRadius;
              const angle = Math.atan2(dy, dx);
              const timeProgress = (Date.now() - explosionPoint.time) / 800;
              
              let pushX = 0;
              let pushY = 0;
              
              switch (explosionPoint.type) {
                case 'radial':
                  // Strong outward burst
                  const radialStrength = 10;
                  pushX = Math.cos(angle) * force * radialStrength;
                  pushY = Math.sin(angle) * force * radialStrength;
                  break;
                  
                case 'spiral':
                  // Spiral outward with rotation
                  const spiralStrength = 7;
                  const rotationSpeed = 5;
                  const spiralAngle = angle + timeProgress * rotationSpeed;
                  pushX = Math.cos(spiralAngle) * force * spiralStrength;
                  pushY = Math.sin(spiralAngle) * force * spiralStrength;
                  break;
                  
                case 'wave':
                  // Wave ripple effect - particles move in waves
                  const waveStrength = 6;
                  const waveFrequency = 3;
                  const waveFactor = Math.sin(distance * waveFrequency - timeProgress * 10);
                  pushX = Math.cos(angle) * force * waveStrength * waveFactor;
                  pushY = Math.sin(angle) * force * waveStrength * waveFactor;
                  break;
              }
              
              return {
                ...particle,
                velocityX: pushX,
                velocityY: pushY,
                x: particle.x + pushX,
                y: particle.y + pushY,
              };
            }
          }
          
          const dx = mousePosition.x - particle.x;
          const dy = mousePosition.y - particle.y;
          const distance = Math.sqrt(dx * dx + dy * dy);
          const maxDistance = isMouseDown ? 40 : 20; // Larger radius when attracting

          if (isMouseDown && distance < maxDistance && distance > 0) {
            // Attract particles towards cursor when mouse is held down
            const force = (maxDistance - distance) / maxDistance;
            const angle = Math.atan2(dy, dx);
            const pullX = Math.cos(angle) * force * 3;
            const pullY = Math.sin(angle) * force * 3;

            return {
              ...particle,
              velocityX: pullX,
              velocityY: pullY,
              x: particle.x + pullX,
              y: particle.y + pullY,
            };
          } else if (!isMouseDown && distance < maxDistance && distance > 0) {
            // Repel particles from cursor on hover
            const force = (maxDistance - distance) / maxDistance;
            const angle = Math.atan2(dy, dx);
            const pushX = -Math.cos(angle) * force * 2;
            const pushY = -Math.sin(angle) * force * 2;

            return {
              ...particle,
              velocityX: pushX,
              velocityY: pushY,
              x: particle.x + pushX,
              y: particle.y + pushY,
            };
          } else {
            // Return to base position smoothly
            const returnForce = 0.05;
            const toBaseX = (particle.baseX - particle.x) * returnForce;
            const toBaseY = (particle.baseY - particle.y) * returnForce;

            return {
              ...particle,
              velocityX: toBaseX,
              velocityY: toBaseY,
              x: particle.x + toBaseX,
              y: particle.y + toBaseY,
            };
          }
        })
      );

      animationRef.current = requestAnimationFrame(animate);
    };

    animationRef.current = requestAnimationFrame(animate);
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [mousePosition, isMouseDown, explosionPoint]);

  // Calculate particle connections for neural network effect
  const connectionDistance = 25; // Maximum distance to draw connections
  const connections: Array<{ x1: number; y1: number; x2: number; y2: number; opacity: number }> = [];
  const particleConnectionCount = new Map<number, number>();
  
  particles.forEach((particle, i) => {
    let connectionCount = 0;
    particles.slice(i + 1).forEach((otherParticle) => {
      const dx = particle.x - otherParticle.x;
      const dy = particle.y - otherParticle.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      
      if (distance < connectionDistance) {
        connectionCount++;
        // Opacity based on distance - closer particles have more visible connections
        const opacity = (1 - distance / connectionDistance) * 0.3;
        connections.push({
          x1: particle.x,
          y1: particle.y,
          x2: otherParticle.x,
          y2: otherParticle.y,
          opacity,
        });
      }
    });
    particleConnectionCount.set(particle.id, connectionCount);
  });
  
  // Helper function to get particle color based on velocity and connections
  const getParticleColor = (particle: Particle) => {
    const velocity = Math.abs(particle.velocityX) + Math.abs(particle.velocityY);
    const connections = particleConnectionCount.get(particle.id) || 0;
    
    // High velocity or many connections = warmer colors (towards red/orange)
    // Low velocity and few connections = cooler colors (towards blue/cyan)
    const intensity = Math.min(velocity * 5 + connections * 0.5, 1);
    
    // Interpolate between primary (base) and accent colors based on intensity
    if (intensity > 0.6) {
      return 'hsl(var(--accent))'; // High activity - accent color
    } else if (intensity > 0.3) {
      return 'hsl(var(--primary))'; // Medium activity - primary color
    } else {
      return 'hsl(var(--primary) / 0.7)'; // Low activity - muted primary
    }
  };

  return (
    <div ref={containerRef} className="absolute inset-0 overflow-hidden">
      {/* Neural network connection lines */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none">
        <defs>
          {connections.map((_, i) => (
            <linearGradient key={`gradient-${i}`} id={`flow-gradient-${i}`} gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity="0">
                <animate
                  attributeName="offset"
                  values="0;1;1;0"
                  dur="3s"
                  repeatCount="indefinite"
                  begin={`${(i * 0.1) % 3}s`}
                />
              </stop>
              <stop offset="30%" stopColor="hsl(var(--primary))" stopOpacity="0.8">
                <animate
                  attributeName="offset"
                  values="0.3;1;1;0.3"
                  dur="3s"
                  repeatCount="indefinite"
                  begin={`${(i * 0.1) % 3}s`}
                />
              </stop>
              <stop offset="60%" stopColor="hsl(var(--accent))" stopOpacity="0.6">
                <animate
                  attributeName="offset"
                  values="0.6;1;1;0.6"
                  dur="3s"
                  repeatCount="indefinite"
                  begin={`${(i * 0.1) % 3}s`}
                />
              </stop>
              <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity="0">
                <animate
                  attributeName="offset"
                  values="1;1;1;1"
                  dur="3s"
                  repeatCount="indefinite"
                  begin={`${(i * 0.1) % 3}s`}
                />
              </stop>
            </linearGradient>
          ))}
        </defs>
        {connections.map((connection, i) => (
          <line
            key={i}
            x1={`${connection.x1}%`}
            y1={`${connection.y1}%`}
            x2={`${connection.x2}%`}
            y2={`${connection.y2}%`}
            stroke={`url(#flow-gradient-${i})`}
            strokeWidth="1.5"
            opacity={connection.opacity}
          />
        ))}
      </svg>
      
      {/* Explosion rings */}
      {explosionRings.map((ring) => {
        const ringClass = ring.type === 'spiral' ? 'explosion-ring-spiral' : 
                         ring.type === 'wave' ? 'explosion-ring-wave' : 
                         'explosion-ring';
        return (
          <div
            key={ring.id}
            className="absolute rounded-full border-2 pointer-events-none"
            style={{
              left: `${ring.x}%`,
              top: `${ring.y}%`,
              width: '20px',
              height: '20px',
              transform: 'translate(-50%, -50%)',
              animation: `${ringClass} 1s ease-out forwards`,
              borderColor: ring.type === 'spiral' ? 'hsl(var(--accent))' : 
                          ring.type === 'wave' ? 'hsl(var(--primary))' :
                          'hsl(var(--primary))',
              boxShadow: `0 0 20px ${ring.type === 'spiral' ? 'hsl(var(--accent) / 0.8)' : 
                                     ring.type === 'wave' ? 'hsl(var(--primary) / 0.6)' :
                                     'hsl(var(--primary) / 0.8)'}`,
            }}
          />
        );
      })}
      
      {/* Explosion type indicator */}
      <div className="absolute top-4 left-4 px-4 py-2 rounded-lg bg-background/80 backdrop-blur-sm border border-border pointer-events-none">
        <p className="text-xs text-muted-foreground mb-1">Double-click explosion:</p>
        <p className="text-sm font-medium text-foreground capitalize">{explosionType}</p>
      </div>
      
      {/* Cursor indicator when mouse is held down */}
      {isMouseDown && (
        <div
          className="absolute rounded-full border-2 border-primary pointer-events-none animate-pulse"
          style={{
            left: `${mousePosition.x}%`,
            top: `${mousePosition.y}%`,
            width: '80px',
            height: '80px',
            transform: 'translate(-50%, -50%)',
            boxShadow: '0 0 30px hsl(var(--primary) / 0.5)',
          }}
        />
      )}
      {particles.map((particle) => {
        const particleColor = getParticleColor(particle);
        return (
          <div
            key={particle.id}
            className="absolute rounded-full transition-all duration-200"
            style={{
              left: `${particle.x}%`,
              top: `${particle.y}%`,
              width: `${particle.size}px`,
              height: `${particle.size}px`,
              opacity: isMouseDown ? particle.opacity * 1.5 : particle.opacity,
              backgroundColor: particleColor,
              boxShadow: `0 0 ${particle.size * (isMouseDown ? 5 : 3)}px ${particleColor}`,
              transform: `translate(-50%, -50%) scale(${1 + Math.abs(particle.velocityX + particle.velocityY) * 0.5})`,
            }}
          />
        );
      })}
      
      {/* Floating geometric shapes */}
      <div className="absolute top-20 left-10 w-16 h-16 border-2 border-primary/30 rotate-45 animate-float" style={{ animationDuration: "8s" }} />
      <div className="absolute top-40 right-20 w-20 h-20 border-2 border-primary/20 animate-float" style={{ animationDuration: "12s", animationDelay: "2s" }} />
      <div className="absolute bottom-32 left-1/4 w-12 h-12 border-2 border-primary/25 rotate-12 animate-float" style={{ animationDuration: "10s", animationDelay: "1s" }} />
      <div className="absolute top-1/3 right-1/3 w-8 h-8 bg-primary/10 rounded-full animate-float" style={{ animationDuration: "15s", animationDelay: "3s" }} />
      
      {/* Circuit-like connecting lines */}
      <svg className="absolute inset-0 w-full h-full opacity-20">
        <defs>
          <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity="0" />
            <stop offset="50%" stopColor="hsl(var(--primary))" stopOpacity="0.5" />
            <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity="0" />
          </linearGradient>
        </defs>
        <line x1="10%" y1="20%" x2="90%" y2="30%" stroke="url(#lineGradient)" strokeWidth="1" className="animate-pulse" />
        <line x1="20%" y1="80%" x2="80%" y2="70%" stroke="url(#lineGradient)" strokeWidth="1" className="animate-pulse" style={{ animationDelay: "1s" }} />
        <line x1="5%" y1="50%" x2="30%" y2="60%" stroke="url(#lineGradient)" strokeWidth="1" className="animate-pulse" style={{ animationDelay: "2s" }} />
      </svg>
    </div>
  );
};
