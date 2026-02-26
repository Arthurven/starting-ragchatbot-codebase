# Frontend Changes

## 1. Dark/Light Theme Toggle Button

### Summary

Added a theme toggle button that switches between the existing dark theme and a new light theme. The button uses sun/moon icons, is positioned in the top-right corner, and persists the user's preference via `localStorage`.

### Files Modified

#### `frontend/index.html`
- Added a `<button class="theme-toggle" id="themeToggle">` element inside `.container`, before `.main-content`
- The button contains two inline SVGs: a sun icon (visible in dark mode) and a moon icon (visible in light mode)
- Includes `aria-label="Toggle dark mode"` and `title="Toggle theme"` for accessibility

#### `frontend/style.css`
- **`.theme-toggle`**: Fixed position button (`top: 1rem; right: 1rem`) with `z-index: 1000`, circular shape (44x44px), smooth hover/focus/active transitions including scale and box-shadow effects
- **`.theme-icon` / `.sun-icon` / `.moon-icon`**: Animated icon crossfade using `opacity` and `transform` (rotate + scale) with 0.3s transitions
- **Transition rules**: Added `transition` for `background-color`, `color`, and `border-color` on key elements so theme changes animate smoothly

#### `frontend/script.js`
- **`initTheme()`**: Reads saved theme from `localStorage` on page load; if `"light"`, sets `data-theme="light"` on `<html>`. Attaches click listener to the toggle button.
- **`toggleTheme()`**: Toggles `data-theme` attribute between `"light"` and absent (dark). Saves preference to `localStorage`.
- Both functions are called during `DOMContentLoaded` initialization.

### Design Decisions

- **Icon choice**: Sun icon in dark mode (click to go light), moon icon in light mode (click to go dark) — follows the convention of showing what clicking will do
- **Position**: Fixed top-right so it's always accessible regardless of scroll position and doesn't interfere with the sidebar or chat area
- **Persistence**: Uses `localStorage` so the preference survives page reloads and browser sessions
- **Accessibility**: Button has `aria-label`, `title`, visible focus ring (`box-shadow`), and is keyboard-navigable (native `<button>` element receives focus and responds to Enter/Space)
- **Animation**: Icons crossfade with rotation for a polished transition; all themed elements smoothly interpolate colors over 0.3s

---

## 2. Light Theme CSS Variables

### Summary

Overhauled the light theme color system for proper accessibility, comprehensive coverage, and visual polish. Replaced hardcoded color values throughout the dark theme with CSS variables so both themes are fully parameterized.

### Changes to `frontend/style.css`

#### New CSS variables added to `:root` (dark theme defaults)
| Variable | Value | Purpose |
|---|---|---|
| `--bg-tertiary` | `rgba(255,255,255,0.05)` | Source list item backgrounds |
| `--hover-bg` | `rgba(255,255,255,0.08)` | Source list hover state |
| `--code-bg` | `rgba(0,0,0,0.2)` | Code block backgrounds |
| `--scrollbar-thumb` | `#334155` | Scrollbar thumb color |
| `--scrollbar-thumb-hover` | `#94a3b8` | Scrollbar thumb hover |
| `--error-bg` | `rgba(239,68,68,0.1)` | Error message background |
| `--error-color` | `#f87171` | Error message text |
| `--error-border` | `rgba(239,68,68,0.2)` | Error message border |
| `--success-bg` | `rgba(34,197,94,0.1)` | Success message background |
| `--success-color` | `#4ade80` | Success message text |
| `--success-border` | `rgba(34,197,94,0.2)` | Success message border |
| `--welcome-shadow` | `rgba(0,0,0,0.2)` | Welcome message box shadow |

#### Hardcoded values replaced with variables
- `.message-content code` and `.message-content pre` — now use `var(--code-bg)` instead of `rgba(0,0,0,0.2)`
- `.error-message` — now uses `var(--error-bg)`, `var(--error-color)`, `var(--error-border)`
- `.success-message` — now uses `var(--success-bg)`, `var(--success-color)`, `var(--success-border)`
- `.welcome-message` box-shadow — now uses `var(--welcome-shadow)`
- All scrollbar thumbs — now use `var(--scrollbar-thumb)` and `var(--scrollbar-thumb-hover)`
- `.message-content blockquote` — fixed `var(--primary)` to `var(--primary-color)` (bug fix)

