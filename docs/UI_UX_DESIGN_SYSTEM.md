# AIA UI/UX Design System (Windows 11 Fluent + Futuristic Minimal)

## 1) Product surface and behavior
- **Platform**: Windows-only floating desktop widget (PySide6), frameless translucent window.
- **Two forms**:
  - **Pill / Orb mode**: compact `260x88`, voice waveform + mode status.
  - **Panel mode**: expanded `420x640`, full chat/log/control workspace.
- **Window behavior**:
  - Rounded corners `14px`.
  - Acrylic-like dark glass surface (`rgba(30,30,30,0.76)`).
  - Deep colored shadow glow mapped to current operation mode.

## 2) Color system and mode accents
### Base palette
- `BG/Base`: `#121212`
- `Surface/Glass`: `rgba(30,30,30,0.76)`
- `Text/Primary`: `#F5F5F5`
- `Text/Secondary`: `#A1A1AA`
- `Border`: `rgba(255,255,255,0.08)`

### Mode accents (global semantic state)
- **PASSIVE**: `#10B981` (emerald calm)
- **ASSISTED**: `#F59E0B` (amber caution)
- **ACTIVE**: `#EF4444` (crimson high-alert)

Accent affects:
1. Send button fill.
2. Voice visualizer glow.
3. Breathing window shadow.
4. Tray icon color.
5. Critical state emphasis.

## 3) Typography and spacing
- Font stack: `Segoe UI Variable`, fallback `Inter`, then `Segoe UI`.
- Default text size: `13px`.
- Hierarchy:
  - Status/meta: `12-13px`, secondary color.
  - Body/chat: `13px`.
  - High-priority action labels: `13-14px`, weight `600-700`.
- Spacing system: `4, 8, 12, 16` px rhythm.

## 4) Core component specs
## Top bar (draggable)
- Height: ~34px.
- Contains online/offline dot + connection text + mode selector + morph button.
- Dot must communicate liveness instantly (green=online, red=offline).

## Chat surface
- Scrollable history area with subtle glass panel.
- User messages: right-semantic identity (icon + label in MVP).
- Agent messages: left-semantic identity.
- Loading hint: log row `⏳ Agent thinking...` while waiting planner response.

## Voice input area
- Animated waveform renderer at bottom.
- Uses accent color and rhythmic random amplitude in MVP as microphone-reactive visual proxy.
- Designed for replacement with actual mic amplitude stream.

## Mode switcher
- Compact Fluent-like combo/segment with rounded corners.
- Changes full application accent with animated transition (300ms).

## Kill switch button
- Prominent emergency control with radial red treatment and bold label.
- Always visible in panel mode.

## 5) Motion language and animation timings
- **Mode transition color fade**: 300ms, `InOutCubic`.
- **Pill⇄Panel morph**: 420ms, `OutBack` spring-like effect.
- **Confirmation modal entry**: 260ms top-slide, `OutCubic`.
- **Breathing glow**: timer-driven pulse loop (~90ms ticks) around shadow alpha.
- **Panic flash**: 280ms red overlay fade-out.

## 6) Security confirmation UX
- Modal is always-on-top and modal-blocking.
- Visual hierarchy:
  1. Warning icon (`⚠`) and critical title.
  2. Structured action payload preview.
  3. Primary CTA `ALLOW EXECUTION` + secondary `DENY`.
  4. Timeout progress strip (auto-deny on expiry).

## 7) Accessibility and UX safeguards
- Critical actions require explicit user approval in assisted/active-critical paths.
- Auto-deny on timeout for confirmation modal.
- Kill switch immediately forces passive-safe state and visual panic acknowledgement.
- High contrast maintained between text and deep dark background.

## 8) Implementation mapping in code
- Design tokens/theme generation: `aia/gui/design_system.py`
- Surface composition + waveform: `aia/gui/chat_widget.py`
- Framed window behavior + animations + panic flow: `aia/gui/main_gui.py`
- Critical confirmation presentation: `aia/gui/confirmation_dialog.py`

## 9) Future evolution (next design iteration)
- Replace waveform proxy with real microphone RMS envelope.
- Add markdown renderer with code block cards and copy actions.
- Add message bubble delegates for full left/right alignment and timestamp chips.
- Add edge-magnetic snapping for pill mode.
