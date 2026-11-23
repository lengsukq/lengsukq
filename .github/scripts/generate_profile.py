#!/usr/bin/env python3
"""Generate animated SVG profile telemetry and flagship project cards for lengsukq."""

from __future__ import annotations

import html
import json
import os
import urllib.request
from collections import Counter
from pathlib import Path

USERNAME = "lengsukq"
REPO_ROOT = Path(__file__).resolve().parents[2]
ASSETS_DIR = REPO_ROOT / "assets"

LANG_COLORS = {
    "TypeScript": "#3178C6",
    "Swift": "#F05138",
    "Python": "#3572A5",
    "Go": "#00ADD8",
    "Kotlin": "#A97BFF",
    "Dart": "#00B4AB",
    "Vue": "#41B883",
    "JavaScript": "#F1E05A",
    "Java": "#B07219",
    "Rust": "#DEA584",
}

FLAGSHIP_SPECS = [
    {
        "repo": "Lucent",
        "slug": "lucent",
        "title": "Lucent",
        "badge": "Apple Silicon · Swift 6",
        "accent": "#38BDF8",
        "accent2": "#818CF8",
        "line1": "Liquid Glass 原生启动器：Everything 级检索、QQ 式截图 OCR",
        "line2": "集成 System Pulse 监控、实时网络监视与高效文件工作区",
        "tags": ["Swift 6", "Liquid Glass", "OCR", "macOS"],
        "lang": "Swift",
    },
    {
        "repo": "OpalDesk",
        "slug": "opaldesk",
        "title": "OpalDesk",
        "badge": "Multi-Display · No Root",
        "accent": "#A78BFA",
        "accent2": "#EC4899",
        "line1": "免 Root Android 多屏桌面工作站（LocalDeX / 外接显示器）",
        "line2": "支持 macOS 原生高速串流、Type-C 扩展与 Liquid Glass 窗口引擎",
        "tags": ["Kotlin", "Compose", "SwiftUI", "Shizuku"],
        "lang": "Kotlin",
    },
    {
        "repo": "LightIsle",
        "slug": "lightisle",
        "title": "LightIsle 轻屿",
        "badge": "Native NAS · Go + SwiftUI",
        "accent": "#34D399",
        "accent2": "#06B6D4",
        "line1": "Apple Silicon macOS 原生轻量 NAS 一体化方案",
        "line2": "SwiftUI 桌面管理端 + 高性能 Go Core 核心 + Vue Web 用户端",
        "tags": ["Go", "SwiftUI", "Vue 3", "NAS"],
        "lang": "Go",
    },
    {
        "repo": "sts2-macos-launcher",
        "slug": "sts2",
        "title": "sts2-macos-launcher",
        "badge": "Game Bridge · HUD",
        "accent": "#F97316",
        "accent2": "#FBBF24",
        "line1": "《杀戮尖塔 2》Apple Silicon macOS 非官方原生桥接启动器",
        "line2": "提供 Mod 管理、隔离存档沙盒、实时诊断与游戏内性能 HUD",
        "tags": ["Swift", "macOS", "Modding", "HUD"],
        "lang": "Swift",
    },
    {
        "repo": "LexiLoop",
        "slug": "lexiloop",
        "title": "LexiLoop 词环",
        "badge": "FSRS · AI Vocab",
        "accent": "#60A5FA",
        "accent2": "#34D399",
        "line1": "Next.js 16 + PostgreSQL 自托管词汇间隔重复复习应用",
        "line2": "支持 EasyDict 导入、AI 结构化词条初始化与有道词典联动",
        "tags": ["Next.js 16", "React 19", "PostgreSQL", "ts-fsrs"],
        "lang": "TypeScript",
    },
    {
        "repo": "MoteFlow",
        "slug": "moteflow",
        "title": "MoteFlow",
        "badge": "HID · Voice · macOS",
        "accent": "#C084FC",
        "accent2": "#38BDF8",
        "line1": "原生 macOS 无线远程控制中枢（SwiftUI + 蓝牙 HID）",
        "line2": "支持自定义键鼠映射、低延迟语音输入与系统级自动化操作",
        "tags": ["SwiftUI", "HID", "Bluetooth", "Automation"],
        "lang": "Swift",
    },
    {
        "repo": "cloudwatch-ai-alert",
        "slug": "cloudwatch",
        "title": "cloudwatch-ai-alert",
        "badge": "AI Ops · AWS",
        "accent": "#F43F5E",
        "accent2": "#FB923C",
        "line1": "AI 驱动的 AWS CloudWatch 告警智能诊断与分析平台",
        "line2": "FastAPI + React + SQLite 架构，自动关联日志与根因排查建议",
        "tags": ["FastAPI", "React", "AWS", "AI Ops"],
        "lang": "Python",
    },
    {
        "repo": "ParaphrasingToolClient",
        "slug": "paraphrasing",
        "title": "ParaphrasingToolClient",
        "badge": "Popular · AI Rewrite",
        "accent": "#10B981",
        "accent2": "#3B82F6",
        "line1": "论文 AI 智能降重客户端，支持 PaperYY 查重报告精确解析",
        "line2": "可视化逐句对照与自定义大模型接口，已部署在线服务",
        "tags": ["Vue 3", "TypeScript", "LLM", "Web"],
        "lang": "Vue",
    },
]


