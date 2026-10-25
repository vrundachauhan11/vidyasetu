import React from 'react';

interface MockBadgeProps {
  label?: string;
  size?: 'sm' | 'md';
}

export const MockBadge: React.FC<MockBadgeProps> = ({ label = 'SIMULATED MOCK', size = 'sm' }) => {
  const isSm = size === 'sm';
  return (
    <span
      className={`inline-flex items-center gap-1 font-mono font-medium uppercase tracking-wider rounded border ${
        isSm ? 'px-1.5 py-0.5 text-[10px]' : 'px-2 py-1 text-xs'
      } bg-amber-50 text-amber-800 border-amber-300/80`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
      {label}
    </span>
  );
};
