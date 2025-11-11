/**
 * Score display component for showing analysis scores.
 */

import React from 'react';

interface ScoreDisplayProps {
  label: string;
  score: number;
  maxScore?: number;
}

export const ScoreDisplay: React.FC<ScoreDisplayProps> = ({
  label,
  score,
  maxScore = 100
}) => {
  const percentage = (score / maxScore) * 100;
  const getColor = (pct: number) => {
    if (pct >= 80) return '#4caf50';
    if (pct >= 60) return '#ff9800';
    return '#f44336';
  };

  const color = getColor(percentage);

  return (
    <div style={{ marginBottom: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
        <span style={{ fontWeight: 'bold' }}>{label}</span>
        <span style={{ color }}>{score.toFixed(1)} / {maxScore}</span>
      </div>
      <div style={{
        width: '100%',
        height: '10px',
        backgroundColor: '#e0e0e0',
        borderRadius: '5px',
        overflow: 'hidden'
      }}>
        <div style={{
          width: `${percentage}%`,
          height: '100%',
          backgroundColor: color,
          transition: 'width 0.3s ease'
        }} />
      </div>
    </div>
  );
};
