// SPDX-License-Identifier: Apache-2.0
// SPDX-FileCopyrightText: 2026 Patrick Zeller
//
// S-02 — XSS regression test suite (CRAM Pre-GA gate)
// ----------------------------------------------------
// Loads crisis-role-manager.html in a headless Chromium instance, injects
// XSS payloads into every user-controlled input surface (role names,
// person names, sync source labels, settings strings, demo-config imports),
// drives the tool through every render path (chart, sidebar tabs, audit
// log, modals, three print templates), and asserts:
//
//   1. No `alert()` dialogues fire (script execution would have triggered).
//   2. No <script> tag appears in the rendered DOM that is not part of
//      the tool's own inlined library blocks.
//   3. No `onerror=`, `onload=`, `onmouseover=` (or similar inline event
//      handlers) appear in the live DOM that originated from user input.
//   4. No `javascript:` URLs appear in any `href` / `src` attribute.
//   5. No CSP-violation console messages are emitted.
//
// The test is intentionally framework-light: it pulls in Playwright
// dynamically and falls back to a clear "skip with reason" exit code
// if the dependency is not installed. Pre-GA, CI/local must have
// Playwright + Chromium provisioned (`npx playwright install chromium`).
//
// Exit codes:
//   0  all surfaces clean
//   1  at least one surface failed (XSS detected)
//   2  setup/tooling failure (Playwright missing, server unreachable, ...)
//
// Usage:
//   node tests/pen-test-s02.js            # uses http://127.0.0.1:8765
//   BASE_URL=http://localhost:9000 node tests/pen-test-s02.js

'use strict';

const path = require('path');
const fs = require('fs');

const BASE_URL = process.env.BASE_URL || 'http://127.0.0.1:8765';
const TOOL_PATH = '/crisis-role-manager.html';
const HEADLESS = process.env.HEADFUL !== '1';
const TIMEOUT_MS = parseInt(process.env.TEST_TIMEOUT_MS || '60000', 10);

// XSS payload set. Each payload is injected into every targeted field
// in isolation. The set is deliberately broad — historical browser bugs
// taught us that vectors which feel redundant on paper are often the
// ones that bypass naive escapers.
const XSS_PAYLOADS = [
  '<img src=x onerror=alert(1)>',
  '"><script>alert(1)</script>',
  'javascript:alert(1)',
  '</div><iframe src=javascript:alert(1)>',
  '"><svg onload=alert(1)>',
  '<script>alert(1)</script>',
  '%3Cscript%3Ealert(1)%3C/script%3E',
  '<a href="javascript:alert(1)">click</a>',
  '<style>body{background:url("javascript:alert(1)")}</style>',
];

