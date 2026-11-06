# Observatory verification

## Passed

- `npm.cmd run build`: strict TypeScript compilation and Vite production build.
- `npm.cmd test`: 17 tests across data-contract and React interaction suites.
  Checks cover real artifacts, future channels, invalid data, endpoint validation,
  theme persistence, replay/reset/scrubbing, variable selection, phase navigation,
  empty results, explicit API failure/recovery, sidebar collapse/persistence,
  the four navigation sections, and mobile menu dismissal.
- Existing Python architecture, adapter, and seeded reproducibility tests: 11 passed.
- API and dissolved-oxygen metadata regression tests: 5 passed.
- Frontend HTTP response and API health/registry smoke checks returned HTTP 200.
- Real seed-42 export: 1,150 samples, 229.8 elapsed simulated hours, seven channels.
- `git diff --check`: no whitespace errors.

The first full Python run had 15 passes and one fixture setup error because the
sandbox could not access pytest's temporary directory. The five API tests then
passed with a fresh permitted temporary directory. The tests did not uncover a
simulator regression. Starlette emits a dependency deprecation warning for its
httpx TestClient integration; this does not affect the read-only API checks.

Production assets are approximately 107 KB gzip for the main JavaScript, 108 KB
gzip for the separately loaded chart module, 8.6 KB gzip for CSS, and 62 KB for
two local font files. The bundled trajectory JSON is approximately 264 KB before
compression. Configure compression on a production static server.

## Remaining visual verification

Actual browser rendering, responsive screenshots, chart hover appearance, and
visual contrast were not verified. The browser connector was unavailable, and
Windows Computer Use ended because it could not establish the active URL safely.
No screenshot or browser-success claim is made. Component tests use jsdom with
the chart renderer mocked; they are not substitutes for visual browser checks.

When opening the site, inspect both themes at desktop and phone widths, all four
views, the chart tooltip and slider, the mobile menu, and keyboard focus within
the connection dialog. Preview/API servers used for checks were stopped after
verification; follow `apps/dashboard/README.md` to start them.
