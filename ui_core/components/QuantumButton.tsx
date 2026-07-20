import React from 'react';
import { nvidiaTokens } from '../design_system/nvidiaTokens';

export interface QuantumButtonProps {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'small' | 'medium' | 'large';
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  className?: string;
}

export const QuantumButton: React.FC<QuantumButtonProps> = ({
  variant = 'primary',
  size = 'medium',
  children,
  onClick,
  disabled,
  className = '',
}) => {
  const getPadding = () => {
    switch (size) {
      case 'small':
        return '0.5rem 1rem';
      case 'large':
        return '1rem 2rem';
      default:
        return '0.75rem 1.5rem';
    }
  };

  const getFontSize = () => {
    switch (size) {
      case 'small':
        return nvidiaTokens.typography.fontSize.sm;
      case 'large':
        return nvidiaTokens.typography.fontSize.lg;
      default:
        return nvidiaTokens.typography.fontSize.base;
    }
  };

  const getVariantStyles = (): React.CSSProperties => {
    switch (variant) {
      case 'secondary':
        return {
          background: 'transparent',
          color: nvidiaTokens.colors.accent.nvidiaGreen,
          border: `1px solid ${nvidiaTokens.colors.accent.nvidiaGreen}`,
        };
      case 'ghost':
        return {
          background: 'transparent',
          color: nvidiaTokens.colors.primary.white,
          border: '1px solid rgba(255, 255, 255, 0.1)',
        };
      default:
        return {
          background: nvidiaTokens.colors.accent.nvidiaGreen,
          color: nvidiaTokens.colors.primary.black,
          border: 'none',
          boxShadow: nvidiaTokens.shadows.glow,
        };
    }
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`relative inline-flex items-center justify-center gap-2 font-semibold transition-all duration-300 rounded cursor-pointer overflow-hidden uppercase tracking-wider ${className}`}
      style={{
        padding: getPadding(),
        fontSize: getFontSize(),
        fontFamily: nvidiaTokens.typography.fontFamily.primary,
        fontWeight: nvidiaTokens.typography.fontWeight.bold,
        opacity: disabled ? 0.5 : 1,
        pointerEvents: disabled ? 'none' : 'auto',
        ...getVariantStyles(),
      }}
    >
      <span className="relative z-10 flex items-center gap-2">{children}</span>
    </button>
  );
};