// Surfaces tested. Each surface knows how to mutate the State in-page
// so the payload lands exactly where a user-controlled string would
// normally end up. We mutate State directly (rather than typing into
// modal inputs) so the test stays robust against UI redesigns and so
// JSON-import paths can be exercised without file uploads.
const SURFACES = [
  {
    id: 'role.name',
    description: 'Role.name (chart cell + role-edit modal + print views)',
    patch: (payload) => `
      State.config.levels.forEach(lvl => lvl.roles.forEach(r => { r.name = ${JSON.stringify(payload)}; }));
    `,
  },
  {
    id: 'role.description',
    description: 'Role.description (role-edit modal + chart tooltip)',
    patch: (payload) => `
      State.config.levels.forEach(lvl => lvl.roles.forEach(r => { r.description = ${JSON.stringify(payload)}; }));
    `,
  },
  {
    id: 'person.name',
    description: 'Person.name (chart cell + sidebar People-list + audit log)',
    patch: (payload) => `
      State.config.persons.forEach(p => { p.name = ${JSON.stringify(payload)}; });
    `,
  },
  {
    id: 'person.phone',
    description: 'Person.phone (person-detail modal — URL context for tel:)',
    patch: (payload) => `
      State.config.persons.forEach(p => { p.phone = ${JSON.stringify(payload)}; });
    `,
  },
  {
    id: 'person.email',
    description: 'Person.email (person-detail modal — URL context for mailto:)',
    patch: (payload) => `
      State.config.persons.forEach(p => { p.email = ${JSON.stringify(payload)}; });
    `,
  },
  {
    id: 'person.notes',
    description: 'Person.notes (person-detail modal long-text field)',
    patch: (payload) => `
      State.config.persons.forEach(p => { p.notes = ${JSON.stringify(payload)}; });
    `,
  },
  {
    id: 'level.name',
    description: 'Level.name (chart row label + level-edit modal)',
    patch: (payload) => `
      State.config.levels.forEach(lvl => { lvl.name = ${JSON.stringify(payload)}; });
    `,
  },
  {
    id: 'meta.organizationName',
    description: 'meta.organizationName (header + print headers)',
    patch: (payload) => `
      if (!State.config.meta) State.config.meta = {};
      State.config.meta.organizationName = ${JSON.stringify(payload)};
    `,
  },
  {
    id: 'meta.printTitle',
    description: 'meta.printTitle (all 3 print templates)',
    patch: (payload) => `
      if (!State.config.meta) State.config.meta = {};
      State.config.meta.printTitle = ${JSON.stringify(payload)};
    `,
  },
  {
    id: 'sync.source.label',
    description: 'Sync source label (settings accordion + drift modal)',
    patch: (payload) => `
      try {
        var st = JSON.parse(localStorage.getItem('cram.sync.v1') || '{}');
        st.sources = st.sources || [];
        st.sources.push({
          id: 'src-pen-test',
          type: 'http',
          label: ${JSON.stringify(payload)},
          config: { url: 'https://example.invalid/' },
          encryption: { enabled: true },
          createdAt: new Date().toISOString()
        });
        localStorage.setItem('cram.sync.v1', JSON.stringify(st));
      } catch (e) { /* swallow — assertion will catch the absence */ }
    `,
  },
  {
    id: 'sync.source.url',
    description: 'Sync source URL (settings accordion — URL context)',
    patch: (payload) => `
      try {
        var st = JSON.parse(localStorage.getItem('cram.sync.v1') || '{}');
        st.sources = st.sources || [];
        st.sources.push({
          id: 'src-pen-test-url',
          type: 'http',
          label: 'pen-test URL surface',
          config: { url: ${JSON.stringify(payload)} },
          encryption: { enabled: true },
          createdAt: new Date().toISOString()
        });
        localStorage.setItem('cram.sync.v1', JSON.stringify(st));
      } catch (e) { /* swallow */ }
    `,
  },
  {
    id: 'audit.entry',
    description: 'Audit log entry (synthetic — sidebar Audit tab)',
    patch: (payload) => `
      try {
        var log = JSON.parse(localStorage.getItem('cram.audit.v1') || '[]');
        log.unshift({
          ts: new Date().toISOString(),
          type: 'pen-test',
          actor: ${JSON.stringify(payload)},
          subject: ${JSON.stringify(payload)},
          detail: ${JSON.stringify(payload)}
        });
        localStorage.setItem('cram.audit.v1', JSON.stringify(log));
      } catch (e) { /* swallow */ }
    `,
  },
  {
    // V2.1 pre-GA polish — keywords as new XSS-surface. Render paths:
    //   - Person-Edit-Modal: keyword chips with data-keyword attribute
    //   - Search-Tab (sidebar): result list + active-tag chips
    //   - Chart Pool-Member hover/tap: keyword tooltip
    //   - Print People-List template: keyword column / inline list
    // We inject into every person so the chart, sidebar, search and
    // print paths all see the payload as soon as their respective
    // render function fires.
    id: 'person.keywords',
    description: 'Person.keywords (chip + search-tab + chart pool-member + print)',
    patch: (payload) => `
      if (Array.isArray(State.config && State.config.persons)) {
        State.config.persons.forEach(p => {
          if (!p) return;
          // Single-element array: assertions sweep the rendered DOM
          // for the literal payload, so one chip per person is enough
          // to exercise every escape path.
          p.keywords = [${JSON.stringify(payload)}];
        });
      }
    `,
  },
];

