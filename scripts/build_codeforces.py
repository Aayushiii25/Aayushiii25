#!/usr/bin/env python3
"""
build_codeforces_heatmap.py
Generates the codeforces.svg contribution heatmap widget.
Uses a blue-to-purple intensity scale for accepted submissions.
Supports card themes and includes custom data attributes for future snake overlay animation.
"""

import os
import sys
import json
import argparse
import datetime
from string import Template

THEMES = {
    "matrix-green": {
        "bg": "#0d1117",
        "accent": "#39ff14",
        "border": "#1b4d1b",
        "glow": "#39ff14",
        "text_primary": "#ffffff",
        "text_secondary": "#8b949e",
        "level_0": "#161b22",
    },
    "cyber-purple": {
        "bg": "#0c0714",
        "accent": "#bd00ff",
        "border": "#4e126b",
        "glow": "#bd00ff",
        "text_primary": "#ffffff",
        "text_secondary": "#a599b5",
        "level_0": "#1b1429",
    },
    "github-dark": {
        "bg": "#0d1117",
        "accent": "#58a6ff",
        "border": "#30363d",
        "glow": "#58a6ff",
        "text_primary": "#ffffff",
        "text_secondary": "#8b949e",
        "level_0": "#161b22",
    }
}

# Blue-to-purple intensity scale for Codeforces activity
CF_CELL_COLORS = {
    "level_0_matrix": "#161b22",
    "level_0_cyber": "#1b1429",
    "level_0_github": "#161b22",
    "level_1": "#1e3a8a",  # Dark Blue
    "level_2": "#3b82f6",  # Bright Blue
    "level_3": "#8b5cf6",  # Vibrant Purple
    "level_4": "#d946ef"   # Glowing Fuchsia
}

SVG_TEMPLATE = Template("""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 740 170" width="740" height="170">
  <defs>
    <style>
      .bg { fill: $bg; }
      .border { stroke: $border; stroke-width: 1.5; fill: none; }
      .glow-border { stroke: $accent; stroke-width: 1.5; fill: none; filter: url(#glow); opacity: 0.4; }
      .header-line { stroke: $border; stroke-width: 1; }
      .header-text { font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace; font-size: 11px; fill: $accent; opacity: 0.7; }
      
      .label-text { font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace; font-size: 9px; fill: $text_secondary; }
      .legend-text { font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace; font-size: 10px; fill: $text_secondary; }
      .stats-text { font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace; font-size: 10px; fill: $text_secondary; opacity: 0.8; }
      
      .cell { stroke: rgba(0, 0, 0, 0.15); stroke-width: 0.5px; }
      .cell-active { transition: transform 0.1s ease, filter 0.1s ease; cursor: pointer; }
      .cell-active:hover { transform: scale(1.2); transform-origin: center; filter: brightness(1.2) drop-shadow(0 0 4px $cell_glow); }
      .cell-future { fill: $level_0; opacity: 0.2; }
      
      .footer-text { font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace; font-size: 9px; fill: $text_secondary; opacity: 0.5; }
      
      .interactive-panel { transition: all 0.3s ease; }
      .interactive-panel:hover { filter: drop-shadow(0 0 8px $accent); }
    </style>
    
    <!-- Neon Glowing Filters -->
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>

  <!-- Background and Border -->
  <g class="interactive-panel">
    <rect class="bg" width="738" height="168" x="1" y="1" rx="8" ry="8" />
    <rect class="glow-border" width="738" height="168" x="1" y="1" rx="8" ry="8" />
    <rect class="border" width="738" height="168" x="1" y="1" rx="8" ry="8" />
  </g>

  <!-- Terminal Header -->
  <g>
    <circle cx="20" cy="16" r="4.5" fill="#ff5f56" />
    <circle cx="34" cy="16" r="4.5" fill="#ffbd2e" />
    <circle cx="48" cy="16" r="4.5" fill="#27c93f" />
    <text x="370" y="20" text-anchor="middle" class="header-text">$handle@codeforces-heatmap:~</text>
    <line x1="1" y1="32" x2="739" y2="32" class="header-line" />
  </g>

  <!-- Month Labels -->
  <g transform="translate(35, 0)">
    $month_labels_svg
  </g>

  <!-- Day Labels (Mon, Wed, Fri) -->
  <g>
    <text x="18" y="69" class="label-text" text-anchor="middle">Mon</text>
    <text x="18" y="95" class="label-text" text-anchor="middle">Wed</text>
    <text x="18" y="121" class="label-text" text-anchor="middle">Fri</text>
  </g>

  <!-- Heatmap Grid -->
  <g transform="translate(35, 48)">
    $cells_svg
  </g>

  <!-- Footer Stats and Legend -->
  <g transform="translate(15, 152)">
    <!-- Solved count summary -->
    <text x="0" y="0" class="stats-text">$total_accepted accepted submissions in the last year</text>
    
    <!-- Legend -->
    <g transform="translate(560, -9)">
      <text x="-32" y="8" class="legend-text" text-anchor="end">Less</text>
      <rect x="-24" y="0" width="8" height="8" rx="1.5" fill="$level_0" />
      <rect x="-13" y="0" width="8" height="8" rx="1.5" fill="$level_1" />
      <rect x="-2" y="0" width="8" height="8" rx="1.5" fill="$level_2" />
      <rect x="9" y="0" width="8" height="8" rx="1.5" fill="$level_3" />
      <rect x="20" y="0" width="8" height="8" rx="1.5" fill="$level_4" />
      <text x="34" y="8" class="legend-text" text-anchor="start">More</text>
    </g>
    
    <text x="355" y="0" text-anchor="middle" class="footer-text">REFRESHED: $refreshed_time</text>
  </g>
</svg>""")

