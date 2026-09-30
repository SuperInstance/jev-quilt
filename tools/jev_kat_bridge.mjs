#!/usr/bin/env node
/**
 * jev_kat_bridge.mjs — characterisation gate bridging the fleet KAT into jev-quilt.
 *
 * WHY
 *
 * AI-Writings PR #70 (merged 2026-09-29T21:26:53Z) shipped labs/jev-kat/jev_kat.mjs:
 * a known-answer control (KAT) for the JEV oracle instrument. jev-quilt consumes that
 * instrument (the p>0.7 canon gate per JEV_ORACLE_SPEC). A consumer that never
 * characterises its instrument is trusting, not verifying. This bridge makes the
 * characterisation a gate artefact INSIDE jev-quilt without copying the instrument.
 *
 * NO VERDICT MUTATION (commissioned constraint)
 *
 * This bridge NEVER mutates jev_quilt verdicts, receipts, ledgers, or any canon state.
 * It only RUNS the canonical instrument and GATES the resulting receipt. The instrument
 * stays canonical in AI-Writings; jev-quilt pins it by commit + sha256 and records the
 * characterisation as a session artefact under jev_sessions/.
 *
 * USAGE
 *   node tools/jev_kat_bridge.mjs run [--json-out PATH]
 *       Fetch the canonical instrument (pinned commit, sha256-verified), run it with
 *       the live key, write a characterisation receipt. Exit 0 = instrument CHARACTERISED
 *       for the canon-gate regime; exit 2 = DEGRADED (a type the canon gate depends on
 *       failed its KAT bar). Requires TYPESAFEAI_KEY and network.
 *
 *   node tools/jev_kat_bridge.mjs gate <receipt.json>
 *       Offline: evaluate an existing receipt through the gate. No network, no key.
 *       Exit 0 CHARACTERISED / 2 DEGRADED / 3 schema-invalid. This is what the suite
 *       pins, so the gate logic is testable without the live instrument.
 *
 * GATE RULE
 *   The fleet canon gate lives in noul regime B (judgement against stated criteria).
 *   The gate therefore tracks: noul regimeB passes, choice discriminates, and — in full
 *   runs — score discriminates. score's known near-constant failure is DEGRADED for any
 *   absolute-threshold use but does not block the canon gate, which never uses score.
 */

import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

export const INSTRUMENT = {
  repo: 'SuperInstance/AI-Writings',
  commit: '3f8405888366e3697b3775017fa5fe13d6244226',
  path: 'labs/jev-kat/jev_kat.mjs',
  sha256: '5f280b8b435852872fadeb449f4382275e80be56e80035da02274db8006e1cc5',
};

const SCHEMA = 'fleet/jev-kat@v1';

export function sha256(buf) {
  return createHash('sha256').update(buf).digest('hex');
}

/**
 * The gate. Pure function over a parsed KAT receipt — this is the pinned surface.
 *
 * Returns { verdict: 'CHARACTERISED' | 'DEGRADED' | 'SCHEMA_INVALID', reasons: [...] }.
 * The canon gate depends on noul regime B (and choice as a sanity instrument). score is
 * advisory: a score failure degrades score-threshold uses but never the canon gate, and
 * is reported in reasons, never silently dropped.
 */
export function gate(receipt) {
  const reasons = [];
  if (!receipt || typeof receipt !== 'object' || receipt.schema !== SCHEMA) {
    return { verdict: 'SCHEMA_INVALID', reasons: [`schema must be ${SCHEMA}`] };
  }
  const noul = receipt.noul;
  if (!noul || typeof noul !== 'object') {
    return { verdict: 'SCHEMA_INVALID', reasons: ['missing noul result'] };
  }
  if (noul.regimeB?.passes !== true) {
    reasons.push('noul regime B (the canon-gate regime) failed its KAT bar');
  }
  if (noul.regimeA1?.passes === false) {
    reasons.push('noul A1 overconfidence: instrument answers unknowable facts confidently');
  }
  const choice = receipt.choice;
  if (choice && choice.discriminates === false) {
    reasons.push('choice instrument does not discriminate');
  }
  // score: advisory-only, recorded honestly.
  if (receipt.score && receipt.score.discriminates === false) {
    reasons.push('score does not discriminate — any absolute-threshold use of score is degraded (canon gate unaffected: it never uses score)');
  }
  const verdict = reasons.some(r => r.startsWith('noul regime B') || r.startsWith('choice')) ? 'DEGRADED' : 'CHARACTERISED';
  return { verdict, reasons };
}