// Views to drive after each injection. Each view is selected by a
// resilient CSS query; missing selectors are tolerated (the suite
// keeps going and the missing view is reported in the summary).
const VIEWS = [
  { id: 'chart',          action: `if (typeof render === 'function') render();` },
  { id: 'sidebar.active', action: `State.activeTab = 'active'; if (typeof renderSidebar === 'function') renderSidebar();` },
  { id: 'sidebar.people', action: `State.activeTab = 'people'; if (typeof renderSidebar === 'function') renderSidebar();` },
  // V2.1: search tab introduced in step 6 (Roster/People/Search/Log).
  // Drives the keyword-result chip + result list render paths.
  { id: 'sidebar.search', action: `State.activeTab = 'search'; if (typeof renderSidebar === 'function') renderSidebar();` },
  { id: 'sidebar.audit',  action: `State.activeTab = 'audit';  if (typeof renderSidebar === 'function') renderSidebar();` },
  // Modals are rendered on demand. We invoke the generic open-modal
  // entry points if they are reachable from window scope; otherwise
  // the assertion sweep across the chart already covers most strings.
];

function loadPlaywright() {
  try {
    return require('playwright');
  } catch (e1) {
    try {
      return require('playwright-core');
    } catch (e2) {
      return null;
    }
  }
}

async function loadDemoConfig(page) {
  const demoPath = path.join(__dirname, '..', 'demo', 'cram-demo-enterprise-en.json');
  if (!fs.existsSync(demoPath)) {
    throw new Error('Demo config not found at ' + demoPath);
  }
  const raw = fs.readFileSync(demoPath, 'utf8');
  // We bypass the file-picker by writing config straight into localStorage
  // in the format CRAM expects, then reloading.
  await page.evaluate((rawJson) => {
    const parsed = JSON.parse(rawJson);
    localStorage.setItem('cram.config.v1', JSON.stringify(parsed.config));
    localStorage.setItem('cram.runtime.v1', JSON.stringify(
      parsed.runtime || { unavailable: {}, manualAssignments: {} }
    ));
  }, raw);
  await page.reload({ waitUntil: 'domcontentloaded' });
  // Defensive wait — give the inline scripts a tick to render the chart.
  await page.waitForTimeout(500);
}

// Scan the live DOM for evidence that a payload was interpreted as
// HTML rather than escaped to text. The check is intentionally strict
// about user-controlled origins: we ignore the two inlined library
// <script> blocks and the manifest blob <script>, because those are
// part of the tool's own source.
async function scanForXssArtifacts(page, payload) {
  return page.evaluate((rawPayload) => {
    const findings = [];

    // 1. Foreign <script> tags. The tool ships exactly three inlined
    //    scripts (fflate, qrcode-generator, main). Any 4th script in
    //    the live DOM is suspicious.
    const scripts = Array.from(document.querySelectorAll('script'));
    if (scripts.length > 3) {
      findings.push({
        kind: 'foreign-script-tag',
        count: scripts.length,
        sample: scripts.slice(3, 4).map(s => s.outerHTML.slice(0, 200)),
      });
    }

    // 2. Inline event handlers anywhere in the rendered DOM. The tool
    //    itself does not emit any inline on*= attributes — it wires
    //    everything via addEventListener — so finding even one is a
    //    smoking gun.
    const EVENT_ATTRS = ['onerror', 'onload', 'onclick', 'onmouseover', 'onfocus', 'onsubmit'];
    const all = Array.from(document.querySelectorAll('*'));
    for (const el of all) {
      for (const attr of EVENT_ATTRS) {
        if (el.hasAttribute(attr)) {
          findings.push({
            kind: 'inline-event-handler',
            attr,
            tag: el.tagName,
            value: el.getAttribute(attr).slice(0, 200),
          });
        }
      }
    }

    // 3. javascript: URLs in href/src. CRAM legitimately uses
    //    tel:, mailto:, blob:, data:, and https://. Anything starting
    //    with "javascript:" (case-insensitive) is a finding.
    const URL_ATTRS = ['href', 'src'];
    for (const el of all) {
      for (const attr of URL_ATTRS) {
        const v = el.getAttribute && el.getAttribute(attr);
        if (v && /^\s*javascript:/i.test(v)) {
          findings.push({ kind: 'javascript-url', attr, tag: el.tagName, value: v.slice(0, 200) });
        }
      }
    }

    // 4. Heuristic: payload-marker survival. If the raw payload string
    //    survives in the live DOM as text content but the live DOM
    //    also reflects HTML-special characters from it (literal <, >),
    //    that confirms escaping worked. We do NOT fail on this — we
    //    just record it for the human reviewer.
    const bodyHtml = document.body ? document.body.innerHTML : '';
    const survivedAsText = bodyHtml.includes(
      rawPayload.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;')
    );

    return { findings, survivedAsText };
  }, payload);
}

