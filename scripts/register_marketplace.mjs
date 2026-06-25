#!/usr/bin/env node
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { homedir } from "node:os";
import { fileURLToPath } from "node:url";

const pluginName = "imagen-design-hub";
const scriptDir = dirname(fileURLToPath(import.meta.url));
const pluginRoot = resolve(scriptDir, "..");
const marketplacePath = resolve(homedir(), ".agents", "plugins", "marketplace.json");

function readJson(path) {
  try {
    return JSON.parse(readFileSync(path, "utf8"));
  } catch (error) {
    if (error.code === "ENOENT") {
      return {
        name: "personal",
        interface: {
          displayName: "Personal Plugins",
        },
        plugins: [],
      };
    }
    throw error;
  }
}

const payload = readJson(marketplacePath);
if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
  throw new Error(`${marketplacePath} must contain a JSON object.`);
}

payload.name ||= "personal";
payload.interface ||= { displayName: "Personal Plugins" };
payload.plugins ||= [];
if (!Array.isArray(payload.plugins)) {
  throw new Error(`${marketplacePath} field "plugins" must be an array.`);
}

const entry = {
  name: pluginName,
  source: {
    source: "local",
    path: `./plugins/${pluginName}`,
  },
  policy: {
    installation: "AVAILABLE",
    authentication: "ON_INSTALL",
  },
  category: "Design",
};

const index = payload.plugins.findIndex((plugin) => plugin && plugin.name === pluginName);
if (index >= 0) {
  payload.plugins[index] = entry;
} else {
  payload.plugins.push(entry);
}

mkdirSync(dirname(marketplacePath), { recursive: true });
writeFileSync(marketplacePath, `${JSON.stringify(payload, null, 2)}\n`);

console.log(`Registered ${pluginName}`);
console.log(`Plugin root: ${pluginRoot}`);
console.log(`Marketplace: ${marketplacePath}`);
