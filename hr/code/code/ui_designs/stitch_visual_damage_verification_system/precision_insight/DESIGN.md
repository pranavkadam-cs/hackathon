---
name: Precision Insight
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#44474c'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#74777d'
  outline-variant: '#c4c6cd'
  surface-tint: '#4f6073'
  primary: '#041627'
  on-primary: '#ffffff'
  primary-container: '#1a2b3c'
  on-primary-container: '#8192a7'
  inverse-primary: '#b7c8de'
  secondary: '#006b5f'
  on-secondary: '#ffffff'
  secondary-container: '#62fae3'
  on-secondary-container: '#007165'
  tertiary: '#211200'
  on-tertiary: '#ffffff'
  tertiary-container: '#38260b'
  on-tertiary-container: '#a88c69'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d2e4fb'
  primary-fixed-dim: '#b7c8de'
  on-primary-fixed: '#0b1d2d'
  on-primary-fixed-variant: '#38485a'
  secondary-fixed: '#62fae3'
  secondary-fixed-dim: '#3cddc7'
  on-secondary-fixed: '#00201c'
  on-secondary-fixed-variant: '#005047'
  tertiary-fixed: '#feddb5'
  tertiary-fixed-dim: '#e1c29b'
  on-tertiary-fixed: '#281802'
  on-tertiary-fixed-variant: '#584326'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.03em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  gutter: 20px
  margin: 24px
---

## Brand & Style
The design system is engineered for high-stakes environments where clarity, speed, and objective evidence are paramount. The brand personality is **Professional, Analytical, and Unwavering**. It targets insurance adjusters, logistics managers, and legal professionals who require a tool that feels like a high-precision instrument rather than a social application.

The aesthetic follows a **Modern Corporate** direction with a focus on **Information Density and Functional Minimalism**. It utilizes a structured grid, generous whitespace to reduce cognitive load, and high-contrast typography to ensure that critical evidence is never overlooked. The emotional response should be one of total confidence—users should feel that the system is as rigorous and meticulous as their own professional standards.

## Colors
The palette is anchored by **Deep Navy (#1A2B3C)**, used for structural elements and primary navigation to establish an immediate sense of authority. **Vibrant Teal (#2DD4BF)** acts as the functional accent, highlighting active states, primary actions, and AI-driven insights without appearing distracting.

The background uses a cool **Neutral Gray (#F8FAFC)** to provide a soft contrast against pure white cards, creating a clear "layered" architecture. Semantic colors (Emerald, Amber, Rose) are reserved strictly for status communication—Success, Warning, and Danger—ensuring that risk indicators are immediately scannable.

## Typography
This design system utilizes **Inter** for its exceptional legibility in data-heavy interfaces. The typographic hierarchy is strictly controlled to differentiate between "Evidence Data" (Body) and "System Metadata" (Labels).

- **Headlines:** Semi-bold weight with tight letter-spacing for a modern, authoritative look.
- **Body:** Standardized at 14px for optimal density in review panels.
- **Labels:** Used for status badges, timestamps, and field headers. Small caps or increased letter-spacing should be applied to `label-sm` to maintain readability at small scales.

## Layout & Spacing
The system employs a **Fluid-Fixed Hybrid Grid**. The primary navigation and "Evidence Metadata" sidebar are fixed-width (280px and 320px respectively), while the central "Review Workspace" stretches to accommodate high-resolution imagery and video streams.

A **4px baseline scale** governs all internal component spacing. Elements are grouped using 8px (sm) or 16px (md) gaps. Large sections or distinct "Evidence Blocks" are separated by 32px (xl) to prevent visual clutter. On mobile devices, margins shrink to 16px, and sidebars collapse into a drawer-style navigation to prioritize the evidence viewport.

## Elevation & Depth
Hierarchy is established through **Tonal Layering** and **Subtle Ambient Shadows**. 
1. **Level 0 (Background):** #F8FAFC - The canvas.
2. **Level 1 (Cards/Panels):** Pure White surface with a 1px border (#E2E8F0) and a very soft shadow (0px 1px 3px rgba(0,0,0,0.05)).
3. **Level 2 (Overlays/Popovers):** Pure White surface with a more pronounced shadow (0px 10px 15px -3px rgba(0,0,0,0.1)) to indicate temporary interaction.

This approach avoids heavy drop-shadows, maintaining a clean, "scientific" feel while still providing enough depth to distinguish interactive layers from the static background.

## Shapes
The shape language uses a **Medium Roundedness** (8px base). This softens the industrial nature of the data without appearing overly "consumer-grade" or playful. 

- **Standard Elements (Buttons, Inputs, Cards):** 8px (0.5rem).
- **Large Containers (Modals, Large Evidence Panels):** 16px (1rem).
- **Status Pills:** Fully rounded (pill-shaped) to distinguish them from interactive buttons.

## Components
- **Buttons:** Primary buttons use the Deep Navy background with white text. Secondary "Action" buttons (e.g., "Verify Evidence") use the Vibrant Teal. All buttons feature a subtle transition state (slight darkening) on hover.
- **Evidence Cards:** Feature a top-weighted image/video area, followed by a metadata row. Risk indicators are positioned in the top-right corner of the card as floating badges.
- **Status Badges:** Use a "Light Fill" approach—e.g., a "High Risk" badge has a light rose background with deep red text for high contrast and readability.
- **Input Fields:** Use a 1px neutral border that transitions to Vibrant Teal on focus. Labels are consistently placed above the field in `label-sm`.
- **AI-Insights Panel:** Distinct from standard lists, these use a very light teal tint (#F0FDFA) for the background to signify that the content was generated by the platform's AI, providing a clear distinction from raw evidence.
- **Lists:** Clean rows with 1px dividers. Use alternating row colors (zebra striping) only for data tables exceeding 20 rows.