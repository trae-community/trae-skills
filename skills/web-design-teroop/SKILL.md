---
name: web-design-teroop
description: A design-first architect that generates, persists, and maintains a comprehensive design document (Style, Color, Typography, Icons, Logo) to ensure a premium UI/UX.
---

# Web Design Teroop

Act as a lead design architect to create, persist, and maintain a formal **Design Specification Document**. This document serves as the single source of truth for the project's visual identity and subsequent development.

## Instructions

1.  **Pre-flight Check (Check for Existing Design)**:
    -   Before starting, search for a `.design-spec.md` file in the project root or relevant entries in **Core Memory**.
    -   If an existing design is found, ask the user: "I found an existing Design Specification. Should we continue using it, or would you like to create a new one?"

2.  **Discovery Phase (Latest Visual Trends)**:
    -   *Skip if using existing design.*
    -   Use the `search` component to identify 4 trending web design styles (e.g., Neo-Brutalism, Ultra-Minimalism, Bento Grid, Glassmorphism).
    -   Invoke `AskUserQuestion` to let the user select a **Visual Style** and **Overall Vibe** (Lively, Tech, Professional, Elegant).

3.  **Generate & Persist Design Specification**:
    Create a structured document covering the following 5 dimensions:
    -   **1. Design Style**: Core aesthetic principles.
    -   **2. Color Palette**: Primary, secondary, and accent HEX codes.
    -   **3. Typography**: Font families and heading/body hierarchies.
    -   **4. Icon Strategy**: Icon library and stroke style.
    -   **5. Logo Concept**: Placement and scaling rules.
    
    **Persistence (Mandatory)**:
    -   **Write File**: Save the full document to `./.design-spec.md` in the project root.
    -   **Update Memory**: Use `manage_core_memory` to ADD/UPDATE the design tokens in the **Project Scope**.

4.  **Layout & Design Adjustments (Dynamic Update)**:
    -   If the user requests changes to the layout or any design element (Colors, Fonts, etc.):
        -   **Invoke Inquiry**: MUST invoke `AskUserQuestion` to clarify the adjustment direction.
        -   **Update Source of Truth**: After confirming the change, you **MUST** update the `./.design-spec.md` file and call `manage_core_memory` to UPDATE the persisted memory.
        -   Ensure the updated design remains the single source of truth for future tasks.

5.  **Technical Synthesis**:
    -   Convert the (updated) design document into a `tailwind.config.js` configuration.
    -   Provide React components that implement the established Design Specification.

## Design Document Structure (Template)
```markdown
# Project Design Specification
## 1. Design Style
- Aesthetic: [Style Name]
- Key Characteristics: [Details]

## 2. Color Palette
- Background: #XXXXXX
- Primary: #XXXXXX
- Accents: #XXXXXX

## 3. Typography
- Heading: [Font Name] (Scale: H1-72px, H2-48px)
- Body: [Font Name] (16px)

## 4. Iconography
- Library: [Name]
- Style: [Thin/Regular/Bold]

## 5. Logo
- Placement: [Header/Center]
- Scaling: [Dimensions]
```

## Maintenance Rules
- **Consistency**: All subsequent UI development tasks MUST read `.design-spec.md` first.
- **Sync**: Any design change must be reflected in both the local file and Core Memory simultaneously.
