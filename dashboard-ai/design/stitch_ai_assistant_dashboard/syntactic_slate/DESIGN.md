---
name: Syntactic Slate
colors:
  surface: '#0f131c'
  surface-dim: '#0f131c'
  surface-bright: '#353942'
  surface-container-lowest: '#0a0e16'
  surface-container-low: '#181c24'
  surface-container: '#1c2028'
  surface-container-high: '#262a33'
  surface-container-highest: '#31353e'
  on-surface: '#dfe2ee'
  on-surface-variant: '#c2c6d6'
  inverse-surface: '#dfe2ee'
  inverse-on-surface: '#2c3039'
  outline: '#8c909f'
  outline-variant: '#424754'
  surface-tint: '#adc6ff'
  primary: '#adc6ff'
  on-primary: '#002e6a'
  primary-container: '#4d8eff'
  on-primary-container: '#00285d'
  inverse-primary: '#005ac2'
  secondary: '#4edea3'
  on-secondary: '#003824'
  secondary-container: '#00a572'
  on-secondary-container: '#00311f'
  tertiary: '#ffb95f'
  on-tertiary: '#472a00'
  tertiary-container: '#ca8100'
  on-tertiary-container: '#3e2400'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#d8e2ff'
  primary-fixed-dim: '#adc6ff'
  on-primary-fixed: '#001a42'
  on-primary-fixed-variant: '#004395'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#0f131c'
  on-background: '#dfe2ee'
  surface-variant: '#31353e'
typography:
  display:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.005em
  body-lg:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: -0.005em
  body-md:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0em
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0em
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: -0.01em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '400'
    lineHeight: 14px
    letterSpacing: 0.02em
  code-block:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-compact: 0.5rem
  margin: 1.5rem
  margin-mobile: 0.75rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1rem
  space-xl: 1.5rem
  space-2xl: 2rem
---

## Brand & Style

This design system embodies high-density utility, technical precision, and quiet authority. Designed for an enterprise AI workspace, it eschews speculative "AI magic" tropes—decorative glowing orbs, rainbow gradients, and amorphous backdrop blurs—in favor of predictable, responsive, and tactile software tools inspired by developer-first platforms like Linear, Raycast, and Vercel.

The visual tone is uncompromisingly utilitarian and disciplined:
- **Tone:** Professional, precise, unhurried, and calm under load.
- **Visual Stance:** Dense, crisp, high-contrast dark-mode interface with sharp delineations between surface tiers, clear typographical scale, and explicit state signaling.
- **Interaction Ethos:** Sub-100ms micro-transitions, absolute visibility of system status (heuristics-driven), strict focus rings, and zero decorative fluff. Every pixel serves prompt engineering, workspace orchestration, model inspection, or vector index telemetry.

## Colors

The palette is engineered around an ultra-deep slate baseline that minimizes eye fatigue while sustaining strict WCAG AAA contrast ratios for body and code typography. Color is deployed strictly as functional syntax, never as background ornamentation.

### Surface System
- **Canvas Base (`#0B0F17`):** The primary root canvas; deep slate-black providing depth without pure hex black deadness.
- **Surface Elevation 1 (`#131B26`):** Sidebar panels, elevated cards, command bars, and drawer canvases.
- **Surface Elevation 2 (`#1A2433`):** Active item highlights, dropdown sheets, floating toolbars, and nested code blocks.
- **Surface Elevation 3 (`#223044`):** Hover states, contextual popovers, modal overlays.
- **Border Subtle (`#1E293B`):** Structural division lines for static splitters and sidebars.
- **Border Default (`#26354A`):** Interactive element boundaries (inputs, cards, table rows).
- **Border Focus (`#3B82F6`):** Solid focus rings and active multi-selection frames.

### Typographic Hierarchy Colors
- **Text Primary (`#F8FAFC`):** Model responses, primary commands, input text, table headers.
- **Text Secondary (`#94A3B8`):** System labels, secondary metadata, token costs, inactive nav icons.
- **Text Muted (`#64748B`):** Timestamps, placeholder text, hotkey bindings, structural hints.

### Semantic Syntax
- **Action Primary (`#3B82F6`):** Send triggers, primary commit actions, execution states.
- **Semantic Success (`#10B981`):** Indexing finalized, pipeline healthy, model weights hot-loaded.
- **Semantic Warning (`#F59E0B`):** Token limits nearing threshold, vector embedding chunking in-progress, cold-starts.
- **Semantic Danger (`#EF4444`):** Destructive actions, rate limit failures, inference engine execution errors.

## Typography

The typographic engine uses **Inter** for conversational prose, structural navigation, and form labels, paired with **JetBrains Mono** for developer ergonomics: execution metadata, latency counters, token math, JSON payloads, and embedded code blocks.

- **Prose Contrast & Rhythm:** Body text is calibrated to 13px (`body-md`) and 15px (`body-lg`) to balance screen density with extended reading comfort during lengthy context window inspections.
- **Tabular Numerics:** All monospace instances use tabular numbers (`tnum`) by default, ensuring metric counters and token meters do not jump horizontally during inference streaming.
- **Punctuation Balance:** Inter uses optical kerning and standard open-type stylistic sets to ensure clean rendering across dark slate backgrounds without letter bloat or fuzzy rendering.

## Layout & Spacing

The layout is built upon an 8-point baseline grid with a 4px sub-grid for dense UI alignment (toolbars, status bars, and terminal widgets).

