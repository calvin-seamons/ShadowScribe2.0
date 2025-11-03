/**
 * ShadowScribe Logo - Quill pen with shadow effect
 */
'use client';

interface LogoProps {
  size?: number;
  className?: string;
}

export function Logo({ size = 40, className = '' }: LogoProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Shadow effect */}
      <g opacity="0.3">
        <path
          d="M60 82 L45 95 L30 82 L35 45 L50 10 L65 45 Z"
          fill="currentColor"
          transform="translate(3, 3)"
        />
      </g>
      
      {/* Quill feather */}
      <path
        d="M60 82 L45 95 L30 82 L35 45 L50 10 L65 45 Z"
        fill="hsl(45 100% 51%)"
        stroke="hsl(270 50% 15%)"
        strokeWidth="2"
      />
      
      {/* Feather barbs */}
      <path
        d="M40 30 L35 40 M42 38 L37 48 M44 46 L39 56 M46 54 L41 64 M48 62 L43 72"
        stroke="hsl(270 50% 15%)"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <path
        d="M60 30 L65 40 M58 38 L63 48 M56 46 L61 56 M54 54 L59 64 M52 62 L57 72"
        stroke="hsl(270 50% 15%)"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      
      {/* Quill tip */}
      <path
        d="M45 90 L50 95 L55 90"
        fill="hsl(270 50% 15%)"
        stroke="hsl(270 50% 15%)"
        strokeWidth="2"
        strokeLinejoin="round"
      />
    </svg>
  );
}

interface LogoTextProps {
  className?: string;
}

export function LogoText({ className = '' }: LogoTextProps) {
  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <Logo size={48} />
      <div className="flex flex-col">
        <span className="text-2xl font-bold tracking-tight bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
          ShadowScribe
        </span>
        <span className="text-xs text-muted-foreground tracking-wider uppercase">
          D&D Companion
        </span>
      </div>
    </div>
  );
}
