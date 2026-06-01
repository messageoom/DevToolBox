"""
macOS-style lock page for unauthorized access.
Pure HTML/CSS/JS -- no external dependencies.
Supports bilingual text (zh / en) via .format() placeholders.
"""

TRANSLATIONS = {
    "zh": {
        "html_lang": "zh",
        "title": "DevToolBox - 需要授权",
        "card_title": "需要授权",
        "subtitle": "此 DevToolBox 需要授权才能访问。请从终端获取访问URL。",
        "hint": "启动应用程序获取访问URL",
        "footer": "DevToolBox &mdash; 本地优先的开发工具箱",
    },
    "en": {
        "html_lang": "en",
        "title": "DevToolBox - Authorization Required",
        "card_title": "Authorization Required",
        "subtitle": "This DevToolBox requires authorization to access.<br>Please get the access URL from the terminal.",
        "hint": "Start the application to get your access URL",
        "footer": "DevToolBox &mdash; Local-First Developer Toolkit",
    },
}

LOCK_PAGE_TEMPLATE = '''<!DOCTYPE html>
<html lang="{html_lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  *, *::before, *::after {{ margin: 0; padding: 0; box-sizing: border-box; }}

  :root {{
    --bg: #1d1d1f;
    --card: rgba(255, 255, 255, 0.05);
    --card-border: rgba(255, 255, 255, 0.08);
    --text: #f5f5f7;
    --text-dim: rgba(245, 245, 247, 0.5);
    --accent: #0071e3;
    --glow: rgba(0, 113, 227, 0.15);
  }}

  body {{
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    overflow: hidden;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }}

  /* Animated gradient background */
  .bg-layer {{
    position: fixed;
    inset: 0;
    z-index: 0;
    background:
      radial-gradient(ellipse 80% 60% at 20% 80%, rgba(0, 113, 227, 0.08) 0%, transparent 60%),
      radial-gradient(ellipse 60% 80% at 80% 20%, rgba(88, 86, 214, 0.06) 0%, transparent 60%),
      radial-gradient(ellipse 50% 50% at 50% 50%, rgba(0, 113, 227, 0.03) 0%, transparent 70%);
    animation: bgShift 12s ease-in-out infinite alternate;
  }}

  @keyframes bgShift {{
    0%   {{ opacity: 0.6; transform: scale(1); }}
    50%  {{ opacity: 1;   transform: scale(1.05); }}
    100% {{ opacity: 0.6; transform: scale(1); }}
  }}

  /* Floating particles */
  .particles {{
    position: fixed;
    inset: 0;
    z-index: 1;
    pointer-events: none;
  }}

  .particle {{
    position: absolute;
    width: 2px;
    height: 2px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.15);
    animation: particleFloat linear infinite;
  }}

  .particle:nth-child(1)  {{ left: 10%; top: 20%; animation-duration: 18s; animation-delay: 0s; }}
  .particle:nth-child(2)  {{ left: 25%; top: 60%; animation-duration: 22s; animation-delay: 2s; width: 3px; height: 3px; }}
  .particle:nth-child(3)  {{ left: 40%; top: 35%; animation-duration: 16s; animation-delay: 4s; }}
  .particle:nth-child(4)  {{ left: 55%; top: 75%; animation-duration: 20s; animation-delay: 1s; width: 1.5px; height: 1.5px; }}
  .particle:nth-child(5)  {{ left: 70%; top: 15%; animation-duration: 24s; animation-delay: 3s; }}
  .particle:nth-child(6)  {{ left: 85%; top: 50%; animation-duration: 19s; animation-delay: 5s; width: 2.5px; height: 2.5px; }}
  .particle:nth-child(7)  {{ left: 15%; top: 85%; animation-duration: 21s; animation-delay: 2.5s; }}
  .particle:nth-child(8)  {{ left: 60%; top: 40%; animation-duration: 17s; animation-delay: 0.5s; width: 1px; height: 1px; }}
  .particle:nth-child(9)  {{ left: 35%; top: 10%; animation-duration: 23s; animation-delay: 4.5s; }}
  .particle:nth-child(10) {{ left: 90%; top: 80%; animation-duration: 15s; animation-delay: 1.5s; width: 2px; height: 2px; }}

  @keyframes particleFloat {{
    0%   {{ transform: translateY(0) translateX(0); opacity: 0; }}
    10%  {{ opacity: 1; }}
    90%  {{ opacity: 1; }}
    100% {{ transform: translateY(-100vh) translateX(30px); opacity: 0; }}
  }}

  /* Main card */
  .card {{
    position: relative;
    z-index: 2;
    width: 380px;
    padding: 48px 40px;
    background: var(--card);
    border: 1px solid var(--card-border);
    border-radius: 20px;
    backdrop-filter: blur(40px) saturate(180%);
    -webkit-backdrop-filter: blur(40px) saturate(180%);
    text-align: center;
    animation: cardFadeIn 0.8s ease-out both;
    box-shadow:
      0 0 0 0.5px rgba(255, 255, 255, 0.04),
      0 20px 60px rgba(0, 0, 0, 0.4),
      0 0 80px var(--glow);
  }}

  @keyframes cardFadeIn {{
    from {{ opacity: 0; transform: translateY(20px) scale(0.96); }}
    to   {{ opacity: 1; transform: translateY(0) scale(1); }}
  }}

  /* Lock icon */
  .icon-wrap {{
    width: 64px;
    height: 64px;
    margin: 0 auto 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: rgba(0, 113, 227, 0.08);
    border: 1px solid rgba(0, 113, 227, 0.15);
    animation: iconPulse 3s ease-in-out infinite;
  }}

  .icon-wrap svg {{
    width: 28px;
    height: 28px;
    stroke: var(--accent);
    fill: none;
    stroke-width: 1.5;
    stroke-linecap: round;
    stroke-linejoin: round;
  }}

  @keyframes iconPulse {{
    0%, 100% {{ box-shadow: 0 0 0 0 rgba(0, 113, 227, 0); }}
    50%      {{ box-shadow: 0 0 0 12px rgba(0, 113, 227, 0.06); }}
  }}

  .title {{
    font-size: 20px;
    font-weight: 600;
    letter-spacing: -0.02em;
    margin-bottom: 10px;
    color: var(--text);
  }}

  .subtitle {{
    font-size: 14px;
    line-height: 1.5;
    color: var(--text-dim);
    margin-bottom: 32px;
  }}

  .divider {{
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--card-border), transparent);
    margin-bottom: 24px;
  }}

  .hint {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    font-size: 12px;
    color: var(--text-dim);
  }}

  .hint svg {{
    width: 14px;
    height: 14px;
    stroke: var(--text-dim);
    fill: none;
    stroke-width: 1.5;
    stroke-linecap: round;
    stroke-linejoin: round;
    flex-shrink: 0;
  }}

  /* Footer */
  .footer {{
    position: fixed;
    bottom: 24px;
    left: 0;
    right: 0;
    text-align: center;
    z-index: 2;
    font-size: 11px;
    color: rgba(255, 255, 255, 0.15);
    animation: cardFadeIn 1s ease-out 0.3s both;
  }}
</style>
</head>
<body>
  <div class="bg-layer"></div>
  <div class="particles">
    <div class="particle"></div>
    <div class="particle"></div>
    <div class="particle"></div>
    <div class="particle"></div>
    <div class="particle"></div>
    <div class="particle"></div>
    <div class="particle"></div>
    <div class="particle"></div>
    <div class="particle"></div>
    <div class="particle"></div>
  </div>

  <div class="card">
    <div class="icon-wrap">
      <svg viewBox="0 0 24 24">
        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
        <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
      </svg>
    </div>
    <div class="title">{card_title}</div>
    <div class="subtitle">{subtitle}</div>
    <div class="divider"></div>
    <div class="hint">
      <svg viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="16" x2="12" y2="12"/>
        <line x1="12" y1="8" x2="12.01" y2="8"/>
      </svg>
      {hint}
    </div>
  </div>

  <div class="footer">{footer}</div>
</body>
</html>'''


def get_lock_page_html(lang='zh'):
    t = TRANSLATIONS.get(lang, TRANSLATIONS['zh'])
    return LOCK_PAGE_TEMPLATE.format(
        html_lang=t['html_lang'],
        title=t['title'],
        card_title=t['card_title'],
        subtitle=t['subtitle'],
        hint=t['hint'],
        footer=t['footer'],
    )