### Layout Model
- **Core Canvas Strategy:** Fluid composite layout consisting of a fixed 240px or 64px collapsible navigation rail, an elastic main conversational/editor canvas, and an optional 360px collapsible context inspector.
- **Splitpanes:** Dividers utilize 1px gutters enclosed by 4px hit targets with `#1E293B` outlines.
- **Responsive Adaptations:**
  - **Desktop (>= 1280px):** 3-column architecture (Global Navigation, Main Chat/Execution Buffer, Telemetry/Variables Drawer).
  - **Tablet (768px - 1279px):** 2-column architecture (collapsible sidebar, shared main view with slide-over drawer).
  - **Mobile (< 768px):** Single-column stacked mode; sidebar converts to a swipe drawer, context drawer shifts to a bottom-sheet modal. Gutters compress to 8px (`gutter-compact`).

## Elevation & Depth

This design system avoids blurred multi-stop drop-shadows and frosted glass distortion. Visual layering is managed through **tonal stacking** complemented by razor-sharp border outlines:

- **Baseline Canvas:** Flat `#0B0F17`.
- **Level 1 (Cards, Chat Bubbles, Panes):** `#131B26` enclosed by a 1px border of `#1E293B`.
- **Level 2 (Active States, Context Menus, Tooltips):** `#1A2433` with a 1px border of `#26354A` and a directional 4px micro-shadow: `0 4px 12px rgba(0, 0, 0, 0.45)`.
- **Level 3 (Modals, Command K Palettes):** `#131B26` framed by a 1px border of `#26354A` and a deep, directional backdrop shadow: `0 12px 32px rgba(0, 0, 0, 0.70)`. Overlays use a solid tint of `rgba(11, 15, 23, 0.8)` with no blur filter to prevent GPU lag on high-frequency stream events.
- **Focus Indications:** Keyboard navigation takes absolute precedence. Interactive items invoke a 2px offset-free outline using `#3B82F6`.

## Shapes

To ensure an enterprise software posture, shapes conform to a compact, non-pill radius (`roundedness: 1`):

- **Default UI Nodes (Buttons, Inputs, Badges, Tabs):** 6px border radius (`0.25rem` to `0.375rem`).
- **Containers (Panels, Modal Windows, Large Cards):** 8px border radius (`0.5rem`).
- **Code & Syntax Blocks:** 6px radius, matching nested controls.
- **Circular Indicators:** 9999px strictly reserved for operational presence indicators (live SSE stream dot, server latency indicator, user profile avatar). Pills are banned for standard buttons and tags.

## Components

### Buttons
- **Primary:** Background `#3B82F6`, text `#F8FAFC`, subtle inner top border highlighting `rgba(255, 255, 255, 0.15)`. Hover: `#2563EB`. Active: `#1D4ED8`. Focus: 2px ring `#3B82F6` with 2px offset `#0B0F17`.
- **Secondary / Ghost:** Background transparent, border 1px `#26354A`, text `#94A3B8`. Hover: Background `#1A2433`, text `#F8FAFC`.
- **Destructive:** Background `transparent`, border 1px `rgba(239, 68, 68, 0.4)`, text `#EF4444`. Hover: Background `#EF4444`, text `#FFFFFF`.
- **Size Scale:** Compact (28px height, 11px JetBrains Mono for actions), Regular (36px height, 13px Inter).

### Input Fields & Prompt Console
- **Base Style:** Background `#131B26`, border 1px `#26354A`, text `#F8FAFC`, placeholder `#64748B`.
- **Focused:** Border 1px `#3B82F6`, inset subtle shadow `0 0 0 1px #3B82F6`.
- **Multimodal AI Prompt Bar:** Integrated container containing auto-expanding textarea, secondary toolbar footer (model selector dropdown, temperature slider toggle, token count badge, file attachment chip, and execution trigger button).

### Chips & Badges
- **Status Badges:** JetBrains Mono 11px uppercase. Built using a 1px border and 10% tinted background:
  - *Ready / Idle:* Green (`#10B981` border/text, `rgba(16, 185, 129, 0.1)` background).
  - *Processing / Chunking:* Amber (`#F59E0B` border/text, `rgba(245, 158, 11, 0.1)` background).
  - *Failed:* Red (`#EF4444` border/text, `rgba(239, 68, 68, 0.1)` background).
- **Metadata Tag:** Background `#1A2433`, border 1px `#26354A`, text `#94A3B8`, 4px radius.

### Lists & Data Grids
- **Dense Data Rows:** Height 36px, border-bottom 1px `#1E293B`, text `#F8FAFC`.
- **Row Hover:** Surface `#1A2433` transition within 75ms.
- **Selected Row:** Surface `#1A2433`, 2px left border strip in `#3B82F6`.

### Checkboxes & Switches
- **Checkbox:** 14px x 14px, 3px border radius. Unchecked: border 1px `#26354A`, background `#0B0F17`. Checked: background `#3B82F6`, border `#3B82F6` with crisp white checkmark SVG.
- **Switch:** 32px width x 18px height, thumb diameter 14px. Unchecked track `#1E293B`. Checked track `#3B82F6`.

### Code Blocks & Telemetry Inspector
- **Code Block:** Background `#0B0F17`, border 1px `#1E293B`, header strip with mono language tag (`label-sm`), execution duration, and one-click copy button.
- **Telemetry Metric Pill:** Fixed-width tabular numeric widget displaying prompt tokens, response tokens, and elapsed latency (e.g., `42ms / 312 tok`).