#!/usr/bin/env node
import { execFileSync, spawnSync } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const pluginRoot = process.env.PLUGIN_ROOT || resolve(scriptDir, "..");

function git(args, options = {}) {
  return execFileSync("git", ["-C", pluginRoot, ...args], {
    encoding: "utf8",
    stdio: options.stdio || ["ignore", "pipe", "pipe"],
  }).trim();
}

function tryGit(args) {
  const result = spawnSync("git", ["-C", pluginRoot, ...args], {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
  });
  return {
    ok: result.status === 0,
    stdout: (result.stdout || "").trim(),
    stderr: (result.stderr || "").trim(),
  };
}

function shortSha(value) {
  return value ? value.slice(0, 7) : "unknown";
}

function main() {
  const inside = tryGit(["rev-parse", "--is-inside-work-tree"]);
  if (!inside.ok || inside.stdout !== "true") {
    return;
  }

  const remote = tryGit(["remote", "get-url", "origin"]);
  if (!remote.ok || !remote.stdout) {
    return;
  }

  const dirty = tryGit(["status", "--porcelain=v1", "--untracked-files=all"]);
  if (!dirty.ok || dirty.stdout) {
    console.log("[Imagen Design Hub] Auto-update skipped: local changes are present.");
    return;
  }

  const branch = tryGit(["branch", "--show-current"]);
  if (!branch.ok || !branch.stdout) {
    return;
  }

  let upstream = tryGit(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"]);
  if (!upstream.ok || !upstream.stdout) {
    const fallback = `origin/${branch.stdout}`;
    const fallbackCheck = tryGit(["rev-parse", "--verify", fallback]);
    if (!fallbackCheck.ok) {
      return;
    }
    upstream = { ok: true, stdout: fallback };
  }

  const before = git(["rev-parse", "HEAD"]);
  const fetch = tryGit(["fetch", "--quiet", "--prune", "origin"]);
  if (!fetch.ok) {
    return;
  }

  const upstreamSha = tryGit(["rev-parse", upstream.stdout]);
  if (!upstreamSha.ok || !upstreamSha.stdout || upstreamSha.stdout === before) {
    return;
  }

  const fastForwardable = tryGit(["merge-base", "--is-ancestor", "HEAD", upstream.stdout]);
  if (!fastForwardable.ok) {
    console.log("[Imagen Design Hub] Auto-update skipped: remote is not a fast-forward.");
    return;
  }

  const pull = tryGit(["pull", "--ff-only", "--quiet"]);
  if (!pull.ok) {
    return;
  }

  const after = git(["rev-parse", "HEAD"]);
  if (after !== before) {
    console.log(`[Imagen Design Hub] Auto-update applied: ${shortSha(before)} -> ${shortSha(after)}.`);
  }
}

try {
  main();
} catch {
  process.exit(0);
}
