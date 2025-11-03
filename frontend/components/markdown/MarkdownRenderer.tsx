/**
 * Markdown renderer with syntax highlighting and D&D-specific formatting
 */
'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import rehypeRaw from 'rehype-raw';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export function MarkdownRenderer({ content, className = '' }: MarkdownRendererProps) {
  return (
    <ReactMarkdown
      className={`prose prose-sm max-w-none dark:prose-invert ${className}`}
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeHighlight, rehypeRaw]}
      components={{
        // Custom components for D&D-specific formatting
        h1: ({ node, ...props }) => <h1 className="text-2xl font-bold text-primary mb-4" {...props} />,
        h2: ({ node, ...props }) => <h2 className="text-xl font-semibold text-primary mb-3 mt-6" {...props} />,
        h3: ({ node, ...props }) => <h3 className="text-lg font-medium text-primary mb-2 mt-4" {...props} />,
        p: ({ node, ...props }) => <p className="mb-3 leading-relaxed" {...props} />,
        ul: ({ node, ...props }) => <ul className="list-disc list-inside mb-3 space-y-1" {...props} />,
        ol: ({ node, ...props }) => <ol className="list-decimal list-inside mb-3 space-y-1" {...props} />,
        li: ({ node, ...props }) => <li className="ml-2" {...props} />,
        code: ({ node, inline, ...props }: any) => 
          inline ? (
            <code className="px-1.5 py-0.5 bg-muted rounded text-sm font-mono" {...props} />
          ) : (
            <code className="block p-3 bg-muted rounded-lg overflow-x-auto font-mono text-sm" {...props} />
          ),
        pre: ({ node, ...props }) => (
          <pre className="bg-muted rounded-lg p-3 overflow-x-auto mb-3" {...props} />
        ),
        blockquote: ({ node, ...props }) => (
          <blockquote className="border-l-4 border-primary pl-4 italic text-muted-foreground my-3" {...props} />
        ),
        table: ({ node, ...props }) => (
          <div className="overflow-x-auto mb-3">
            <table className="min-w-full border-collapse border border-border" {...props} />
          </div>
        ),
        th: ({ node, ...props }) => (
          <th className="border border-border px-3 py-2 bg-muted font-semibold text-left" {...props} />
        ),
        td: ({ node, ...props }) => (
          <td className="border border-border px-3 py-2" {...props} />
        ),
        a: ({ node, ...props }) => (
          <a className="text-primary hover:underline" target="_blank" rel="noopener noreferrer" {...props} />
        ),
        strong: ({ node, ...props }) => <strong className="font-bold text-foreground" {...props} />,
        em: ({ node, ...props }) => <em className="italic" {...props} />,
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
