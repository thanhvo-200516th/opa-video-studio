// Kênh gửi khung về Python (tools/film3d/render.py).
// Mỗi tin nhị phân: [u32 LE độ dài header][header JSON utf-8][dữ liệu]; chờ 'ok' rồi mới gửi tin sau (giữ nhịp, không dồn bộ nhớ).
export async function connectWire(url) {
  const ws = new WebSocket(url);
  ws.binaryType = 'arraybuffer';
  await new Promise((resolve, reject) => {
    ws.onopen = resolve;
    ws.onerror = () => reject(new Error(`không nối được WebSocket ${url}`));
  });
  const waiters = [];
  ws.onmessage = () => { const w = waiters.shift(); if (w) w(); };
  const enc = new TextEncoder();

  async function send(header, payload) {
    const h = enc.encode(JSON.stringify(header));
    const n = payload ? payload.byteLength : 0;
    const buf = new Uint8Array(4 + h.length + n);
    new DataView(buf.buffer).setUint32(0, h.length, true);
    buf.set(h, 4);
    if (payload) buf.set(new Uint8Array(payload.buffer, payload.byteOffset, payload.byteLength), 4 + h.length);
    const acked = new Promise((r) => waiters.push(r));
    ws.send(buf);
    await acked;
  }
  return { send, log: (msg) => send({ type: 'log', msg: String(msg) }) };
}
