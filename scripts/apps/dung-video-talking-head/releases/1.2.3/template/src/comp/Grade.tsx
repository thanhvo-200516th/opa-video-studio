import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { rand } from "../anim";

const GRAIN =
  "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='260' height='260'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")";

/** Vignette + scrim đọc chữ + grain nhẹ. Grain dịch theo frame nên không "dính" vào ảnh. */
export const Grade: React.FC = () => {
  const frame = useCurrentFrame();
  const gx = Math.floor(rand(frame) * 260);
  const gy = Math.floor(rand(frame + 977) * 260);

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse 76% 60% at 50% 38%, rgba(0,0,0,0) 38%, rgba(0,0,0,.46) 100%)",
        }}
      />
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(to top, rgba(0,0,0,.66) 0%, rgba(0,0,0,.34) 20%, rgba(0,0,0,0) 46%)",
        }}
      />
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(to bottom, rgba(0,0,0,.42) 0%, rgba(0,0,0,0) 18%)",
        }}
      />
      <AbsoluteFill
        style={{
          backgroundImage: GRAIN,
          backgroundPosition: `${gx}px ${gy}px`,
          opacity: 0.045,
          mixBlendMode: "overlay",
        }}
      />
    </AbsoluteFill>
  );
};
