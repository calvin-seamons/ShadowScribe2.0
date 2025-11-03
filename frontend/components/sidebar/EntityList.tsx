/**
 * Displays extracted entities and where they were found
 */
'use client';

import { EntitiesMetadata } from '@/lib/types/metadata';
import { Tag } from 'lucide-react';

interface EntityListProps {
  entities: EntitiesMetadata;
}

export function EntityList({ entities }: EntityListProps) {
  if (!entities.entities || entities.entities.length === 0) {
    return <div className="text-sm text-muted-foreground">No entities extracted</div>;
  }

  return (
    <div className="space-y-3">
      {entities.entities.map((entity, idx) => (
        <div key={idx} className="space-y-2">
          <div className="flex items-start gap-2">
            <Tag className="w-4 h-4 mt-0.5 flex-shrink-0 text-primary" />
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium truncate">{entity.name}</div>
              
              {entity.found_in_sections && entity.found_in_sections.length > 0 && (
                <div className="mt-1 space-y-1">
                  {entity.found_in_sections.map((sections, secIdx) => (
                    <div key={secIdx} className="text-xs">
                      <span className="text-muted-foreground">Found in: </span>
                      <span className="text-foreground">
                        {sections.join(', ')}
                      </span>
                      {entity.match_confidence && entity.match_confidence[secIdx] && (
                        <span className="ml-2 text-muted-foreground">
                          ({(entity.match_confidence[secIdx] * 100).toFixed(0)}% match)
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              )}
              
              {entity.match_strategy && entity.match_strategy.length > 0 && (
                <div className="mt-1 text-xs text-muted-foreground">
                  Strategy: {entity.match_strategy[0]}
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