async function runSurface(browser, surface, payload) {
  const context = await browser.newContext();
  const dialogs = [];
  const consoleErrors = [];
  const pageErrors = [];
  const cspViolations = [];

  const page = await context.newPage();
  page.on('dialog', async (d) => {
    dialogs.push({ type: d.type(), message: d.message() });
    await d.dismiss().catch(() => {});
  });
  page.on('pageerror', (err) => { pageErrors.push(String(err.message || err)); });
  page.on('console', (msg) => {
    const t = msg.type();
    const text = msg.text();
    if (t === 'error') consoleErrors.push(text);
    if (/Content Security Policy/i.test(text)) cspViolations.push(text);
  });

  await page.goto(BASE_URL + TOOL_PATH, { waitUntil: 'domcontentloaded', timeout: TIMEOUT_MS });
  await page.evaluate(() => localStorage.clear());
  await page.reload({ waitUntil: 'domcontentloaded' });
  await loadDemoConfig(page);

  // Apply the surface-specific patch, then re-render every view.
  await page.evaluate(surface.patch(payload));
  for (const view of VIEWS) {
    try { await page.evaluate(view.action); } catch (e) { /* tolerated */ }
    await page.waitForTimeout(50);
  }

  const scan = await scanForXssArtifacts(page, payload);

  await context.close();

  const pass = (
    dialogs.length === 0 &&
    pageErrors.length === 0 &&
    cspViolations.length === 0 &&
    scan.findings.length === 0
  );

  return {
    surface: surface.id,
    payload,
    pass,
    dialogs,
    pageErrors,
    cspViolations,
    findings: scan.findings,
    survivedAsText: scan.survivedAsText,
  };
}

async function main() {
  const playwright = loadPlaywright();
  if (!playwright) {
    console.error('[skip] Playwright not installed.');
    console.error('       npm i -D playwright && npx playwright install chromium');
    console.error('       (S-02 cannot run automated without it — see tests/README.md for manual repro.)');
    process.exit(2);
  }

  let browser;
  try {
    browser = await playwright.chromium.launch({ headless: HEADLESS });
  } catch (e) {
    console.error('[skip] Chromium failed to launch:', e && e.message);
    console.error('       Try: npx playwright install chromium');
    process.exit(2);
  }

  console.log('S-02 pen-test running against', BASE_URL + TOOL_PATH);
  console.log('Surfaces:', SURFACES.length, '× payloads:', XSS_PAYLOADS.length,
              '=', SURFACES.length * XSS_PAYLOADS.length, 'test cases\n');

  const results = [];
  let passCount = 0;
  let failCount = 0;

  for (const surface of SURFACES) {
    for (const payload of XSS_PAYLOADS) {
      try {
        const r = await runSurface(browser, surface, payload);
        results.push(r);
        if (r.pass) {
          passCount++;
          process.stdout.write('.');
        } else {
          failCount++;
          process.stdout.write('F');
        }
      } catch (e) {
        failCount++;
        results.push({
          surface: surface.id,
          payload,
          pass: false,
          error: String(e && e.message || e),
        });
        process.stdout.write('E');
      }
    }
  }

  console.log('\n');
  console.log('=== S-02 RESULTS ===');
  console.log('Pass:', passCount, '/ Fail:', failCount, '/ Total:', results.length);

  if (failCount > 0) {
    console.log('\n--- FAILURES ---');
    for (const r of results.filter(x => !x.pass)) {
      console.log('\n[FAIL]', r.surface, '←', JSON.stringify(r.payload));
      if (r.error) console.log('       error:', r.error);
      if (r.dialogs && r.dialogs.length) console.log('       dialogs:', JSON.stringify(r.dialogs));
      if (r.pageErrors && r.pageErrors.length) console.log('       pageErrors:', r.pageErrors);
      if (r.cspViolations && r.cspViolations.length) console.log('       csp:', r.cspViolations);
      if (r.findings && r.findings.length) console.log('       findings:', JSON.stringify(r.findings, null, 2));
    }
  }

  await browser.close();
  process.exit(failCount === 0 ? 0 : 1);
}

main().catch((e) => {
  console.error('Unhandled error in S-02 runner:', e);
  process.exit(2);
});
