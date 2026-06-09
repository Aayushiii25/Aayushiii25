#!/usr/bin/env python3
"""
build_dashboard.py
Generates the dashboard.svg widget summarizing LeetCode and Codeforces statistics.
Supports custom themes (matrix-green, cyber-purple, github-dark).
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
        "bar_bg": "#161b22",
        "easy": "#39ff14",
        "medium": "#ffb703",
        "hard": "#ff006e"
    },
    "cyber-purple": {
        "bg": "#0c0714",
        "accent": "#bd00ff",
        "border": "#4e126b",
        "glow": "#bd00ff",
        "text_primary": "#ffffff",
        "text_secondary": "#a599b5",
        "bar_bg": "#1b1429",
        "easy": "#00f0ff",
        "medium": "#bd00ff",
        "hard": "#ff007f"
    },
    "github-dark": {
        "bg": "#0d1117",
        "accent": "#58a6ff",
        "border": "#30363d",
        "glow": "#58a6ff",
        "text_primary": "#ffffff",
        "text_secondary": "#8b949e",
        "bar_bg": "#161b22",
        "easy": "#2ea44f",
        "medium": "#dbab09",
        "hard": "#d73a49"
    }
}

SVG_TEMPLATE = Template("""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 $view_width 250" width="$view_width" height="250">
  <defs>
    <style>
      .bg { fill: $bg; }
      .border { stroke: $border; stroke-width: 1.5; fill: none; }
      .glow-border { stroke: $accent; stroke-width: 1.5; fill: none; filter: url(#glow); opacity: 0.4; }
      .header-line { stroke: $border; stroke-width: 1; }
      .header-text { font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace; font-size: 11px; fill: $accent; opacity: 0.7; }
      
      .terminal-prompt { font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace; font-weight: bold; font-size: 12px; fill: $accent; }
      .terminal-command { font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace; font-size: 12px; fill: $text_primary; }
      
      .stat-label { font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace; font-size: 12px; fill: $text_secondary; }
      .stat-val { font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace; font-weight: bold; font-size: 12px; fill: $text_primary; }
      .stat-highlight { font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace; font-weight: bold; font-size: 12px; fill: $accent; filter: url(#glow-soft); }
      
      .bar-bg { fill: $bar_bg; rx: 3px; ry: 3px; }
      .bar-easy { fill: $easy; rx: 3px; ry: 3px; filter: url(#glow-easy); }
      .bar-medium { fill: $medium; rx: 3px; ry: 3px; filter: url(#glow-medium); }
      .bar-hard { fill: $hard; rx: 3px; ry: 3px; filter: url(#glow-hard); }
      
      .footer-text { font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace; font-size: 10px; fill: $text_secondary; opacity: 0.5; }
      
      /* Hover interactions */
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
    <filter id="glow-soft" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="1.5" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
    <filter id="glow-easy" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="1" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
    <filter id="glow-medium" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="1" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
    <filter id="glow-hard" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="1" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>

  <!-- Background and Border -->
  <g class="interactive-panel">
    <rect class="bg" width="$rect_width" height="248" x="1" y="1" rx="8" ry="8" />
    <rect class="glow-border" width="$rect_width" height="248" x="1" y="1" rx="8" ry="8" />
    <rect class="border" width="$rect_width" height="248" x="1" y="1" rx="8" ry="8" />
  </g>

  <!-- Terminal Header -->
  <g>
    <!-- Window Controls (Red, Yellow, Green) -->
    <circle cx="20" cy="16" r="4.5" fill="#ff5f56" />
    <circle cx="34" cy="16" r="4.5" fill="#ffbd2e" />
    <circle cx="48" cy="16" r="4.5" fill="#27c93f" />
    
    <!-- Title -->
    <text x="$title_x" y="20" text-anchor="middle" class="header-text">guest@cp-dashboard:~</text>
    <line x1="1" y1="32" x2="$line_x2" y2="32" class="header-line" />
  </g>

  <!-- Left Column: LeetCode -->
  <a href="https://leetcode.com/u/$lc_username" target="_blank">
    <g transform="translate(25, 50)">
      <!-- Command Line Prompt -->
      <text x="0" y="12" class="terminal-prompt">$$ <tspan class="terminal-command">cat leetcode.json</tspan></text>
      <line x1="0" y1="20" x2="250" y2="20" class="header-line" opacity="0.3" />
      
      <!-- Stats -->
      <text x="0" y="40" class="stat-label">Solved Total:</text>
      <text x="250" y="40" text-anchor="end" class="stat-highlight">$solved_all / $total_questions</text>
      
      <!-- Easy -->
      <text x="0" y="65" class="stat-label">Easy:</text>
      <text x="250" y="65" text-anchor="end" class="stat-val">$solved_easy / $total_easy</text>
      <rect x="0" y="72" width="250" height="6" class="bar-bg" />
      <rect x="0" y="72" width="$easy_width" height="6" class="bar-easy" />

      <!-- Medium -->
      <text x="0" y="105" class="stat-label">Medium:</text>
      <text x="250" y="105" text-anchor="end" class="stat-val">$solved_medium / $total_medium</text>
      <rect x="0" y="112" width="250" height="6" class="bar-bg" />
      <rect x="0" y="112" width="$medium_width" height="6" class="bar-medium" />

      <!-- Hard -->
      <text x="0" y="145" class="stat-label">Hard:</text>
      <text x="250" y="145" text-anchor="end" class="stat-val">$solved_hard / $total_hard</text>
      <rect x="0" y="152" width="250" height="6" class="bar-bg" />
      <rect x="0" y="152" width="$hard_width" height="6" class="bar-hard" />
    </g>
  </a>

  <!-- Vertical Divider & Codeforces Column -->
  <g $cf_display>
    <!-- Vertical Divider -->
    <line x1="300" y1="42" x2="300" y2="215" class="header-line" opacity="0.3" />

    <!-- Right Column: Codeforces -->
    <a href="https://codeforces.com/profile/$cf_handle" target="_blank">
      <g transform="translate(325, 50)">
        <!-- Command Line Prompt -->
        <text x="0" y="12" class="terminal-prompt">$$ <tspan class="terminal-command">neofetch --codeforces</tspan></text>
        <line x1="0" y1="20" x2="250" y2="20" class="header-line" opacity="0.3" />
        
        <!-- Handle -->
        <text x="0" y="42" class="stat-label">Handle:</text>
        <text x="250" y="42" text-anchor="end" class="stat-val">$cf_handle</text>
        
        <!-- Solved Count -->
        <text x="0" y="72" class="stat-label">Solved Total:</text>
        <text x="250" y="72" text-anchor="end" class="stat-highlight">$cf_solved</text>
        
        <!-- Current Rating / Rank -->
        <text x="0" y="102" class="stat-label">Current Rating:</text>
        <text x="250" y="102" text-anchor="end" class="stat-val">$cf_rating ($cf_rank)</text>
        
        <!-- Max Rating / Rank -->
        <text x="0" y="132" class="stat-label">Max Rating:</text>
        <text x="250" y="132" text-anchor="end" class="stat-val">$cf_max_rating ($cf_max_rank)</text>
        
        <!-- Status Log -->
        <text x="0" y="162" class="stat-label">System State:</text>
        <text x="250" y="162" text-anchor="end" class="stat-val" fill="$accent" filter="url(#glow-soft)" opacity="0.95">ACTIVE</text>
      </g>
    </a>
  </g>

  <!-- Footer Line -->
  <line x1="1" y1="225" x2="$line_x2" y2="225" class="header-line" />
  
  <!-- Footer Refreshed Status -->
  <text x="15" y="239" class="footer-text">[SYSTEM STATUS: ONLINE]</text>
  <text x="$footer_x" y="239" text-anchor="end" class="footer-text">REFRESHED: $refreshed_time</text>
</svg>""")

def build_dashboard(theme_name):
    # Determine the theme dictionary
    theme = THEMES.get(theme_name, THEMES["matrix-green"])

    # Configuration flag: check HIDE_CODEFORCES from environment (default to true)
    hide_cf = os.environ.get("HIDE_CODEFORCES", "true").lower() == "true"

    # Load LeetCode cached data
    leetcode_path = "data/leetcode_data.json"
    if os.path.exists(leetcode_path):
        with open(leetcode_path, "r", encoding="utf-8") as f:
            lc = json.load(f)
    else:
        lc = {
            "username": "N/A", "total_questions": 0, "total_easy": 0, "total_medium": 0, "total_hard": 0,
            "solved_all": 0, "solved_easy": 0, "solved_medium": 0, "solved_hard": 0
        }

    # Load Codeforces cached data
    codeforces_path = "data/codeforces_data.json"
    if os.path.exists(codeforces_path):
        with open(codeforces_path, "r", encoding="utf-8") as f:
            cf = json.load(f)
    else:
        cf = {
            "handle": "N/A", "rating": 0, "rank": "unrated",
            "max_rating": 0, "max_rank": "unrated", "solved_count": 0
        }

    # Calculate LeetCode width values (maximum 250px)
    def calc_width(solved, total):
        if total <= 0:
            return 0
        ratio = solved / total
        return min(round(ratio * 250), 250)

    easy_width = calc_width(lc.get("solved_easy", 0), lc.get("total_easy", 0))
    medium_width = calc_width(lc.get("solved_medium", 0), lc.get("total_medium", 0))
    hard_width = calc_width(lc.get("solved_hard", 0), lc.get("total_hard", 0))

    # Formatter for timestamps
    refreshed_time = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Set up layout variables based on hide_cf flag
    if hide_cf:
        view_width = 300
        rect_width = 298
        title_x = 150
        line_x2 = 299
        cf_display = 'display="none"'
        footer_x = 285
    else:
        view_width = 600
        rect_width = 598
        title_x = 300
        line_x2 = 599
        cf_display = ''
        footer_x = 585

    # Render template values
    svg_content = SVG_TEMPLATE.substitute(
        bg=theme["bg"],
        accent=theme["accent"],
        border=theme["border"],
        glow=theme["glow"],
        text_primary=theme["text_primary"],
        text_secondary=theme["text_secondary"],
        bar_bg=theme["bar_bg"],
        easy=theme["easy"],
        medium=theme["medium"],
        hard=theme["hard"],
        view_width=view_width,
        rect_width=rect_width,
        title_x=title_x,
        line_x2=line_x2,
        cf_display=cf_display,
        footer_x=footer_x,
        solved_all=lc.get("solved_all", 0),
        total_questions=lc.get("total_questions", 0),
        solved_easy=lc.get("solved_easy", 0),
        total_easy=lc.get("total_easy", 0),
        easy_width=easy_width,
        solved_medium=lc.get("solved_medium", 0),
        total_medium=lc.get("total_medium", 0),
        medium_width=medium_width,
        solved_hard=lc.get("solved_hard", 0),
        total_hard=lc.get("total_hard", 0),
        hard_width=hard_width,
        lc_username=lc.get("username", "N/A"),
        cf_handle=cf.get("handle", "N/A"),
        cf_solved=cf.get("solved_count", 0),
        cf_rating=cf.get("rating", 0),
        cf_rank=cf.get("rank", "unrated").title(),
        cf_max_rating=cf.get("max_rating", 0),
        cf_max_rank=cf.get("max_rank", "unrated").title(),
        refreshed_time=refreshed_time
    )

    # Save SVG file
    output_dir = "widgets"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "dashboard.svg")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"Successfully generated dashboard.svg in {output_path} using theme: {theme_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build CP Dashboard SVG.")
    parser.add_argument(
        "--theme",
        default="matrix-green",
        choices=["matrix-green", "cyber-purple", "github-dark"],
        help="Color theme for the dashboard"
    )
    args = parser.parse_args()
    build_dashboard(args.theme)
