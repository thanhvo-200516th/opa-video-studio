import React from "react";
import { continueRender, delayRender, staticFile } from "remotion";

const FACES: [string, string, string][] = [
  ["BeVietnamPro", "fonts/BeVietnamPro-Medium.ttf", "500"],
  ["BeVietnamProBold", "fonts/BeVietnamPro-Bold.ttf", "700"],
  ["BeVietnamProBlack", "fonts/BeVietnamPro-Black.ttf", "900"],
  ["DTPhudu", "fonts/DTPhudu-Bold.otf", "700"],
  ["DTPhuduBlack", "fonts/DTPhudu-Black.otf", "900"],
  ["BebasNeueVN", "fonts/BebasNeue.otf", "400"],
  ["Merolat", "fonts/Merolat.ttf", "400"],
  ["BeVietnamProBlackItalic", "fonts/BeVietnamPro-BlackItalic.ttf", "900"],
  ["HeyMonday", "fonts/HeyMonday.ttf", "400"],
];

const css = FACES.map(
  ([family, file, weight]) =>
    `@font-face{font-family:'${family}';src:url('${staticFile(file)}');font-weight:${weight};font-display:block;}`
).join("\n");

/** Chèn @font-face và chặn render tới khi font thật sự sẵn sàng. */
export const Fonts: React.FC = () => {
  const [handle] = React.useState(() => delayRender("fonts"));
  React.useEffect(() => {
    let alive = true;
    Promise.all(
      FACES.map(([f]) => document.fonts.load(`700 100px '${f}'`, "Ăâêôơư"))
    )
      .then(() => document.fonts.ready)
      .then(() => alive && continueRender(handle))
      .catch(() => alive && continueRender(handle));
    return () => {
      alive = false;
    };
  }, [handle]);
  return <style>{css}</style>;
};
