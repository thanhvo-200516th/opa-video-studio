// Đường cong theo thời gian cho máy quay và tư thế: Hermite bậc ba, liên tục C1 qua các khóa đặt không đều.
// Tiếp tuyến tại khóa giữa = chênh lệch hữu hạn theo thời gian; khóa đầu, khóa cuối và khóa "hold" có tiếp tuyến 0
// (dừng mượt, không vọt). Dùng: const camPos = track([[0, [x, y, z]], [2.6, [...], true], ...]); camPos(t) -> [x, y, z].
export function track(keys) {
  const ks = keys.map(([t, v, hold]) => ({ t, v: Array.isArray(v) ? v : [v], hold: !!hold }));
  for (let i = 1; i < ks.length; i++) if (!(ks[i].t > ks[i - 1].t)) throw new Error(`track: khóa ${i} không tăng dần (${ks[i].t})`);
  const n = ks.length, dim = ks[0].v.length;
  const tang = ks.map((k, i) => {
    if (k.hold || i === 0 || i === n - 1) return new Array(dim).fill(0);
    const a = ks[i - 1], b = ks[i + 1];
    return k.v.map((_, d) => (b.v[d] - a.v[d]) / (b.t - a.t));
  });
  return (t) => {
    if (t <= ks[0].t) return ks[0].v.slice();
    if (t >= ks[n - 1].t) return ks[n - 1].v.slice();
    let i = 0;
    while (t > ks[i + 1].t) i++;
    const a = ks[i], b = ks[i + 1], h = b.t - a.t, u = (t - a.t) / h;
    const u2 = u * u, u3 = u2 * u;
    const h00 = 2 * u3 - 3 * u2 + 1, h10 = u3 - 2 * u2 + u, h01 = -2 * u3 + 3 * u2, h11 = u3 - u2;
    return a.v.map((_, d) => h00 * a.v[d] + h10 * h * tang[i][d] + h01 * b.v[d] + h11 * h * tang[i + 1][d]);
  };
}

/** Như track nhưng giá trị là một số. */
export function scalar(keys) {
  const f = track(keys);
  return (t) => f(t)[0];
}

export const clamp01 = (x) => Math.min(Math.max(x, 0), 1);
export const smooth = (x) => { const u = clamp01(x); return u * u * (3 - 2 * u); };
export const ramp = (t, a, b) => smooth((t - a) / (b - a));
export const easeIn = (x) => { const u = clamp01(x); return u * u; };
export const easeOut = (x) => { const u = clamp01(x); return 1 - (1 - u) * (1 - u); };
export const inOut = (x) => { const u = clamp01(x); return u < 0.5 ? 4 * u * u * u : 1 - (-2 * u + 2) ** 3 / 2; };
/** Dao động tắt dần bắt đầu ở t0 (0 trước t0). */
export const ring = (t, t0, amp, hz, decay) => (t < t0 ? 0 : amp * Math.exp(-(t - t0) * decay) * Math.sin(2 * Math.PI * hz * (t - t0)));
/** Cú nảy parabol từ t0 tới t1, cao h (0 ngoài khoảng). */
export const hop = (t, t0, t1, h) => (t <= t0 || t >= t1 ? 0 : 4 * h * ((t - t0) / (t1 - t0)) * (1 - (t - t0) / (t1 - t0)));
