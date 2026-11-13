"""Ảnh phổ có đánh dấu cue cho phim 3D "Thủ môn" (G6): pho-cue.png.

Phổ log tần số (30 Hz – 16 kHz) của master, vạch cue tô màu theo nhóm bus, tên cue ở mép trên, các đoạn nhạc (sections)
và khoảng lặng khai báo tô nền. Đọc được bằng mắt (và bằng Opus) để soát "đúng số mà sai chất".
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

SR = 48000
GROUP_COLOR = {"giong-bo": "#0068FF", "hung": "#E5484D", "the-gioi": "#1A9E5B", "chuyen-canh": "#9A6BFF",
               "logo": "#F5A623", "nen": "#888888"}


def group_of(kind: str, groups: dict[str, set[str]]) -> str:
    return next((g for g, kinds in groups.items() if kind in kinds), "khác")


def spectrogram_png(master: np.ndarray, sheet: dict, groups: dict[str, set[str]], out: Path,
                    title: str = "thu-mon · master") -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from scipy.signal import spectrogram

    f, t, s = spectrogram(master, fs=SR, nperseg=2048, noverlap=2048 - 256, window="hann", mode="magnitude")
    s_db = 20 * np.log10(s + 1e-9)
    s_db -= s_db.max()
    fig, ax = plt.subplots(figsize=(32, 10), dpi=100)
    sel = (f >= 30) & (f <= 16000)
    ax.pcolormesh(t, f[sel], s_db[sel], shading="auto", cmap="magma", vmin=-90, vmax=0)
    ax.set_yscale("log")
    ax.set_ylim(30, 16000)
    ax.set_xlim(0, len(master) / SR)
    ax.set_xlabel("giây")
    ax.set_ylabel("Hz")
    ax.set_title(f"{title} — vạch cue theo nhóm bus; nền xám = khoảng lặng khai báo", fontsize=13)
    for s_ in sheet["silences"]:
        if s_["kind"] in ("near", "silent") and s_["scope"] == "mix":
            ax.axvspan(s_["from"] / 30, s_["to"] / 30, color="#BBBBBB", alpha=0.35, lw=0)
    for sec in sheet["sections"]:
        ax.axvline(sec["from"] / 30, color="white", lw=0.6, alpha=0.5)
        ax.text(sec["from"] / 30 + 0.03, 34, sec["name"], color="white", fontsize=9, alpha=0.9)
    for i, ev in enumerate(e for e in sheet["events"] if e["sound"] and e["kind"] != "bed"):
        g = group_of(ev["kind"], groups)
        x = float(ev["f"]) / 30
        ax.axvline(x, color=GROUP_COLOR.get(g, "white"), lw=0.9, alpha=0.85)
        ax.text(x, 16000 * (0.88 ** (i % 8)), ev["id"], rotation=90, fontsize=8, va="top", ha="right",
                color=GROUP_COLOR.get(g, "white"))
    handles = [plt.Line2D([0], [0], color=c, lw=3) for c in GROUP_COLOR.values()]
    ax.legend(handles, list(GROUP_COLOR), loc="lower right", fontsize=9, framealpha=0.6)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    plt.close(fig)
    return out