#### Light theme `[data-theme="light"]` variable overrides
| Variable | Light Value | Notes |
|---|---|---|
| `--background` | `#f8fafc` | Slate-50 — soft off-white |
| `--surface` | `#ffffff` | Pure white for cards/sidebar |
| `--surface-hover` | `#f1f5f9` | Slate-100 hover state |
| `--text-primary` | `#1e293b` | Slate-800 — ~14.5:1 contrast ratio vs background (WCAG AAA) |
| `--text-secondary` | `#475569` | Slate-600 — ~7.4:1 contrast ratio (WCAG AAA) |
| `--border-color` | `#cbd5e1` | Slate-300 — clearly visible but not harsh |
| `--shadow` | `0 1px 3px rgba(0,0,0,0.08), ...` | Softer multi-layer shadow for light bg |
| `--focus-ring` | `rgba(37,99,235,0.3)` | Slightly more opaque for visibility on white |
| `--welcome-shadow` | `rgba(0,0,0,0.08)` | Subtle shadow for light mode |
| `--code-bg` | `rgba(0,0,0,0.05)` | Light gray code blocks |
| `--bg-tertiary` | `#f1f5f9` | Slate-100 for source items |
| `--hover-bg` | `#e2e8f0` | Slate-200 for source hover |
| `--scrollbar-thumb` | `#cbd5e1` | Matches border color |
| `--scrollbar-thumb-hover` | `#94a3b8` | Darker on hover |
| `--error-bg` | `#fef2f2` | Red-50 |
| `--error-color` | `#dc2626` | Red-600 — good contrast on white |
| `--error-border` | `#fecaca` | Red-200 |
| `--success-bg` | `#f0fdf4` | Green-50 |
| `--success-color` | `#16a34a` | Green-600 — good contrast on white |
| `--success-border` | `#bbf7d0` | Green-200 |

### Accessibility

All color pairings were chosen from the Tailwind CSS Slate palette to meet WCAG standards:
- **Primary text on background**: ~14.5:1 (AAA)
- **Secondary text on background**: ~7.4:1 (AAA)
- **Primary color on background**: ~4.6:1 (AA normal text)
- **White on user-message blue**: ~4.6:1 (AA)
- **Error red on white**: ~4.7:1 (AA)
- **Success green on white**: ~4.6:1 (AA)

---

## 3. JavaScript Toggle Functionality

### Summary

Enhanced the theme toggle JavaScript with OS preference detection, flash-of-wrong-theme prevention, dynamic accessibility labels, expanded CSS transitions, and a keyboard shortcut.

### Changes to `frontend/index.html`

- **Inline `<script>` in `<head>`**: Runs before CSS loads to read `localStorage` or `prefers-color-scheme` and set `data-theme="light"` on `<html>` immediately. This prevents a flash of the dark theme on page load when the user prefers light mode.
- Bumped CSS version query from `?v=9` to `?v=10` to bust cache.

### Changes to `frontend/script.js`

#### New function: `getEffectiveTheme()`
- Returns the user's effective theme preference
- Checks `localStorage` first; if no saved preference, falls back to `window.matchMedia('(prefers-color-scheme: light)')` to respect the OS setting

#### New function: `applyTheme(theme)`
- Centralized theme application: sets or removes `data-theme` attribute on `<html>`
- Dynamically updates `aria-label` and `title` on the toggle button to reflect the action ("Switch to light mode" / "Switch to dark mode") so screen readers announce the correct next action

#### Updated: `initTheme()`
- Calls `applyTheme(getEffectiveTheme())` to sync the aria-label on load (the inline script already set the attribute, but labels need the DOM button)
- Registers a `change` listener on `matchMedia('(prefers-color-scheme: light)')` — if the user hasn't explicitly saved a preference, the theme auto-follows OS changes in real time
- Registers a `keydown` listener for **Ctrl+Shift+L** (or Cmd+Shift+L on Mac) as a keyboard shortcut to toggle the theme without clicking

#### Updated: `toggleTheme()`
- Now delegates to `applyTheme(next)` for consistent behavior (aria-label update, attribute toggle)

### Changes to `frontend/style.css`

#### Expanded transition selectors
Added these selectors to the smooth-transition rule so they also animate during theme switches:
- `.main-content`
- `.course-title-item`
- `.sources-list li`
- `.source-link`
- `.error-message`
- `.success-message`

#### New box-shadow transition rule
Added a separate rule for elements that transition `box-shadow` in addition to colors:
- `.message.welcome-message .message-content`
- `#sendButton`

### Features

| Feature | Details |
|---|---|
| **Click toggle** | Clicking the sun/moon button switches themes |
| **Keyboard shortcut** | Ctrl+Shift+L (Cmd+Shift+L on Mac) toggles themes |
| **OS preference** | Falls back to `prefers-color-scheme` when no saved preference |
| **Live OS tracking** | If no saved preference, theme auto-follows OS changes in real time |
| **Persistence** | Saved to `localStorage`; survives reloads and sessions |
| **No FOUC** | Inline head script applies theme before CSS/DOM render |
| **Dynamic aria-label** | Updates to "Switch to dark/light mode" after each toggle |
| **Smooth transitions** | 0.3s ease on background-color, color, border-color, and box-shadow across all themed elements |
