# UI Redesign — Navy & Gold Law-Firm Theme
## HackAgents BIU 2026 | Court Practice Simulator (מתמחה בבית המשפט)

---

## Goal

Replace the default Streamlit appearance with a Navy & Gold law-firm aesthetic: dark navy background, gold accents, serif typography, transcript-style chat messages, and a central ⚖ emblem header on every screen.

## Approach

Streamlit Theme Config (config.toml) handles the base shell colors. A focused CSS patch in `app.py` covers the custom components that config.toml cannot reach (emblem header, message border strips, textarea backgrounds). No structural changes to screen routing or orchestrator interface.

---

## Color Palette

| Role | Hex | Usage |
|---|---|---|
| Background | `#1a1a2e` | App background |
| Surface | `#111122` | Inputs, top bar, secondary bg |
| Surface raised | `#1e2550` | Judge message boxes |
| Surface red | `#231520` | Attorney message boxes |
| Surface slate | `#1e2535` | User message boxes |
| Gold | `#c9a84c` | Primary accent, buttons, emblem |
| Text primary | `#e8e0cc` | Body text |
| Text muted | `#8a8a9a` | Labels, secondary text |
| Text dim | `#3a3a5c` | Subtitles, decorative |
| Judge strip | `#c9a84c` | Right border on judge messages |
| Attorney strip | `#cc4444` | Right border on attorney messages |
| User strip | `#88aabb` | Right border on user messages |

---

## Files Changed

| File | Action | What changes |
|---|---|---|
| `.streamlit/config.toml` | **Create** | Base theme: background, text, primaryColor, font |
| `app.py` | **Modify** | Replace RTL-only CSS with full CSS patch; add `HEADER_HTML` constant and inject before router |
| `ui/chat_view.py` | **Modify** | `_render_message()` switches to transcript style (speaker label + right-border strip box) |
| `ui/setup_form.py` | **Modify** | No structural change; gold rule under section title |
| `ui/debrief_view.py` | **Modify** | Score cards get `border-top: 2px solid #c9a84c` via CSS class |

No changes to `core/orchestrator.py`, `agents/`, or any test files.

---

## `.streamlit/config.toml`

```toml
[theme]
base = "dark"
backgroundColor = "#1a1a2e"
secondaryBackgroundColor = "#111122"
textColor = "#e8e0cc"
primaryColor = "#c9a84c"
font = "serif"
```

---

## CSS Patch (`app.py`)

Injected once via `st.markdown(..., unsafe_allow_html=True)` before the screen router. Covers:

1. **RTL direction** — `body, .stApp, .stMarkdown { direction: rtl; text-align: right; }`
2. **Textarea/input backgrounds** — override Streamlit's default light inputs to `#111122`
3. **Message classes** — `.msg-judge`, `.msg-attorney`, `.msg-user` with colored `border-right` strips and matching dark backgrounds
4. **Divider** — `.gold-rule { background: #c9a84c; height: 1px; }`

---

## Emblem Header (`HEADER_HTML` in `app.py`)

A constant injected at the top of every screen (before the router calls `render()`):

```
        ⚖            ← 56×56px gold circle border, font-size 28px
  מתמחה בבית המשפט   ← color #c9a84c, letter-spacing 4px, uppercase
Court Practice Simulator  ← color #3a3a5c, italic, small
────────────────────────  ← 1px solid #c9a84c44 divider
```

Rendered as `st.markdown(HEADER_HTML, unsafe_allow_html=True)`.

---

## Chat View — Transcript Messages

Each message rendered by `_render_message(msg: dict)` (where `msg` has keys `role`, `content`, `speaker`) as two HTML elements:

**Speaker label line:**
```
🔵 כב׳ השופטת לוי:
```
Color: gold (judge) / `#cc4444` (attorney) / `#88aabb` (user). Font-size 10px, letter-spacing 1px, uppercase.

**Message box:**
```html
<div class="msg-{role}">
  {content}
</div>
```

CSS per role:
- `.msg-judge`    → `background:#1e2550; border-right:3px solid #c9a84c`
- `.msg-attorney` → `background:#231520; border-right:3px solid #cc4444`
- `.msg-user`     → `background:#1e2535; border-right:3px solid #88aabb`

All share: `padding:10px 14px; font-size:13px; line-height:1.6; border-radius:1px`.

---

## Setup Form

No structural changes. The gold `primaryColor` in config.toml makes the "בחן אותי!" button gold automatically. A thin `st.markdown('<div class="gold-rule"></div>', unsafe_allow_html=True)` is added under the section title for visual polish.

---

## Debrief View

Score metric cards (`st.metric`) inherit theme colors automatically. A CSS rule adds a gold top border:

```css
[data-testid="stMetric"] {
  border-top: 2px solid #c9a84c;
  background: #111122;
  padding: 12px 8px;
}
```

Section titles (`###`) render in the default `textColor` (`#e8e0cc`); no additional styling needed.

---

## Testing

No new tests required — the existing 12 tests cover behavior, not appearance. Verify visually by running `streamlit run app.py` after implementation and checking all three screens match the mockup.

The mockup is saved at `.superpowers/brainstorm/` for reference.
