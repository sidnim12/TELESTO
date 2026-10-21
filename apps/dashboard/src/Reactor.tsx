export default function Reactor() {
  return (
    <div className="reactor-scene" aria-hidden="true">
      <div className="reactor-orbit orbit-one" />
      <div className="reactor-orbit orbit-two" />
      <svg viewBox="0 0 420 310" className="reactor-svg" fill="none">
        <defs>
          <linearGradient
            id="glass"
            x1="130"
            y1="60"
            x2="290"
            y2="240"
            gradientUnits="userSpaceOnUse"
          >
            <stop stopColor="#d8eaff" stopOpacity=".12" />
            <stop offset=".5" stopColor="#d8eaff" stopOpacity=".02" />
            <stop offset="1" stopColor="#d8eaff" stopOpacity=".13" />
          </linearGradient>
          <linearGradient
            id="fluid"
            x1="210"
            y1="120"
            x2="210"
            y2="250"
            gradientUnits="userSpaceOnUse"
          >
            <stop stopColor="#78baff" stopOpacity=".14" />
            <stop offset="1" stopColor="#78baff" stopOpacity=".02" />
          </linearGradient>
        </defs>
        <g stroke="#8fb9e9" strokeWidth=".7" opacity=".2">
          <path d="M38 250l172-96 172 96-172 96zM38 200l172-96 172 96M210 30v270M70 267l172-96M110 290l172-96M310 290l-172-96" />
        </g>
        <path
          d="M139 83v133c0 25 142 25 142 0V83"
          fill="url(#glass)"
          stroke="#afcff4"
          strokeOpacity=".6"
        />
        <ellipse
          cx="210"
          cy="83"
          rx="71"
          ry="24"
          fill="url(#glass)"
          stroke="#afcff4"
          strokeOpacity=".7"
        />
        <ellipse
          cx="210"
          cy="216"
          rx="71"
          ry="24"
          stroke="#afcff4"
          strokeOpacity=".25"
        />
        <path d="M140 154v62c0 25 140 25 140 0v-62" fill="url(#fluid)" />
        <ellipse
          cx="210"
          cy="154"
          rx="70"
          ry="23"
          stroke="#89c8ff"
          strokeOpacity=".65"
          className="liquid-ring"
        />
        <path d="M151 88v124M269 88v124" stroke="#c7dfff" strokeOpacity=".2" />
        <path
          d="M203 42v150M217 42v150M202 42c0 4 16 4 16 0s-16-4-16 0"
          stroke="#a8ccf5"
          strokeOpacity=".7"
        />
        <path
          d="M177 169l33 12 33-12M177 169v9l33 12 33-12v-9M210 181v9"
          stroke="#89c8ff"
          strokeOpacity=".7"
        />
        <path
          d="M177 117l33 12 33-12M177 117v9l33 12 33-12v-9"
          stroke="#afcff4"
          strokeOpacity=".5"
        />
        <path
          d="M160 68V43l-29-16M257 68V47l33-18M160 236v29M260 236v29"
          stroke="#afcff4"
          strokeOpacity=".6"
        />
        <g className="reactor-bubbles" fill="#89c8ff">
          <circle cx="169" cy="204" r="2" />
          <circle cx="240" cy="196" r="1.5" />
          <circle cx="187" cy="188" r="2" />
          <circle cx="248" cy="174" r="1" />
          <circle cx="229" cy="216" r="1.7" />
        </g>
        <g stroke="#b7d6fb" strokeOpacity=".45">
          <path d="M278 111h42l18-20M141 190H97l-18 20" />
          <circle cx="278" cy="111" r="2" />
          <circle cx="141" cy="190" r="2" />
        </g>
        <g fill="#bbd7fa" fontSize="8" fontFamily="monospace" letterSpacing="1">
          <text x="305" y="81">
            DIGITAL TWIN
          </text>
          <text x="34" y="224">
            FED-BATCH
          </text>
          <text x="174" y="284">
            INDPENSIM / 01
          </text>
        </g>
      </svg>
      <span className="reactor-coordinate">SIMULATION DOMAIN · BIOPROCESS</span>
    </div>
  );
}
