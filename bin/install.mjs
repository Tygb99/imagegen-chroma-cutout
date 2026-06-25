#!/usr/bin/env node
import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { homedir } from "node:os";
import { spawnSync } from "node:child_process";

const repoUrl = process.env.IMAGEN_DESIGN_HUB_REPO || "https://github.com/Tygb99/imagen-design-hub.git";
const pluginDir = resolve(process.env.IMAGEN_DESIGN_HUB_PLUGIN_DIR || `${homedir()}/plugins/imagen-design-hub`);

function run(command, args, options = {}) {
  const result = spawnSync(command, args, {
    encoding: "utf8",
    stdio: options.capture ? ["ignore", "pipe", "pipe"] : "inherit",
  });
  if (result.status !== 0) {
    const detail = options.capture ? result.stderr || result.stdout : "";
    throw new Error(`${command} ${args.join(" ")} failed${detail ? `: ${detail.trim()}` : ""}`);
  }
  return (result.stdout || "").trim();
}

function commandExists(command) {
  const result = spawnSync(command, ["--version"], {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
  });
  return result.status === 0;
}

function ensureTools() {
  for (const command of ["git", "node"]) {
    if (!commandExists(command)) {
      throw new Error(`${command} is required.`);
    }
  }
}

function installOrUpdatePlugin() {
  if (existsSync(resolve(pluginDir, ".git"))) {
    run("git", ["-C", pluginDir, "pull", "--ff-only"]);
    return;
  }

  if (existsSync(pluginDir)) {
    throw new Error(`${pluginDir} exists but is not a git checkout. Move it away or set IMAGEN_DESIGN_HUB_PLUGIN_DIR.`);
  }

  run("git", ["clone", repoUrl, pluginDir]);
}

function registerMarketplace() {
  const registerScript = resolve(pluginDir, "scripts/register_marketplace.mjs");
  if (!existsSync(registerScript)) {
    throw new Error(`Missing marketplace registration script: ${registerScript}`);
  }
  run("node", [registerScript]);
}

function main() {
  ensureTools();
  installOrUpdatePlugin();
  registerMarketplace();
  console.log(`Installed Imagen Design Hub plugin at ${pluginDir}`);
  console.log("Restart Codex or reopen the plugin picker if the new plugin is not visible yet.");
}

try {
  main();
} catch (error) {
  console.error(`[imagen-design-hub] ${error.message}`);
  process.exit(1);
}
