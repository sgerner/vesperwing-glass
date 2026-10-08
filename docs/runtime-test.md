# Runtime test — 2026-10-07

Tested extension 0.1.0 with Thunderbird 157.0.1 on Kubuntu/KDE Wayland using `/tmp/lumaglass-demo-profile`, fictional local mail, and legacy profile stylesheet loading disabled. The real profile was not modified.

## Verified

- Extension installation and enablement succeed.
- Light and dark main mail views show translucent rail, toolbar, folder pane, inbox cards, and plain-text message reader.
- Print preview shows readable controls and an opaque white printed page. Preview was cancelled; nothing printed.
- Disabling immediately removes the extension styles; enabling immediately restores them.
- Styling survives a Thunderbird restart.
- A newly opened separate compose window receives the dark styles. Fictional text entry and caret work. The test message was discarded without sending or saving.

## Remaining acceptance gaps

- Settings and Add-ons retain a mostly opaque canvas despite some applied styling.
- Compose body transparency is very restrained and needs further visual refinement.
- Dark New Message button truncates in a narrow folder pane.
- Light compose, authored HTML email edge cases, accessibility modes, and uninstall cleanup have not been verified in this run.

The Experiment mechanism works without userChrome/userContent enabled, but this candidate is not yet ready for a claim of complete surface coverage or marketplace submission.

## Refinement 0.2.0

Computer-use checks in the same fictional profile, still with legacy profile CSS disabled:

- Light/dark rail, top/status bars and inbox cards remain translucent, with square control/card edges.
- Unselected tabs and idle toolbar buttons blend into the backdrop; light top-bar labels use bright ink and restrained shadow for contrast.
- Settings and Add-ons now expose the wallpaper through their canvases. Appearance layout-selection boxes are square (their illustrative images retain native artwork).
- Separate light compose editor shows visible glass at 76% frame opacity. Fictional subject/body entry and caret were checked, then discarded without saving or sending.
- Reader frame uses explicit 78% opacity instead of relying on a broad browser fade. Plain-text mail remains readable in both schemes.
- Print preview has square controls and opaque white paper; cancelled without printing.
- Extension update/restart preserves the appearance. The final accessibility opacity guards were inspected in source; OS accessibility preferences were not exercised.

Remaining: complex authored/received HTML and quoted content, uninstall cleanup, actual forced-colors/reduced-transparency settings. Native OS dialogs keep the desktop appearance. Whole-frame blending also fades glyphs/images locally; it does not alter sent message HTML. No claim of exhaustive edge-case coverage or Add-ons approval is made.

- Final 0.2.0 disable/re-enable was exercised: native opaque canvases return when disabled, utility glass returns on enable. This revealed a generic button rule clearing the native toggle backing; the final rule excludes `.toggle-button` and switch controls.
