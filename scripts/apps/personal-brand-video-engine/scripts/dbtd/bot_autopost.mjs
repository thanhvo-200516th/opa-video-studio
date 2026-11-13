import fs from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const configPath = path.join(__dirname, "config.json");
const profileDir = path.join(__dirname, "browser_profile");
const logDir = path.join(__dirname, "logs");
const localStatusPath = path.join(__dirname, "local_status.json");
const credentialsPath = path.join(__dirname, "credentials.json");

await fs.mkdir(logDir, { recursive: true });
await fs.mkdir(profileDir, { recursive: true });

const config = JSON.parse(await fs.readFile(configPath, "utf8"));
const args = new Set(process.argv.slice(2));
const isLoginMode = args.has("--login");
const isDryRun = args.has("--dry-run");
const forceId = [...args].find((a) => a.startsWith("--id="))?.split("=")[1];

async function writeLog(msg) {
  const now = new Date().toLocaleString("vi-VN", { timeZone: "Asia/Ho_Chi_Minh" });
  const line = `[${now}] ${msg}`;
  console.log(line);
  await fs.appendFile(path.join(logDir, "autopost.log"), line + "\r\n", "utf8");
}

/**
 * Quét thư mục bài đăng trong DBTD để tự động nhận diện file theo quy tắc cố định:
 *   - [Prefix]_VIDEO.mp4
 *   - [Prefix]_THUMB.png / .jpg
 *   - [Prefix]_IMG_01.png, [Prefix]_IMG_02.png...
 */
export async function scanPostMedia(dbtdRootDir, relativeFolder, filePrefix) {
  const folderSubPath = relativeFolder.replace(/^DBTD[\\/]/i, "");
  const folderPath = path.join(dbtdRootDir, folderSubPath);

  if (!existsSync(folderPath)) {
    return { folderPath, exists: false, video: null, thumb: null, images: [] };
  }

  const entries = await fs.readdir(folderPath);
  let video = null;
  let thumb = null;
  const images = [];

  for (const name of entries.sort()) {
    const upper = name.toUpperCase();
    const full = path.join(folderPath, name);
    if (upper.startsWith(`${filePrefix.toUpperCase()}_VIDEO.`) || upper.endsWith("_VIDEO.MP4") || upper.endsWith("_FINAL.MP4")) {
      video = full;
    } else if (upper.includes("_THUMB.")) {
      thumb = full;
    } else if (upper.includes("_IMG_")) {
      images.push(full);
    }
  }

  return { folderPath, exists: true, video, thumb, images };
}

