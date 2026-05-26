// src/lib/utils/logger/interceptor.js
// ⚠️  Solo desarrollo — activar una vez en hooks.server.js
import fs from "fs";
import path from "path";

const LOG_DIR = "logs";
const LOG_FILE = path.join(
  LOG_DIR,
  `${new Date().toISOString().split("T")[0]}.log`,
);

if (!fs.existsSync(LOG_DIR)) fs.mkdirSync(LOG_DIR);

/**
 * Sobreescribe console.log/warn/error para que también escriban en disco.
 * Solo activo en desarrollo — no hace nada en producción.
 * Llamar una sola vez en hooks.server.js
 *
 * @example
 * // src/hooks.server.js
 * import { interceptConsole } from '$lib/utils/logger/interceptor.js';
 * interceptConsole();
 */
export function interceptConsole() {
  if (import.meta.env.PROD) return;

  const _log = console.log.bind(console);
  const _warn = console.warn.bind(console);
  const _error = console.error.bind(console);

  const toFile = (label, args) => {
    const timestamp = new Date().toISOString();
    const message = args
      .map((a) => (typeof a === "object" ? JSON.stringify(a) : String(a)))
      .join(" ");
    fs.appendFileSync(
      LOG_FILE,
      `[${timestamp}] [${label}] ${message}\n`,
      "utf8",
    );
  };

  console.log = (...args) => {
    _log(...args);
    toFile("LOG  ", args);
  };

  console.warn = (...args) => {
    _warn(...args);
    toFile("WARN ", args);
  };

  console.error = (...args) => {
    _error(...args);
    toFile("ERROR", args);
  };
}