def github_get(path: str) -> dict | list:
    url = f"https://api.github.com/{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "lengsukq-profile-generator",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_all_repos() -> list[dict]:
    repos: list[dict] = []
    page = 1
    while True:
        batch = github_get(f"users/{USERNAME}/repos?type=public&per_page=100&page={page}")
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return repos


def render_overview_svg(user: dict, repos: list[dict]) -> str:
    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    non_fork = [r for r in repos if not r.get("fork") and not r.get("archived")]
    original_stars = sum(r.get("stargazers_count", 0) for r in non_fork)
    public_repos = user.get("public_repos", len(repos))
    followers = user.get("followers", 0)

    lang_counts: Counter[str] = Counter()
    for r in non_fork:
        lang = r.get("language")
        if lang:
            # Merge Java into Kotlin/Android weight if OpalDesk reports Java, or keep exact
            lang_counts[lang] += 1

    top_langs = lang_counts.most_common(6)
    total_lang_repos = sum(c for _, c in top_langs) or 1

    metrics = [
        ("TOTAL STARS", f"{total_stars}", "#FBBF24", "All Public Repos"),
        ("ORIGINAL STARS", f"{original_stars}", "#38BDF8", f"{len(non_fork)} Active Projects"),
        ("PUBLIC REPOS", f"{public_repos}", "#34D399", "Open Source"),
        ("FOLLOWERS", f"{followers}", "#A78BFA", "GitHub Community"),
    ]

    metric_blocks = []
    positions = [(28, 62), (294, 62), (28, 152), (294, 152)]
    for (label, value, color, sub), (x, y) in zip(metrics, positions):
        metric_blocks.append(f"""
    <g>
      <rect x="{x}" y="{y}" width="248" height="78" rx="14" fill="#0F172A" fill-opacity="0.88" stroke="#334155" stroke-opacity="0.65" stroke-width="1"/>
      <rect x="{x}" y="{y}" width="4" height="78" rx="2" fill="{color}"/>
      <text x="{x + 18}" y="{y + 24}" class="mono" font-size="11" font-weight="600" fill="#94A3B8">{html.escape(label)}</text>
      <text x="{x + 18}" y="{y + 54}" class="sans" font-size="28" font-weight="800" fill="#F8FAFC">{html.escape(value)}</text>
      <text x="{x + 232}" y="{y + 54}" text-anchor="end" class="mono" font-size="10.5" fill="{color}">{html.escape(sub)}</text>
    </g>""")

    bar_rows = []
    bar_x = 610
    bar_max_w = 430
    for idx, (lang, count) in enumerate(top_langs):
        pct = round(count * 100 / total_lang_repos, 1)
        w = max(24, round(bar_max_w * (count / total_lang_repos)))
        y = 74 + idx * 28
        color = LANG_COLORS.get(lang, "#60A5FA")
        bar_rows.append(f"""
    <g>
      <circle cx="{bar_x}" cy="{y + 7}" r="4.5" fill="{color}"/>
      <text x="{bar_x + 14}" y="{y + 11}" class="mono" font-size="12" font-weight="600" fill="#E2E8F0">{html.escape(lang)}</text>
      <rect x="{bar_x + 112}" y="{y + 1}" width="{bar_max_w}" height="12" rx="6" fill="#1E293B"/>
      <rect x="{bar_x + 112}" y="{y + 1}" width="{w}" height="12" rx="6" fill="{color}" fill-opacity="0.9">
        <animate attributeName="width" from="0" to="{w}" dur="{0.7 + idx * 0.12:.2f}s" fill="freeze"/>
      </rect>
      <text x="{bar_x + 558}" y="{y + 11}" text-anchor="end" class="mono" font-size="11.5" fill="#94A3B8">{count} ({pct}%)</text>
    </g>""")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 260" width="1200" height="260" fill="none">
  <defs>
    <linearGradient id="ovBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#070B14"/>
      <stop offset="100%" stop-color="#0D1526"/>
    </linearGradient>
    <linearGradient id="ovBorder" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#38BDF8" stop-opacity="0.5"/>
      <stop offset="50%" stop-color="#818CF8" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#34D399" stop-opacity="0.5"/>
    </linearGradient>
  </defs>
  <style>
    .mono {{ font-family: "SF Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
    .sans {{ font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; }}
  </style>
  <rect width="1200" height="260" rx="18" fill="url(#ovBg)"/>
  <rect x="1" y="1" width="1198" height="258" rx="18" stroke="url(#ovBorder)" stroke-width="1.2"/>

  <text x="28" y="38" class="mono" font-size="13" font-weight="700" fill="#38BDF8">✦ LIVE GITHUB TELEMETRY</text>
  <text x="542" y="38" text-anchor="end" class="mono" font-size="11" fill="#64748B">Auto-synced via Actions</text>

  <line x1="574" y1="26" x2="574" y2="234" stroke="#1E293B" stroke-width="1.5"/>

  <text x="610" y="38" class="mono" font-size="13" font-weight="700" fill="#A78BFA">✦ TOP LANGUAGES (ORIGINAL REPOS)</text>
  <text x="1168" y="38" text-anchor="end" class="mono" font-size="11" fill="#64748B">{len(non_fork)} repositories</text>

  {''.join(metric_blocks)}
  {''.join(bar_rows)}
</svg>
"""


def render_project_card(spec: dict, repo_data: dict | None) -> str:
    stars = repo_data.get("stargazers_count", 0) if repo_data else 0
    pushed_at = (repo_data.get("pushed_at") or "")[:10] if repo_data else ""
    lang = spec["lang"]
    lang_color = LANG_COLORS.get(lang, spec["accent"])
    accent = spec["accent"]
    accent2 = spec["accent2"]

    star_label = f"★ {stars}" if stars > 0 else "ACTIVE"
    star_bg = "#FBBF24" if stars > 0 else "#34D399"
    date_text = f"Updated {pushed_at}" if pushed_at else "Actively Maintained"
    badge_w = max(136, round(len(spec["badge"]) * 7.0 + 26))
    date_x = 24 + badge_w + 12

    tags_svg = []
    cur_x = 24
    for tag in spec["tags"]:
        tw = max(56, len(tag) * 7.6 + 22)
        tags_svg.append(
            f'<rect x="{cur_x}" y="128" width="{tw:.0f}" height="22" rx="6" fill="#1E293B" fill-opacity="0.9" stroke="#334155" stroke-opacity="0.8"/>'
            f'<text x="{cur_x + tw / 2:.1f}" y="143" text-anchor="middle" class="mono" font-size="10.5" fill="#CBD5E1">{html.escape(tag)}</text>'
        )
        cur_x += tw + 8

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 580 168" width="580" height="168" fill="none">
  <defs>
    <linearGradient id="bg-{spec['slug']}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#090E1A"/>
      <stop offset="100%" stop-color="#0F172A"/>
    </linearGradient>
    <linearGradient id="bar-{spec['slug']}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{accent}"/>
      <stop offset="100%" stop-color="{accent2}"/>
    </linearGradient>
    <radialGradient id="glow-{spec['slug']}" cx="15%" cy="15%" r="55%">
      <stop offset="0%" stop-color="{accent}" stop-opacity="0.16"/>
      <stop offset="100%" stop-color="#090E1A" stop-opacity="0"/>
    </radialGradient>
    <clipPath id="clip-{spec['slug']}">
      <rect x="0" y="0" width="580" height="168" rx="16"/>
    </clipPath>
  </defs>
  <style>
    .mono {{ font-family: "SF Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
    .sans {{ font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; }}
  </style>

  <g clip-path="url(#clip-{spec['slug']})">
    <rect width="580" height="168" rx="16" fill="url(#bg-{spec['slug']})"/>
    <rect width="580" height="168" rx="16" fill="url(#glow-{spec['slug']})"/>
    <rect x="0" y="0" width="580" height="3.5" fill="url(#bar-{spec['slug']})"/>
    <rect x="1" y="1" width="578" height="166" rx="16" stroke="{accent}" stroke-opacity="0.35" stroke-width="1.2"/>

    <!-- Header -->
    <circle cx="30" cy="36" r="5" fill="{lang_color}"/>
    <text x="44" y="41" class="sans" font-size="19" font-weight="700" fill="#F8FAFC">{html.escape(spec['title'])}</text>

    <!-- Category Pill -->
    <rect x="24" y="54" width="{badge_w}" height="20" rx="10" fill="{accent}" fill-opacity="0.14" stroke="{accent}" stroke-opacity="0.4"/>
    <text x="{24 + badge_w / 2:.1f}" y="68" text-anchor="middle" class="mono" font-size="10.5" font-weight="600" fill="{accent}">{html.escape(spec['badge'])}</text>
    <text x="{date_x}" y="68" class="mono" font-size="10.5" fill="#64748B">{html.escape(date_text)}</text>

    <!-- Top Right Status / Stars Pill -->
    <rect x="466" y="23" width="90" height="24" rx="12" fill="{star_bg}" fill-opacity="0.15" stroke="{star_bg}" stroke-opacity="0.5"/>
    <circle cx="481" cy="35" r="3" fill="{star_bg}">
      <animate attributeName="opacity" values="1;0.35;1" dur="2.2s" repeatCount="indefinite"/>
    </circle>
    <text x="519" y="39" text-anchor="middle" class="mono" font-size="11" font-weight="700" fill="{star_bg}">{html.escape(star_label)}</text>

    <!-- Description -->
    <text x="24" y="94" class="sans" font-size="13" fill="#CBD5E1">{html.escape(spec['line1'])}</text>
    <text x="24" y="114" class="sans" font-size="13" fill="#94A3B8">{html.escape(spec['line2'])}</text>

    <!-- Tags -->
    {''.join(tags_svg)}
  </g>
</svg>
"""


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    user = github_get(f"users/{USERNAME}")
    repos = fetch_all_repos()
    repo_map = {r["name"]: r for r in repos}

    (ASSETS_DIR / "overview-stats.svg").write_text(
        render_overview_svg(user, repos), encoding="utf-8"
    )

    for spec in FLAGSHIP_SPECS:
        card_svg = render_project_card(spec, repo_map.get(spec["repo"]))
        (ASSETS_DIR / f"card-{spec['slug']}.svg").write_text(card_svg, encoding="utf-8")

    print(f"Generated overview-stats.svg and {len(FLAGSHIP_SPECS)} project cards.")


if __name__ == "__main__":
    main()
