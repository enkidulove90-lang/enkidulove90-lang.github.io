# Interactive Paper Map Implementation Plan

> **Goal:** Build a trustworthy paper map: local coordinates first, graceful unlocated fallback, and environment-specific restricted basemap credentials.

**Architecture:** Notion provides semantic location metadata; Python resolves trusted local WGS-84 entries and cached images; Hexo generates a static payload and injects one environment-specific CARTO key; Leaflet renders CARTO Voyager with an OpenStreetMap fallback.

## Completed tasks

- [x] Preserve the five Notion location fields in Markdown Front-matter.
- [x] Add `tools/location_dict.json` with institution aliases, semantic kinds, cities and WGS-84 coordinates.
- [x] Make public Nominatim lookup opt-in, rate-limited and replaceable through `NOMINATIM_URL`.
- [x] Keep periodic builds cache-only and network-independent for geocoding.
- [x] Generate located papers, unlocated papers, semantic links and honest coverage metadata.
- [x] Render darkened CARTO Voyager with separate local/production Key injection and an OpenStreetMap failure fallback.
- [x] Use transparent semantic icons, a floating vertical legend, and an on-demand slide-in city panel that closes on map clicks.
- [x] Merge institutions sharing the same city and semantic type to avoid overlapping markers.
- [x] Add a singleton hover card, local three-image city galleries, institution profiles, carousel cleanup, and clustering above 100 markers.
- [x] Add automated tests for WGS-84 validation, aliases, unlocated fallback and frontend behavior.
- [ ] Continue expanding the institution dictionary as new verified affiliations enter Notion.
