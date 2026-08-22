# CW Transportadora - Design System Documentation

## Overview
This design system follows the "Enterprise SaaS Modern" aesthetic, inspired by platforms like Salesforce and HubSpot. It provides a clean, professional, and reliable visual language with touches of innovation.

## Color Palette

### Primary Colors - "Professional Blue"
```css
--color-primary: #0F62FE;           /* IBM Blue vibrant */
--color-primary-dark: #0043CE;      /* Darker shade for hover states */
--color-primary-light: #4589FF;     /* Lighter shade for accents */
```

### Neutral Colors - Light Mode
```css
--color-background: #FFFFFF;        /* Main background */
--color-surface: #F4F4F4;           /* Secondary background */
--color-surface-dark: #E0E0E0;      /* Tertiary background */
--color-card: #FFFFFF;              /* Card background */
--color-border: #E0E0E0;            /* Standard borders */
--color-border-light: #F4F4F4;      /* Subtle borders */
```

### Neutral Colors - Dark Mode
```css
--color-background-dark: #161616;   /* Main background */
--color-surface-dark: #262626;      /* Secondary background */
--color-card-dark: #262626;         /* Card background */
--color-border-dark: #393939;       /* Standard borders */
--color-border-light-dark: #353535; /* Subtle borders */
```

### Text Colors - Light Mode
```css
--color-text-primary: #161616;      /* Primary text */
--color-text-secondary: #525252;   /* Secondary text */
--color-text-tertiary: #8D8D8D;     /* Tertiary text */
```

### Text Colors - Dark Mode
```css
--color-text-primary-dark: #FFFFFF; /* Primary text */
--color-text-secondary-dark: #C6C6C6; /* Secondary text */
--color-text-tertiary-dark: #8D8D8D; /* Tertiary text */
```

### Status Colors
```css
--color-success: #198038;           /* Green - Professional */
--color-warning: #F1C21B;           /* Yellow - Amber */
--color-error: #DA1E28;             /* Red */
--color-info: #0F62FE;              /* Blue - Primary */
```

### Accent Colors
```css
--color-accent-1: #8A3FFC;          /* Purple - Highlights */
--color-accent-2: #009D9A;          /* Turquoise - Positive data */
--color-accent-3: #FF7323;          /* Orange - Alerts */
```

## Typography

### Font Families
```css
--font-family-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
--font-family-secondary: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
```

### Font Sizes
```css
--font-size-h1: 32px;               /* Headings level 1 */
--font-size-h2: 24px;               /* Headings level 2 */
--font-size-h3: 18px;               /* Headings level 3 */
--font-size-body: 14px;             /* Body text */
--font-size-small: 12px;            /* Small text */
--font-size-caption: 11px;          /* Caption text */
```

### Font Weights
```css
--font-weight-regular: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;
```

### Letter Spacing
```css
--letter-spacing-tight: -0.5px;      /* H1 */
--letter-spacing-tight: -0.25px;     /* H2 */
--letter-spacing-normal: 0px;        /* Body, H3 */
```

### Line Heights
```css
--line-height-tight: 1.2;           /* Headings */
--line-height-normal: 1.5;          /* Body text */
--line-height-relaxed: 1.75;        /* Long-form content */
```

## Spacing

### Scale (4px base unit)
```css
--spacing-xs: 4px;                  /* 0.25rem */
--spacing-sm: 8px;                  /* 0.5rem */
--spacing-md: 16px;                 /* 1rem */
--spacing-lg: 24px;                 /* 1.5rem */
--spacing-xl: 32px;                 /* 2rem */
--spacing-2xl: 48px;                /* 3rem */
--spacing-3xl: 64px;                /* 4rem */
```

### Component Spacing
```css
--spacing-card-padding: 24px;
--spacing-section-gap: 32px;
--spacing-form-gap: 16px;
--spacing-list-gap: 12px;
```

## Border Radius

```css
--radius-sm: 4px;                   /* Small elements */
--radius-md: 8px;                   /* Cards, buttons */
--radius-lg: 12px;                  /* Large cards, modals */
--radius-xl: 16px;                  /* Hero elements */
--radius-full: 9999px;              /* Pills, avatars */
```

## Shadows

```css
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07);
--shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15);
```

## Transitions

```css
--transition-fast: 150ms ease;
--transition-normal: 250ms ease;
--transition-slow: 350ms ease;
```

## Z-Index Scale

```css
--z-dropdown: 1000;
--z-sticky: 1020;
--z-fixed: 1030;
--z-modal-backdrop: 1040;
--z-modal: 1050;
--z-popover: 1060;
--z-tooltip: 1070;
```

## Breakpoints

```css
--breakpoint-sm: 640px;             /* Small tablets */
--breakpoint-md: 768px;             /* Tablets */
--breakpoint-lg: 1024px;            /* Laptops */
--breakpoint-xl: 1280px;            /* Desktops */
--breakpoint-2xl: 1536px;           /* Large screens */
```

## Component Tokens

### Buttons
```css
--button-height-sm: 32px;
--button-height-md: 40px;
--button-height-lg: 48px;
--button-padding-x: 16px;
```

### Inputs
```css
--input-height: 40px;
--input-padding-x: 12px;
--input-border-width: 1px;
```

### Sidebar
```css
--sidebar-width: 260px;
--sidebar-collapsed-width: 64px;
```

### Header
```css
--header-height: 64px;
```

## Usage Guidelines

### Dark Mode Implementation
To implement dark mode, add the `.dark-mode` class to the body element. All color variables should be defined with CSS custom properties that update based on this class.

### Responsive Design
Use the breakpoint tokens with CSS `@media` queries to create responsive layouts:
```css
@media (min-width: var(--breakpoint-md)) {
  /* Tablet and up styles */
}
```

### Accessibility
- Ensure text contrast ratios meet WCAG AA standards (4.5:1 for normal text, 3:1 for large text)
- Use semantic HTML elements
- Provide focus states for interactive elements
- Include aria-labels for icon-only buttons

## Component States

### Button States
- **Default**: Primary color background, white text
- **Hover**: Primary dark color background
- **Active**: Primary dark color with slight scale transform
- **Disabled**: Opacity 0.5, no pointer events

### Input States
- **Default**: Border color, white background
- **Focus**: Primary color border, subtle glow
- **Error**: Error color border, error message
- **Disabled**: Gray background, no pointer events

### Card States
- **Default**: White background, subtle shadow
- **Hover**: Slightly elevated shadow
- **Active**: Primary color border

## Icon Guidelines

### Navigation Icons
- Size: 20px
- Stroke width: 2px
- Color: Current text color

### Action Icons
- Size: 16px
- Stroke width: 2px
- Color: Inherit from parent

### Status Icons
- Size: 16px
- Stroke width: 2px
- Color: Corresponding status color
