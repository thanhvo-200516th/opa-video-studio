import fs from "node:fs/promises";
import { chromium } from "playwright";

const sheetId = "1iF3AnPhuEs7A8o_zLJLfJtKA3JtjjynT9tkrNivsOu4";
const dbtdDir = "/media/vmiz/Over Powers/THÀNH V/THCN thành/THUONG_HIEU_CA_NHAN_THANH_90_NGAY/DBTD";

const catalog = JSON.parse(await fs.readFile(`${dbtdDir}/danh_sach_60_bai_autopost.json`, "utf8"));

// Read full CSV we generated earlier (has all 60 rows: 48 scheduled + 12 backup)
const csvRaw = await fs.readFile(`${dbtdDir}/Lich_Dang_Tu_Dong_Import_GGSheet.csv`, "utf8");

// Helper to format TSV cell for Google Sheets clipboard paste (RFC-4180 TSV: quote if contains \n, \r, \t, or ")
function toTsvCell(val) {
  const s = String(val ?? "").replace(/\r\n/g, "\n").replace(/\r/g, "\n").trim();
  if (s.includes("\n") || s.includes("\t") || s.includes('"') || s.startsWith("=")) {
    return `"${s.replace(/"/g, '""')}"`;
  }
  return s;
}

function toTsv(rows) {
  return rows.map((r) => r.map(toTsvCell).join("\t")).join("\n");
}

// 1. Prepare TSV for updating `Lịch sản xuất` (A5:N53)
const prodHeaders = [
  "Ngày",
  "Tuần",
  "Nền tảng",
  "Content ID",
  "Pillar",
  "Tuyến",
  "Tiêu đề",
  "Trạng thái",
  "Script",
  "Quay",
  "Dựng",
  "Đăng",
  "CTA",
  "Thư mục DBTD",
];
const prodRows = catalog.map((item, idx) => [
  item.date,
  item.week,
  idx % 2 === 0 ? "TikTok + Facebook Reels" : "TikTok + Facebook",
  item.contentId,
  item.pillar,
  item.route,
  item.title,
  "Ý tưởng",
  "Chưa",
  "Chưa",
  "Chưa",
  "Chưa",
  item.cta,
  item.relativeFolder,
]);
const prodTsv = toTsv([prodHeaders, ...prodRows]);

// 2. Parse CSV rows or build all 60 AutoPost rows
// Let's parse Lich_Dang_Tu_Dong_Import_GGSheet.csv back into rows so we include all 60 rows (48 main + 12 backup)
function parseCsv(text) {
  const clean = text.replace(/^\uFEFF/, "");
  const rows = [];
  let row = [];
  let cur = "";
  let inQuotes = false;
  for (let i = 0; i < clean.length; i++) {
    const ch = clean[i];
    const next = clean[i + 1];
    if (inQuotes) {
      if (ch === '"' && next === '"') {
        cur += '"';
        i++;
      } else if (ch === '"') {
        inQuotes = false;
      } else {
        cur += ch;
      }
    } else {
      if (ch === '"') {
        inQuotes = true;
      } else if (ch === ",") {
        row.push(cur);
        cur = "";
      } else if (ch === "\r" && next === "\n") {
        row.push(cur);
        rows.push(row);
        row = [];
        cur = "";
        i++;
      } else if (ch === "\n") {
        row.push(cur);
        rows.push(row);
        row = [];
        cur = "";
      } else {
        cur += ch;
      }
    }
  }
  if (cur.length > 0 || row.length > 0) {
    row.push(cur);
    rows.push(row);
  }
  return rows;
}

const csvParsedRows = parseCsv(csvRaw);
const autoTitleRows = [
  ["Bảng Điều Khiển Đăng Bài Tự Động (TikTok + Facebook Cá Nhân + Fanpage)"],
  ["Thư mục gốc: F:\\THÀNH V\\THCN thành\\THUONG_HIEU_CA_NHAN_THANH_90_NGAY\\DBTD | Quy tắc đặt tên file: [Prefix]_VIDEO.mp4, [Prefix]_THUMB.png, [Prefix]_IMG_01.png..."],
  [],
  ...csvParsedRows,
];
const autoPostTsv = toTsv(autoTitleRows);

const browser = await chromium.launch({ headless: true, channel: "chrome" });
const context = await browser.newContext({
  viewport: { width: 1440, height: 900 },
  permissions: ["clipboard-read", "clipboard-write"],
});
const page = await context.newPage();

async function gotoCell(cellRef) {
  const nameBox = page.locator("#t-name-box, input.waffle-name-box").first();
  await nameBox.click();
  await page.keyboard.press("Control+A");
  await page.keyboard.type(cellRef, { delay: 30 });
  await page.keyboard.press("Enter");
  await page.waitForTimeout(800);
}

async function pasteTsvAt(cellRef, tsvText) {
  await gotoCell(cellRef);
  await page.evaluate(async (text) => {
    await navigator.clipboard.writeText(text);
  }, tsvText);
  await page.waitForTimeout(400);
  await page.keyboard.press("Control+V");
  await page.waitForTimeout(5000);
}

console.log("1. Mở trực tiếp tab Lịch Đăng Tự Động (gid=229404957)...");
await page.goto(`https://docs.google.com/spreadsheets/d/${sheetId}/edit?gid=229404957#gid=229404957`, {
  waitUntil: "domcontentloaded",
  timeout: 60000,
});
await page.waitForTimeout(7000);

const newUrl = page.url();
const gidMatch = newUrl.match(/gid=(\d+)/);
const newGid = gidMatch ? gidMatch[1] : "229404957";
console.log("Tab URL:", newUrl, "GID:", newGid);

console.log("2. Dán toàn bộ 60 bài Lịch Đăng Tự Động (Caption sạch không chứa ký tự Markdown) vào A1...");
await pasteTsvAt("A1", autoPostTsv);

// Format header row A4:P4 bold & freeze rows 1..4
await gotoCell("A4:P4");
await page.keyboard.press("Control+B");
await page.waitForTimeout(500);
await gotoCell("A1");
await page.keyboard.press("Control+B");

// Wait for Google Sheets to finish saving
await page.waitForTimeout(8000);
await page.screenshot({ path: `${dbtdDir}/_he_thong_bot/logs/proof_ggsheet_autopost.png` });

// Save the new GID into config.json
if (newGid) {
  const cfgPath = `${dbtdDir}/_he_thong_bot/config.json`;
  const cfg = JSON.parse(await fs.readFile(cfgPath, "utf8"));
  cfg.autoPostTabGid = newGid;
  await fs.writeFile(cfgPath, JSON.stringify(cfg, null, 2), "utf8");
}

await browser.close();
console.log("DONE! Synced to Google Sheet successfully. New GID:", newGid);