function parseCsvText(text) {
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

/**
 * Đọc lịch đăng trực tiếp từ tab 'Lịch Đăng Tự Động' (gid=229404957) trên Google Sheet
 * (Nếu mất mạng tạm thời sẽ fallback về danh_sach_60_bai_autopost.json trên máy)
 */
async function loadSchedule() {
  const catalogPath = path.join(config.dbtdRootDir, "danh_sach_60_bai_autopost.json");
  let catalog = JSON.parse(await fs.readFile(catalogPath, "utf8"));

  if (config.googleSheetId && config.autoPostTabGid) {
    try {
      const csvUrl = `https://docs.google.com/spreadsheets/d/${config.googleSheetId}/export?format=csv&gid=${config.autoPostTabGid}`;
      const res = await fetch(csvUrl);
      if (res.ok) {
        const csvText = await res.text();
        const rows = parseCsvText(csvText);
        // Data rows start after header row "STT"
        const headerIdx = rows.findIndex((r) => r[0] === "STT");
        if (headerIdx !== -1) {
          const dataRows = rows.slice(headerIdx + 1).filter((r) => r[4]);
          catalog = dataRows.map((r, idx) => ({
            seq: Number(r[0]) || idx + 1,
            rowNumberOnSheet: headerIdx + 2 + idx,
            date: r[1]?.trim() || "",
            time: r[2]?.trim() || "19:30",
            week: r[3]?.trim() || "",
            contentId: r[4]?.trim() || "",
            relativeFolder: r[5]?.trim() || "",
            filePrefix: r[6]?.trim() || "",
            tiktokMediaType: r[7]?.trim() || "VIDEO",
            thumbText: r[8]?.trim() || "",
            captionTikTok: r[9]?.trim() || "",
            fbMediaType: r[10]?.trim() || "VIDEO",
            postFacebook: r[11]?.trim() || "",
            statusTikTok: r[12]?.trim() || "Chờ file",
            statusFBProfile: r[13]?.trim() || "Chờ file",
            statusFanpage: r[14]?.trim() || "Chờ file",
            logNote: r[15]?.trim() || "",
          }));
        }
      }
    } catch (err) {
      await writeLog(`[Cảnh báo] Không tải được CSV trực tiếp từ Google Sheet (${err.message}), dùng bản lưu trên máy.`);
    }
  }

  let localStatus = {};
  if (existsSync(localStatusPath)) {
    localStatus = JSON.parse(await fs.readFile(localStatusPath, "utf8"));
  }

  for (const item of catalog) {
    const saved = localStatus[item.contentId];
    if (saved) {
      item.statusTikTok = saved.statusTikTok ?? item.statusTikTok;
      item.statusFBProfile = saved.statusFBProfile ?? item.statusFBProfile;
      item.statusFanpage = saved.statusFanpage ?? item.statusFanpage;
    }
  }

  return { catalog, localStatus };
}

async function saveStatus(localStatus, contentId, platformKey, newStatus, linkOrNote = "") {
  localStatus[contentId] = localStatus[contentId] || {};
  localStatus[contentId][platformKey] = newStatus;
  localStatus[contentId].updatedAt = new Date().toISOString();
  if (linkOrNote) {
    localStatus[contentId].note = linkOrNote;
  }
  await fs.writeFile(localStatusPath, JSON.stringify(localStatus, null, 2), "utf8");
}

function isDueNow(dateDDMMYYYY, timeHHMM) {
  const [dd, mm, yyyy] = dateDDMMYYYY.split("/").map(Number);
  const [hh, min] = (timeHHMM || "19:30").split(":").map(Number);
  const now = new Date();
  const todayDD = now.getDate();
  const todayMM = now.getMonth() + 1;
  const todayYYYY = now.getFullYear();

  if (yyyy !== todayYYYY || mm !== todayMM || dd !== todayDD) return false;
  const nowMinutes = now.getHours() * 60 + now.getMinutes();
  const scheduledMinutes = hh * 60 + min;
  return nowMinutes >= scheduledMinutes;
}

/**
 * Tự động đăng TikTok qua TikTok Studio (Chạy ngầm Headless)
 */
async function postToTikTok(context, item, media) {
  if (!media.video) {
    throw new Error(`Không tìm thấy file ${item.filePrefix}_VIDEO.mp4 trong ${media.folderPath}`);
  }
  await writeLog(`[TikTok] Đang mở ngầm TikTok Studio Upload cho bài ${item.contentId}...`);
  const page = await context.newPage();
  try {
    await page.goto("https://www.tiktok.com/tiktokstudio/upload", { waitUntil: "domcontentloaded", timeout: 60000 });
    await page.waitForTimeout(4000);

    const fileInput = page.locator('input[type="file"][accept*="video"]').first();
    await fileInput.setInputFiles(media.video);
    await writeLog(`[TikTok] Đã nạp video: ${path.basename(media.video)}. Chờ xử lý...`);

    const captionEditor = page.locator('[contenteditable="true"]').first();
    await captionEditor.waitFor({ state: "visible", timeout: 60000 });
    await captionEditor.click();
    await page.keyboard.press("Control+A");
    await page.keyboard.press("Backspace");
    await page.keyboard.insertText(item.captionTikTok);

    // Chờ nút Đăng (Post) sẵn sàng
    await page.waitForTimeout(10000);
    const postBtn = page.locator('button[data-e2e="post_video_button"], button:has-text("Đăng"), button:has-text("Post")').first();
    await postBtn.click();
    await page.waitForTimeout(8000);
    await writeLog(`[TikTok] ✅ Đã đăng thành công mã ${item.contentId}!`);
  } finally {
    await page.close();
  }
}

/**
 * Tự động đăng Facebook Cá Nhân / Fanpage (Hỗ trợ cả VIDEO và BỘ ẢNH IMG_01, IMG_02...)
 */
async function postToFacebook(context, item, media, isFanpage = false) {
  const label = isFanpage ? "Fanpage" : "FB Cá Nhân";
  const targetUrl = isFanpage && config.fanpageUrl ? config.fanpageUrl : "https://www.facebook.com/";
  const filesToUpload = [];

  if (item.fbMediaType === "VIDEO" && media.video) {
    filesToUpload.push(media.video);
  } else if (item.fbMediaType === "VIDEO + IMG") {
    if (media.video) filesToUpload.push(media.video);
    else if (media.images.length > 0) filesToUpload.push(...media.images);
  } else if (media.images.length > 0) {
    filesToUpload.push(...media.images);
  } else if (media.video) {
    filesToUpload.push(media.video);
  }

  if (filesToUpload.length === 0) {
    throw new Error(`[${label}] Chưa có file _VIDEO.mp4 hoặc _IMG_01.png trong ${media.folderPath}`);
  }

  await writeLog(`[${label}] Đang mở ngầm ${targetUrl} cho bài ${item.contentId}...`);
  const page = await context.newPage();
  try {
    await page.goto(targetUrl, { waitUntil: "domcontentloaded", timeout: 60000 });
    await page.waitForTimeout(4000);

    // Mở khung tạo bài viết và nạp file
    const fileInput = page.locator('input[type="file"]').first();
    await fileInput.setInputFiles(filesToUpload);
    await writeLog(`[${label}] Đã nạp ${filesToUpload.length} file media.`);

    await page.waitForTimeout(3000);
    const editor = page.locator('div[role="dialog"] [contenteditable="true"], [aria-label*="bạn đang nghĩ gì" i], [aria-label*="what\'s on your mind" i]').first();
    await editor.click();
    await page.keyboard.insertText(item.postFacebook);

    await page.waitForTimeout(8000);
    const submitBtn = page.locator('div[role="dialog"] [aria-label="Đăng"], div[role="dialog"] [aria-label="Post"], div[role="dialog"] [ aria-label="Tiếp" ]').first();
    await submitBtn.click();
    await page.waitForTimeout(8000);
    await writeLog(`[${label}] ✅ Đã đăng thành công mã ${item.contentId}!`);
  } finally {
    await page.close();
  }
}

async function main() {
  const { catalog, localStatus } = await loadSchedule();

  if (isDryRun) {
    await writeLog("=== CHẾ ĐỘ KIỂM TRA LỊCH & FILE TRONG DBTD (DRY-RUN) ===");
    for (const item of catalog.slice(0, 8)) {
      const media = await scanPostMedia(config.dbtdRootDir, item.relativeFolder, item.filePrefix);
      await writeLog(
        `Bài #${String(item.seq).padStart(2, "0")} [${item.date} ${item.time}] ${item.contentId} | Folder: ${
          media.exists ? "CÓ" : "THIẾU"
        } | Video: ${media.video ? "CÓ" : "Chưa bỏ file"} | Ảnh: ${media.images.length} file`
      );
    }
    return;
  }

  const { chromium } = await import("playwright");

  if (isLoginMode) {
    await writeLog("=== CHẾ ĐỘ ĐĂNG NHẬP LẦN ĐẦU (MỞ CỬA SỐ TRÌNH DUYỆT) ===");
    await writeLog("Hãy đăng nhập sẵn TikTok và Facebook trong cửa sổ trình duyệt vừa mở. Sau khi đăng nhập xong, bạn chỉ cần đóng trình duyệt lại.");
    const context = await chromium.launchPersistentContext(profileDir, {
      headless: false,
      channel: config.browserChannel || "chrome",
      viewport: { width: 1280, height: 820 },
      args: ["--disable-blink-features=AutomationControlled"],
    });
    const page1 = context.pages()[0] || (await context.newPage());
    await page1.goto("https://www.tiktok.com/tiktokstudio/upload");
    const page2 = await context.newPage();
    await page2.goto("https://www.facebook.com/");
    await new Promise((resolve) => context.on("close", resolve));
    await writeLog("✅ Đã lưu phiên đăng nhập vào DBTD/_he_thong_bot/browser_profile!");
    return;
  }

  // Chế độ chạy ngầm 100% (Headless = true)
  const dueItems = catalog.filter((item) => {
    if (forceId) return item.contentId.toUpperCase() === forceId.toUpperCase();
    return isDueNow(item.date, item.time);
  });

  if (dueItems.length === 0) {
    await writeLog("Chưa có bài đăng nào tới giờ cần chạy trong khung giờ này.");
    return;
  }

  const context = await chromium.launchPersistentContext(profileDir, {
    headless: config.headless !== false,
    channel: config.browserChannel || "chrome",
    viewport: { width: 1280, height: 820 },
    args: [
      "--headless=new",
      "--disable-blink-features=AutomationControlled",
      "--mute-audio",
      "--no-first-run",
    ],
  });

  try {
    for (const item of dueItems) {
      const media = await scanPostMedia(config.dbtdRootDir, item.relativeFolder, item.filePrefix);
      const hasAnyMedia = Boolean(media.video || media.images.length > 0);
      if (!hasAnyMedia) {
        await writeLog(`[Bỏ qua tạm thời] Bài ${item.contentId} (${item.date}) đã tới giờ nhưng chưa có file _VIDEO.mp4 hoặc _IMG_01 trong ${media.folderPath}`);
        continue;
      }

      if (item.statusTikTok !== "Đã đăng ✅" && item.statusTikTok !== "Bỏ qua") {
        try {
          await postToTikTok(context, item, media);
          await saveStatus(localStatus, item.contentId, "statusTikTok", "Đã đăng ✅");
        } catch (err) {
          await writeLog(`[Lỗi TikTok - ${item.contentId}]: ${err.message}`);
          await saveStatus(localStatus, item.contentId, "statusTikTok", "Lỗi ⚠️", err.message);
        }
      }

      if (item.statusFBProfile !== "Đã đăng ✅" && item.statusFBProfile !== "Bỏ qua") {
        try {
          await postToFacebook(context, item, media, false);
          await saveStatus(localStatus, item.contentId, "statusFBProfile", "Đã đăng ✅");
        } catch (err) {
          await writeLog(`[Lỗi FB Cá nhân - ${item.contentId}]: ${err.message}`);
          await saveStatus(localStatus, item.contentId, "statusFBProfile", "Lỗi ⚠️", err.message);
        }
      }

      if (item.statusFanpage !== "Đã đăng ✅" && item.statusFanpage !== "Bỏ qua") {
        try {
          await postToFacebook(context, item, media, true);
          await saveStatus(localStatus, item.contentId, "statusFanpage", "Đã đăng ✅");
        } catch (err) {
          await writeLog(`[Lỗi Fanpage - ${item.contentId}]: ${err.message}`);
          await saveStatus(localStatus, item.contentId, "statusFanpage", "Lỗi ⚠️", err.message);
        }
      }
    }
  } finally {
    await context.close();
  }
}

main().catch(async (err) => {
  await writeLog(`[FATAL ERROR] ${err.stack || err.message}`);
  process.exit(1);
});
