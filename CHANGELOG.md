# Changelog

All notable changes to the Bosch AI Intelligence Workspace are recorded
here, most recent first. This file is also rendered inside the app on
**System Settings -> System -> What changed**, so anyone using the app
can see what moved between versions without reading source.

## [1.1.0] - 2026-09-02

### Fixed
- Type was failing to render on some networks: the app pulled Manrope
  and Inter from `fonts.googleapis.com` at page-load time, which is
  commonly blocked on corporate/EU networks (loading fonts directly
  from Google's CDN leaks the visitor's IP without consent, which is
  why many organizations block it outright). Fonts are now bundled
  with the app and served locally, so there is no external request
  that can fail or get blocked.
- Radio, toggle, checkbox, select and tab labels no longer rely on
  Streamlit's default (low-contrast) text styling -- they now use an
  explicit dark, full-opacity, semi-bold treatment so an option can
  never render as pale/near-invisible text again.

### Changed
- Deepened the secondary/metadata text color (`SLATE`) from `#8A8A8E`
  to `#63636A` across every page for stronger, more premium contrast
  against the ivory/white surfaces.
- Buttons, download buttons, tabs, toggles, and multiselect chips all
  now have explicit hover, active/pressed, and focus states (previously
  only the primary button had a hover state).

### Added
- Feedback submitted through the floating widget is now emailed to
  `rby4kor@bosch.com` in addition to being written to
  `data/feedback.jsonl` (requires SMTP environment variables to be set
  in the deployment -- see System Settings -> System).
- This changelog, surfaced inside the app, so version-to-version
  changes are visible without reading source or diffing commits.

## [1.0.0] - 2026-08-01

### Added
- Initial release of the Bosch AI Intelligence Workspace: editorial
  enterprise design system, guided Create Intelligence Brief workflow,
  Visual Library, Reports, Analytics, Activity Log, and floating
  feedback widget.
