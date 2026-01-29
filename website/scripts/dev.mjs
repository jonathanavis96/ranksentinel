import { readFileSync } from "node:fs";
import { spawn } from "node:child_process";

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
