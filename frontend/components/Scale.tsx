export function Scale({ className = "" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 600 720"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden
    >
      <defs>
        <linearGradient id="woodH" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#4f2c12" />
          <stop offset="35%" stopColor="#9a5d2a" />
          <stop offset="50%" stopColor="#b3743a" />
          <stop offset="65%" stopColor="#9a5d2a" />
          <stop offset="100%" stopColor="#4f2c12" />
        </linearGradient>
        <linearGradient id="woodV" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#a06432" />
          <stop offset="40%" stopColor="#7a4720" />
          <stop offset="100%" stopColor="#4a2810" />
        </linearGradient>
        <linearGradient id="postShine" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#3a1f0c" />
          <stop offset="30%" stopColor="#7a4720" />
          <stop offset="50%" stopColor="#b3743a" />
          <stop offset="70%" stopColor="#7a4720" />
          <stop offset="100%" stopColor="#3a1f0c" />
        </linearGradient>
        <radialGradient id="bowl" cx="0.5" cy="0.25">
          <stop offset="0%" stopColor="#b3743a" />
          <stop offset="60%" stopColor="#7a4720" />
          <stop offset="100%" stopColor="#3a1f0c" />
        </radialGradient>
        <radialGradient id="redBall" cx="0.35" cy="0.3">
          <stop offset="0%" stopColor="#d56a52" />
          <stop offset="60%" stopColor="#a23a25" />
          <stop offset="100%" stopColor="#5e1808" />
        </radialGradient>
        <radialGradient id="darkBall" cx="0.35" cy="0.3">
          <stop offset="0%" stopColor="#8a552a" />
          <stop offset="60%" stopColor="#5e3514" />
          <stop offset="100%" stopColor="#2c1606" />
        </radialGradient>
        <radialGradient id="finial" cx="0.4" cy="0.3">
          <stop offset="0%" stopColor="#c08e57" />
          <stop offset="100%" stopColor="#5b3517" />
        </radialGradient>
      </defs>

      {/* ground shadow */}
      <ellipse cx="300" cy="700" rx="200" ry="9" fill="#1a1410" opacity="0.18" />

      {/* base: stepped pyramid */}
      <rect x="190" y="675" width="220" height="22" rx="2" fill="url(#woodV)" />
      <rect x="200" y="668" width="200" height="9" fill="#3a1f0c" opacity="0.4" />
      <rect x="210" y="655" width="180" height="22" rx="2" fill="url(#woodV)" />
      <rect x="218" y="648" width="164" height="9" fill="#3a1f0c" opacity="0.4" />
      <rect x="232" y="635" width="136" height="22" rx="2" fill="url(#woodV)" />
      <rect x="252" y="617" width="96" height="20" rx="3" fill="url(#woodV)" />

      {/* central post */}
      <rect x="287" y="170" width="26" height="450" fill="url(#postShine)" />
      <line x1="293" y1="170" x2="293" y2="620" stroke="#3a1f0c" strokeWidth="1" opacity="0.5" />
      <line x1="307" y1="170" x2="307" y2="620" stroke="#3a1f0c" strokeWidth="1" opacity="0.5" />

      {/* upper post collar */}
      <rect x="280" y="165" width="40" height="12" rx="2" fill="url(#woodV)" />
      <rect x="284" y="158" width="32" height="10" rx="2" fill="url(#woodV)" />

      {/* top finial */}
      <circle cx="300" cy="148" r="14" fill="url(#finial)" />
      <circle cx="296" cy="144" r="4" fill="#e9c694" opacity="0.7" />
      <path d="M 290 138 Q 300 122 310 138" fill="none" stroke="#5b3517" strokeWidth="2" />
      <circle cx="300" cy="122" r="5" fill="url(#finial)" />

      {/* beam: straight horizontal wooden bar with tapered ends. Balanced. */}
      <path
        d="
          M 90 135
          L 510 135
          Q 535 135 540 152
          Q 535 155 510 148
          L 90 148
          Q 65 155 60 152
          Q 65 135 90 135 Z
        "
        fill="url(#woodH)"
      />
      <path
        d="M 90 135 L 510 135 L 510 140 L 90 140 Z"
        fill="#3a1f0c"
        opacity="0.3"
      />

      {/* beam end finials, directly above each bowl */}
      <circle cx="120" cy="142" r="11" fill="url(#finial)" />
      <circle cx="117" cy="139" r="3" fill="#e9c694" opacity="0.6" />
      <circle cx="480" cy="142" r="11" fill="url(#finial)" />
      <circle cx="477" cy="139" r="3" fill="#e9c694" opacity="0.6" />

      {/* small ring hooks where chains attach (directly under finials) */}
      <circle cx="120" cy="160" r="4" fill="none" stroke="#2a1a0c" strokeWidth="1.5" />
      <circle cx="480" cy="160" r="4" fill="none" stroke="#2a1a0c" strokeWidth="1.5" />

      {/* left chains: three nearly vertical strands forming a slight cone to the bowl rim */}
      <line x1="120" y1="164" x2="80" y2="345" stroke="#2a1a0c" strokeWidth="1.5" />
      <line x1="120" y1="164" x2="120" y2="345" stroke="#2a1a0c" strokeWidth="1.5" />
      <line x1="120" y1="164" x2="160" y2="345" stroke="#2a1a0c" strokeWidth="1.5" />

      {/* right chains, mirrored */}
      <line x1="480" y1="164" x2="440" y2="345" stroke="#2a1a0c" strokeWidth="1.5" />
      <line x1="480" y1="164" x2="480" y2="345" stroke="#2a1a0c" strokeWidth="1.5" />
      <line x1="480" y1="164" x2="520" y2="345" stroke="#2a1a0c" strokeWidth="1.5" />

      {/* left bowl, centered directly under the left beam tip */}
      <ellipse cx="120" cy="350" rx="80" ry="10" fill="#2a1606" />
      <ellipse cx="120" cy="347" rx="78" ry="8" fill="url(#woodV)" />
      <path
        d="M 40 350 Q 120 440 200 350 Z"
        fill="url(#bowl)"
        stroke="#2a1606"
        strokeWidth="1"
      />
      <ellipse cx="120" cy="353" rx="75" ry="6" fill="#3a1f0c" opacity="0.4" />

      {/* right bowl, centered directly under the right beam tip */}
      <ellipse cx="480" cy="350" rx="80" ry="10" fill="#2a1606" />
      <ellipse cx="480" cy="347" rx="78" ry="8" fill="url(#woodV)" />
      <path
        d="M 400 350 Q 480 440 560 350 Z"
        fill="url(#bowl)"
        stroke="#2a1606"
        strokeWidth="1"
      />
      <ellipse cx="480" cy="353" rx="75" ry="6" fill="#3a1f0c" opacity="0.4" />

      {/* red ball on left bowl: the question */}
      <circle cx="120" cy="320" r="32" fill="url(#redBall)" />
      <ellipse cx="108" cy="308" rx="10" ry="5" fill="#f4a890" opacity="0.6" />

      {/* three darker balls on right bowl: the cited clauses */}
      <circle cx="445" cy="328" r="22" fill="url(#darkBall)" />
      <circle cx="480" cy="315" r="24" fill="url(#darkBall)" />
      <circle cx="519" cy="328" r="22" fill="url(#darkBall)" />
      <ellipse cx="438" cy="320" rx="5" ry="2.5" fill="#c08e57" opacity="0.5" />
      <ellipse cx="473" cy="307" rx="5" ry="2.5" fill="#c08e57" opacity="0.5" />
      <ellipse cx="512" cy="320" rx="5" ry="2.5" fill="#c08e57" opacity="0.5" />
    </svg>
  );
}
