---
name: Technical Trust System
colors:
  surface: '#f7f9fb'
  surface-dim: '#d8dadc'
  surface-bright: '#f7f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#eceef0'
  surface-container-high: '#e6e8ea'
  surface-container-highest: '#e0e3e5'
  on-surface: '#191c1e'
  on-surface-variant: '#45464d'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#76777d'
  outline-variant: '#c6c6cd'
  surface-tint: '#565e74'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#131b2e'
  on-primary-container: '#7c839b'
  inverse-primary: '#bec6e0'
  secondary: '#515f74'
  on-secondary: '#ffffff'
  secondary-container: '#d5e3fd'
  on-secondary-container: '#57657b'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#001e2f'
  on-tertiary-container: '#008cc7'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dae2fd'
  primary-fixed-dim: '#bec6e0'
  on-primary-fixed: '#131b2e'
  on-primary-fixed-variant: '#3f465c'
  secondary-fixed: '#d5e3fd'
  secondary-fixed-dim: '#b9c7e0'
  on-secondary-fixed: '#0d1c2f'
  on-secondary-fixed-variant: '#3a485c'
  tertiary-fixed: '#c9e6ff'
  tertiary-fixed-dim: '#89ceff'
  on-tertiary-fixed: '#001e2f'
  on-tertiary-fixed-variant: '#004c6e'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
typography:
  display:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-lg:
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
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.05em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  container-max: 1440px
  gutter: 20px
---

## Brand & Style

The design system is engineered for high-stakes insurance environments where precision, transparency, and speed are paramount. The brand personality is authoritative yet assistive—acting as a high-fidelity lens for claims adjusters. 

The aesthetic follows a **Corporate / Modern** direction with a **Technical** overlay. It prioritizes information density without clutter, using a structured hierarchy to guide the user through complex datasets. Visual elements are intentional and functional, evoking the feeling of a sophisticated diagnostic tool rather than a standard back-office application. The emotional response should be one of absolute confidence in the AI’s findings and the reliability of the data presented.

## Colors

The palette is anchored in deep "Ink" and "Slate" tones to establish a foundation of professional stability. 

- **Primary (#0F172A):** Used for core navigation, primary headers, and deep-contrast text to ensure maximum legibility.
- **Secondary (#334155):** Utilized for supporting UI elements, icons, and secondary actions.
- **Tertiary (#0EA5E9):** A high-visibility blue used exclusively for interactive elements, text links, and active states.
- **Neutral (#F8FAFC):** The primary background color to reduce eye strain during long processing sessions.

**Functional Status Colors:**
These are strictly reserved for AI verification outcomes:
- **Green (Success):** Claims or evidence that are fully supported by AI cross-referencing.
- **Amber (Warning):** Items requiring manual human review or showing minor inconsistencies.
- **Red (Error):** Direct contradictions or high-probability fraud flags.

## Typography

This design system utilizes **Inter** for all primary interface elements to ensure maximum readability and a neutral, professional tone. To reinforce the technical nature of AI verification, **JetBrains Mono** is introduced for data labels, status badges, and metadata. This monospaced font helps distinguish system-generated data from user-entered content.

- **Headlines:** Keep weights at 600 or 700 to provide clear section anchors.
- **Body:** Standardized at 14px for density, allowing more information to be visible above the fold.
- **Labels:** Use uppercase and monospaced styling for status badges and claim IDs to create a "serial number" feel.

## Layout & Spacing

The layout utilizes a **Fixed Grid** system for desktop, centered on a 1440px canvas to maintain control over data table density. 

- **Desktop (12 Columns):** 24px margins, 20px gutters. Content is often organized into a 3/4 layout (left navigation/summary, right primary data worklist).
- **Tablet (8 Columns):** Sidebars collapse into icons or top navigation to prioritize data visibility.
- **Mobile (4 Columns):** Tables reflow into vertically stacked cards.

Spacing follows a strict 4px baseline rhythm. For high-density data views, use `sm` (8px) for internal component padding and `md` (16px) for block spacing.

## Elevation & Depth

To maintain a "technical workstation" feel, this design system avoids heavy shadows. Instead, it utilizes **Tonal Layers** and **Low-Contrast Outlines**.

- **Level 0 (Background):** Neutral (#F8FAFC).
- **Level 1 (Cards/Containers):** Pure White (#FFFFFF) with a 1px solid border in Slate-200. No shadow.
- **Level 2 (Modals/Popovers):** Pure White with a 1px border and a subtle, high-diffusion ambient shadow (4px blur, 5% opacity black) to suggest a slight lift.
- **Focus States:** 2px outer glow using the Tertiary blue color to clearly indicate keyboard navigation.

## Shapes

The shape language is "Soft" (4px radius) to maintain a precise, engineered look. 

- **Buttons & Inputs:** 4px (Soft) corner radius.
- **Badges & Status Tags:** 2px radius for a more clinical, "stamped" appearance.
- **Large Container/Cards:** 8px (Rounded-lg) to subtly differentiate the main workspace from the individual elements within it.

## Components

### Data Tables
Tables are the core of the system. They must use `body-md` typography. Rows should have a hover state (#F1F5F9) and utilize subtle 1px dividers. Column headers use `label-sm` monospaced text for a technical feel.

### Image Inspection Cards
Used for claim evidence. These cards feature a large image thumbnail with a "Verification Overlay." If the AI detects a contradiction, a semi-transparent red header (#EF4444 at 90%) is applied to the card with the specific risk flag.

### Risk Flag Badges
Small, high-contrast indicators. They use the status colors (Green, Amber, Red). The text inside must be monospaced `label-sm`. 
- *Supported:* Green background, white text.
- *Inconsistent:* Amber background, Primary color text.
- *Contradiction:* Red background, white text.

### Buttons
- **Primary:** Primary color background, white text. 
- **Secondary:** White background, 1px Slate-200 border, Primary text.
- **Ghost:** No border or background, Tertiary blue text. Used for "Cancel" or "View Details" within tables.

### Input Fields
Fields should have a 1px border. On focus, the border changes to Tertiary blue. AI-suggested values in fields should be highlighted with a very faint blue background (#F0F9FF) and a "System Generated" tooltip.