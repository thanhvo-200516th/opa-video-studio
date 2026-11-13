import React from "react";
import { COLORS, MascotState } from "./tokens";

export interface MascotAvatarProps {
  state?: MascotState;
  size?: number;
  color?: string;
  className?: string;
  style?: React.CSSProperties;
}

export const MascotAvatar: React.FC<MascotAvatarProps> = ({
  state = "idle",
  size = 48,
  color = COLORS.primary,
  className = "",
  style = {},
}) => {
  return (
    <div
      className={`opa-mascot-container ${className}`}
      style={{
        width: size,
        height: size,
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        position: "relative",
        ...style,
      }}
    >
      <svg
        viewBox="0 0 2000 2000"
        width="100%"
        height="100%"
        style={{ overflow: "visible" }}
      >
        <g id="mascot-body" className={`mascot-${state}`} fill={color}>
          {/* U-Shape Muzzle */}
          <path
            id="c-muzzle"
            className="part-muzzle"
            d="M 877.25 814.86 L 658.32 814.86 L 480 987.27 L 480 1235.56 A 397.24 397.24 0 0 0 877.25 1632.8 L 1122.76 1632.8 A 397.24 397.24 0 0 0 1520 1235.56 L 1520 987.27 L 1341.68 814.86 L 1122.76 814.86 L 1122.76 937.62 A 198.62 198.62 0 0 1 1321.38 1136.24 L 1321.38 1235.56 A 198.62 198.62 0 0 1 1122.76 1434.18 L 877.25 1434.18 A 198.62 198.62 0 0 1 678.62 1235.56 L 678.62 1136.24 A 198.62 198.62 0 0 1 877.25 937.62 Z"
          />

          {/* Left Horn with pivot 569.16 901.07 */}
          <path
            id="a-horn-left"
            className="part-horn-left"
            style={{ transformOrigin: "569.16px 901.07px" }}
            d="M 658.32 814.86 C 551.92 814.86 338.18 604.44 439.79 407.48 L 349.62 367.33 C 265.83 524.18 300.58 861.43 480 987.27 L 504 1090 L 660 1030 L 760 890 Z"
          />

          {/* Right Horn with pivot 1430.84 901.07 */}
          <path
            id="b-horn-right"
            className="part-horn-right"
            style={{ transformOrigin: "1430.84px 901.07px" }}
            d="M 1341.68 814.86 C 1448.08 814.86 1661.82 604.44 1560.21 407.48 L 1650.38 367.33 C 1734.17 524.18 1699.42 861.43 1520 987.27 L 1496 1090 L 1340 1030 L 1240 890 Z"
          />

          {/* Nostril Gap */}
          <path
            id="d-nostril-gap"
            fill="none"
            d="M 877.25 814.86 L 1122.76 814.86 L 1122.76 937.62 L 877.25 937.62 Z"
          />
        </g>
      </svg>

      <style>{`
        /* Idle: gentle breathing */
        .mascot-idle {
          transform-origin: 1000px 1200px;
          animation: opaBreathe 2.4s cubic-bezier(0.4, 0, 0.2, 1) infinite;
        }
        @keyframes opaBreathe {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.025) translateY(-8px); }
        }

        /* Thinking: horns wiggle, subtle muzzle glow */
        .mascot-thinking .part-horn-left {
          animation: opaHornLeft 1.2s ease-in-out infinite alternate;
        }
        .mascot-thinking .part-horn-right {
          animation: opaHornRight 1.2s ease-in-out infinite alternate;
        }
        .mascot-thinking .part-muzzle {
          animation: opaThinkingMuzzle 1.2s ease-in-out infinite alternate;
        }
        @keyframes opaHornLeft {
          0% { transform: rotate(-3deg); }
          100% { transform: rotate(4deg); }
        }
        @keyframes opaHornRight {
          0% { transform: rotate(3deg); }
          100% { transform: rotate(-4deg); }
        }
        @keyframes opaThinkingMuzzle {
          0% { opacity: 0.9; }
          100% { opacity: 1; transform: translateY(-4px); }
        }

        /* Responding: attentive, horns erect, slight pulse */
        .mascot-responding {
          transform-origin: 1000px 1000px;
          animation: opaResponding 1.6s ease-in-out infinite;
        }
        @keyframes opaResponding {
          0%, 100% { transform: scale(1.02); }
          50% { transform: scale(1.04) translateY(-6px); }
        }

        /* Success / Catch: snappy pop and settle */
        .mascot-success {
          transform-origin: 1000px 1200px;
          animation: opaPop 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) 1;
        }
        @keyframes opaPop {
          0% { transform: scale(0.9) translateY(20px); }
          60% { transform: scale(1.1) translateY(-15px); }
          100% { transform: scale(1) translateY(0); }
        }

        /* Alert / Error: fast shake */
        .mascot-alert {
          transform-origin: 1000px 1000px;
          animation: opaAlert 0.4s ease-in-out 2;
        }
        @keyframes opaAlert {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-15px) rotate(-2deg); }
          75% { transform: translateX(15px) rotate(2deg); }
        }
      `}</style>
    </div>
  );
};

export default MascotAvatar;
