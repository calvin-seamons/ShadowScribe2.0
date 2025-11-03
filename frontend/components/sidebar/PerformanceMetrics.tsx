/**
 * Displays performance metrics with timing breakdown
 */
'use client';

import { PerformanceMetrics as PerformanceMetricsType } from '@/lib/types/metadata';
import { Clock } from 'lucide-react';

interface PerformanceMetricsProps {
  performance: PerformanceMetricsType;
}

export function PerformanceMetrics({ performance }: PerformanceMetricsProps) {
  const timing = performance.timing || {};
  
  const metrics = [
    { label: 'Routing & Entities', value: timing.routing_and_entities, color: 'bg-blue-500' },
    { label: 'Entity Resolution', value: timing.entity_resolution, color: 'bg-purple-500' },
    { label: 'RAG Queries', value: timing.rag_queries, color: 'bg-green-500' },
    { label: 'Response Generation', value: timing.response_generation, color: 'bg-orange-500' },
  ].filter(m => m.value !== undefined);

  const total = timing.total || 0;
  const maxValue = Math.max(...metrics.map(m => m.value || 0));

  return (
    <div className="space-y-4">
      {metrics.length > 0 ? (
        <>
          <div className="space-y-3">
            {metrics.map((metric, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">{metric.label}</span>
                  <span className="font-medium">{metric.value?.toFixed(0)}ms</span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className={`h-full ${metric.color} transition-all duration-300`}
                    style={{ width: `${((metric.value || 0) / maxValue) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          {total > 0 && (
            <div className="pt-3 border-t border-border">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-muted-foreground" />
                  <span className="text-sm font-medium">Total Time</span>
                </div>
                <span className="text-sm font-bold">{total.toFixed(0)}ms</span>
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="text-sm text-muted-foreground">No timing data available</div>
      )}
    </div>
  );
}