export function instrumentUrl() {
  return `https://raw.githubusercontent.com/${INSTRUMENT.repo}/${INSTRUMENT.commit}/${INSTRUMENT.path}`;
}

async function cmdRun(jsonOut) {
  const key = process.env.TYPESAFEAI_KEY;
  if (!key) { console.error('TYPESAFEAI_KEY not set — live characterisation skipped'); process.exit(2); }

  const src = await fetch(instrumentUrl());
  if (!src.ok) { console.error(`instrument fetch failed: HTTP ${src.status}`); process.exit(2); }
  const code = Buffer.from(await src.arrayBuffer());
  const digest = sha256(code);
  if (digest !== INSTRUMENT.sha256) {
    console.error(`instrument sha256 mismatch: got ${digest}, pinned ${INSTRUMENT.sha256}`); process.exit(2);
  }

  const dir = mkdtempSync(join(tmpdir(), 'jev-kat-'));
  const instrumentPath = join(dir, 'jev_kat.mjs');
  writeFileSync(instrumentPath, code);

  const child = spawnSync(process.execPath, [instrumentPath, '--json'], {
    env: { ...process.env, TYPESAFEAI_KEY: key },
    encoding: 'utf8',
    maxBuffer: 16 * 1024 * 1024,
    timeout: 10 * 60 * 1000,
  });
  if (child.error) { console.error(`instrument run failed: ${child.error.message}`); process.exit(2); }

  // The instrument prints human lines then the JSON blob on the final line.
  const lines = (child.stdout || '').trim().split('\n');
  const receipt = JSON.parse(lines[lines.length - 1]);
  const result = gate(receipt);
  const record = {
    bridge: 'jev-quilt/tools/jev_kat_bridge.mjs',
    instrument: { ...INSTRUMENT, sha256_verified: digest },
    gated: result,
    receipt,
  };
  const out = jsonOut || `jev_sessions/kat-characterisation-${receipt.ts?.replace(/[:.]/g, '-') || Date.now()}.json`;
  writeFileSync(out, JSON.stringify(record, null, 2));
  console.log(`instrument: ${INSTRUMENT.repo}@${INSTRUMENT.commit.slice(0, 8)} sha256 ${digest.slice(0, 12)}…`);
  console.log(`receipt:   ${out}`);
  console.log(`verdict:   ${result.verdict}`);
  for (const r of result.reasons) console.log(`  - ${r}`);
  process.exit(result.verdict === 'CHARACTERISED' ? 0 : 2);
}

function cmdGate(path) {
  let receipt;
  try {
    receipt = JSON.parse(readFileSync(path, 'utf8'));
  } catch (e) {
    console.error(`unreadable receipt: ${e.message}`); process.exit(3);
  }
  // Accept both raw instrument output and a bridged record (unwrap).
  const kat = receipt.bridge ? receipt.receipt : receipt;
  const result = gate(kat);
  console.log(`${path}: ${result.verdict}`);
  for (const r of result.reasons) console.log(`  - ${r}`);
  process.exit(result.verdict === 'SCHEMA_INVALID' ? 3 : (result.verdict === 'CHARACTERISED' ? 0 : 2));
}

const [, , cmd, ...rest] = process.argv;
if (cmd === 'run') cmdRun(rest[rest.indexOf('--json-out') + 1] || null);
else if (cmd === 'gate') cmdGate(rest[0]);
else {
  console.error('usage: jev_kat_bridge.mjs run [--json-out PATH] | gate <receipt.json>');
  process.exit(2);
}
