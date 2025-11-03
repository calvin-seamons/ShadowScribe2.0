/**
 * Metadata sidebar displaying RAG pipeline information
 */
'use client';

import { useMetadataStore } from '@/lib/stores/metadataStore';
import { ChevronDown, ChevronRight, X } from 'lucide-react';
import { useState } from 'react';
import { RoutingInfo } from './RoutingInfo';
import { EntityList } from './EntityList';
import { ContextSources } from './ContextSources';
import { PerformanceMetrics } from './PerformanceMetrics';

export function MetadataSidebar() {
  const { currentMetadata, sidebarVisible, toggleSidebar } = useMetadataStore();
  const [expandedSections, setExpandedSections] = useState({
    routing: true,
    entities: true,
    sources: true,
    performance: true,
  });

  if (!sidebarVisible) {
    return null;
  }

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  return (
    <div className="w-96 border-l border-border bg-background p-4 overflow-y-auto">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold">Query Analysis</h2>
        <button
          onClick={toggleSidebar}
          className="p-1 hover:bg-muted rounded"
          aria-label="Close sidebar"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {!currentMetadata && (
        <div className="text-sm text-muted-foreground text-center py-8">
          Send a message to see query analysis
        </div>
      )}

      {currentMetadata && (
        <div className="space-y-4">
          {/* Routing Info */}
          {currentMetadata.routing && (
            <Section
              title="Tools & Intentions"
              expanded={expandedSections.routing}
              onToggle={() => toggleSection('routing')}
            >
              <RoutingInfo routing={currentMetadata.routing} />
            </Section>
          )}

          {/* Entities */}
          {currentMetadata.entities && (
            <Section
              title="Entities Extracted"
              expanded={expandedSections.entities}
              onToggle={() => toggleSection('entities')}
            >
              <EntityList entities={currentMetadata.entities} />
            </Section>
          )}

          {/* Context Sources */}
          {currentMetadata.sources && (
            <Section
              title="Context Sources"
              expanded={expandedSections.sources}
              onToggle={() => toggleSection('sources')}
            >
              <ContextSources sources={currentMetadata.sources} />
            </Section>
          )}

          {/* Performance */}
          {currentMetadata.performance && (
            <Section
              title="Performance"
              expanded={expandedSections.performance}
              onToggle={() => toggleSection('performance')}
            >
              <PerformanceMetrics performance={currentMetadata.performance} />
            </Section>
          )}
        </div>
      )}
    </div>
  );
}

interface SectionProps {
  title: string;
  expanded: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}

function Section({ title, expanded, onToggle, children }: SectionProps) {
  return (
    <div className="border border-border rounded-lg">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-3 hover:bg-muted/50 transition-colors"
      >
        <span className="font-medium text-sm">{title}</span>
        {expanded ? (
          <ChevronDown className="w-4 h-4" />
        ) : (
          <ChevronRight className="w-4 h-4" />
        )}
      </button>
      {expanded && <div className="p-3 pt-0 border-t border-border mt-2">{children}</div>}
    </div>
  );
}
