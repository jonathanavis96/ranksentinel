import { existsSync, readFileSync, unlinkSync } from "node:fs";
import { spawn, spawnSync } from "node:child_process";
import path from "node:path";

function isWSL() {
  // WSL2 kernels include "microsoft" in /proc/version.
  // Keep this dependency-free and fast.
  try {
    const v = readFileSync("/proc/version", "utf8");
    return /microsoft/i.test(v);
  } catch {
    return false;
  }
}

const wsl = isWSL();

const projectRoot = process.cwd();
const devLockPath = path.join(projectRoot, ".next", "dev", "lock");

function isNextDevRunningForThisProject() {
  // Heuristic: `ps` command lines include the absolute path to
  // `website/node_modules/.bin/next` when Next is launched from this folder.
  const res = spawnSync("ps", ["-eo", "args"], { encoding: "utf8" });
  if (res.status !== 0) return false;

  return res.stdout
    .split("\n")
    .some((line) => line.includes("next dev") && line.includes(projectRoot));
}

// If a previous dev server crashed, Next can leave a stale lock behind.
// Only remove it when we're confident no dev server is running for *this* project.
if (existsSync(devLockPath) && !isNextDevRunningForThisProject()) {
  try {
    unlinkSync(devLockPath);
    console.warn(`Removed stale Next dev lock: ${devLockPath}`);
  } catch {
    // Ignore; Next will surface a clear error if it can't acquire the lock.
  }
}

// Next.js 16 defaults to Turbopack for `next dev`.
// In WSL, file watching can easily hit fd limits (EMFILE) due to large trees.
// Webpack + polling is slower but reliable.
const nextArgs = ["dev", ...(wsl ? ["--webpack"] : [])];

const env = {
  ...process.env,
  ...(wsl
    ? {
        WATCHPACK_POLLING: process.env.WATCHPACK_POLLING ?? "true",
        WATCHPACK_POLLING_INTERVAL:
          process.env.WATCHPACK_POLLING_INTERVAL ?? "1000",
      }
    : {}),
};

const child = spawn("next", nextArgs, {
  stdio: "inherit",
  env,
});

child.on("exit", (code, signal) => {
  if (signal) process.kill(process.pid, signal);
  process.exit(code ?? 1);
});
