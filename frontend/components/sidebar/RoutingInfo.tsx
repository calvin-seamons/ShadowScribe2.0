/**
 * Displays routing information (tools selected and intentions)
 */
'use client';

import { RoutingMetadata } from '@/lib/types/metadata';
import { Database, Book, ScrollText } from 'lucide-react';

interface RoutingInfoProps {
  routing: RoutingMetadata;
}

export function RoutingInfo({ routing }: RoutingInfoProps) {
  const toolIcons = {
    character_data: Database,
    rulebook: Book,
    session_notes: ScrollText,
  };

  const toolColors = {
    character_data: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
    rulebook: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300',
    session_notes: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
  };

  return (
    <div className="space-y-3">
      {routing.tools_needed.map((tool, idx) => {
        const Icon = toolIcons[tool.tool as keyof typeof toolIcons] || Database;
        const colorClass = toolColors[tool.tool as keyof typeof toolColors] || 'bg-gray-100 text-gray-700';

        return (
          <div key={idx} className="space-y-2">
            <div className="flex items-center gap-2">
              <div className={`p-1.5 rounded ${colorClass}`}>
                <Icon className="w-4 h-4" />
              </div>
              <span className="text-sm font-medium capitalize">
                {tool.tool.replace('_', ' ')}
              </span>
            </div>
            
            <div className="ml-9 space-y-1">
              <div className="text-xs text-muted-foreground">
                <span className="font-medium">Intention:</span> {tool.intention}
              </div>
              
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-muted rounded-full h-1.5">
                  <div
                    className={`h-full rounded-full ${colorClass.split(' ')[0]}`}
                    style={{ width: `${tool.confidence * 100}%` }}
                  />
                </div>
                <span className="text-xs text-muted-foreground">
                  {(tool.confidence * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
