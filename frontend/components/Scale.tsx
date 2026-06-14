export function Scale({ className = "" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 400 500"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden
    >
      <defs>
        <linearGradient id="wood" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#7a4a22" />
          <stop offset="50%" stopColor="#a06a32" />
          <stop offset="100%" stopColor="#6d3f1d" />
        </linearGradient>
        <linearGradient id="woodV" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#8a5526" />
          <stop offset="100%" stopColor="#5b3517" />
        </linearGradient>
        <radialGradient id="ball" cx="0.35" cy="0.3">
          <stop offset="0%" stopColor="#c25744" />
          <stop offset="100%" stopColor="#7a2616" />
        </radialGradient>
        <radialGradient id="dark" cx="0.35" cy="0.3">
          <stop offset="0%" stopColor="#7a4a22" />
          <stop offset="100%" stopColor="#3a1f0c" />
        </radialGradient>
      </defs>

      {/* base */}
      <ellipse cx="200" cy="475" rx="80" ry="8" fill="#2a1a0c" opacity="0.4" />
      <rect x="140" y="455" width="120" height="18" rx="3" fill="url(#woodV)" />
      <rect x="155" y="448" width="90" height="10" rx="2" fill="url(#wood)" />

      {/* post */}
      <rect x="195" y="80" width="10" height="370" fill="url(#woodV)" />

      {/* top finial */}
      <circle cx="200" cy="78" r="9" fill="url(#wood)" />
      <circle cx="200" cy="78" r="4" fill="#3a1f0c" />

      {/* beam */}
      <path
        d="M 60 95 Q 200 60 340 95 L 340 105 Q 200 70 60 105 Z"
        fill="url(#wood)"
      />

      {/* chains */}
      <line x1="75" y1="98" x2="100" y2="240" stroke="#2a1a0c" strokeWidth="1.5" />
      <line x1="95" y1="98" x2="100" y2="240" stroke="#2a1a0c" strokeWidth="1.5" />
      <line x1="305" y1="98" x2="300" y2="240" stroke="#2a1a0c" strokeWidth="1.5" />
      <line x1="325" y1="98" x2="300" y2="240" stroke="#2a1a0c" strokeWidth="1.5" />

      {/* left pan */}
      <ellipse cx="100" cy="245" rx="65" ry="8" fill="#3a1f0c" />
      <path
        d="M 35 245 Q 100 295 165 245"
        fill="url(#wood)"
        stroke="#3a1f0c"
        strokeWidth="1"
      />
      <ellipse cx="100" cy="245" rx="60" ry="6" fill="#5b3517" opacity="0.4" />

      {/* right pan */}
      <ellipse cx="300" cy="245" rx="65" ry="8" fill="#3a1f0c" />
      <path
        d="M 235 245 Q 300 295 365 245"
        fill="url(#wood)"
        stroke="#3a1f0c"
        strokeWidth="1"
      />
      <ellipse cx="300" cy="245" rx="60" ry="6" fill="#5b3517" opacity="0.4" />

      {/* ball on left pan (the question) */}
      <circle cx="100" cy="232" r="22" fill="url(#ball)" />
      <ellipse cx="92" cy="224" rx="6" ry="3" fill="#e89784" opacity="0.6" />

      {/* three balls on right pan (the cited clauses) */}
      <circle cx="278" cy="232" r="14" fill="url(#dark)" />
      <circle cx="300" cy="228" r="14" fill="url(#dark)" />
      <circle cx="322" cy="232" r="14" fill="url(#dark)" />
      <ellipse cx="274" cy="226" rx="3" ry="2" fill="#c08a4a" opacity="0.5" />
      <ellipse cx="296" cy="222" rx="3" ry="2" fill="#c08a4a" opacity="0.5" />
      <ellipse cx="318" cy="226" rx="3" ry="2" fill="#c08a4a" opacity="0.5" />
    </svg>
  );
}