def build_codeforces_heatmap(theme_name):
    # Select card theme
    theme = THEMES.get(theme_name, THEMES["matrix-green"])

    # Map the level_0 color based on theme
    if theme_name == "cyber-purple":
        level_0_color = CF_CELL_COLORS["level_0_cyber"]
    else:
        level_0_color = CF_CELL_COLORS["level_0_matrix"]

    # Load cached data
    codeforces_path = "data/codeforces_data.json"
    if os.path.exists(codeforces_path):
        with open(codeforces_path, "r", encoding="utf-8") as f:
            cf = json.load(f)
    else:
        cf = {"handle": "Guest", "submission_calendar": {}}

    handle = cf.get("handle", "Guest")

    # Map submission calendar to date objects
    codeforces_dates = {}
    for date_str, count in cf.get("submission_calendar", {}).items():
        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            codeforces_dates[date_obj] = count
        except ValueError:
            continue

    # Set up date range
    today = datetime.datetime.now(datetime.timezone.utc).date()
    start_date = today - datetime.timedelta(days=364)
    
    # Align to Sunday before/on start_date
    days_to_sunday = (start_date.weekday() + 1) % 7
    grid_start_date = start_date - datetime.timedelta(days=days_to_sunday)

    # Build the 53 weeks x 7 days grid (371 days)
    cells_list = []
    total_accepted = 0
    
    month_labels_list = []
    last_month_name = None
    last_month_col = -5

    for day_idx in range(371):
        current_date = grid_start_date + datetime.timedelta(days=day_idx)
        col = day_idx // 7
        row = day_idx % 7
        
        # Coordinates (cell size = 10, gap = 3)
        x = col * 13
        y = row * 13
        
        date_str = current_date.strftime("%Y-%m-%d")
        
        # Track month label at the start of each column
        if row == 0:
            month_name = current_date.strftime("%b")
            if month_name != last_month_name and col - last_month_col >= 3:
                month_labels_list.append(
                    f'<text x="{x}" y="42" class="label-text" text-anchor="start">{month_name}</text>'
                )
                last_month_name = month_name
                last_month_col = col

        # Determine accepted count and level
        if current_date > today:
            # Future days inside the current week
            color = level_0_color
            count = 0
            hover_class = "cell-future"
        else:
            count = codeforces_dates.get(current_date, 0)
            total_accepted += count
            
            if count == 0:
                color = level_0_color
                level_cf = 0
            else:
                if count == 1:
                    level_cf = 1
                elif count <= 3:
                    level_cf = 2
                elif count <= 6:
                    level_cf = 3
                else:
                    level_cf = 4
                color = CF_CELL_COLORS[f"level_{level_cf}"]
                
            hover_class = "cell-active"

        cell_svg = (
            f'<rect class="cell {hover_class}" x="{x}" y="{y}" width="10" height="10" rx="2" ry="2" '
            f'fill="{color}" data-date="{date_str}" data-count="{count}" data-col="{col}" data-row="{row}" />'
        )
        cells_list.append(cell_svg)

    refreshed_time = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Interpolate template
    svg_content = SVG_TEMPLATE.substitute(
        bg=theme["bg"],
        accent=theme["accent"],
        border=theme["border"],
        glow=theme["glow"],
        text_primary=theme["text_primary"],
        text_secondary=theme["text_secondary"],
        level_0=level_0_color,
        level_1=CF_CELL_COLORS["level_1"],
        level_2=CF_CELL_COLORS["level_2"],
        level_3=CF_CELL_COLORS["level_3"],
        level_4=CF_CELL_COLORS["level_4"],
        cell_glow=CF_CELL_COLORS["level_3"],
        handle=handle,
        total_accepted=total_accepted,
        month_labels_svg="\n    ".join(month_labels_list),
        cells_svg="\n    ".join(cells_list),
        refreshed_time=refreshed_time
    )

    # Save SVG file
    output_dir = "widgets"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "codeforces.svg")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"Successfully generated codeforces.svg in {output_path} using theme: {theme_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build Codeforces Heatmap SVG.")
    parser.add_argument(
        "--theme",
        default="matrix-green",
        choices=["matrix-green", "cyber-purple", "github-dark"],
        help="Color theme for the heatmap container border and title"
    )
    args = parser.parse_args()
    build_codeforces_heatmap(args.theme)
