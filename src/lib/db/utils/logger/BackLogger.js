// src/lib/utils/logger/backlogger.js
// ⚠️  Solo servidor — no importar en componentes .svelte
import fs from "fs";
import path from "path";

// ─────────────────────────────────────────
// CONFIGURACIÓN
// ─────────────────────────────────────────

const LOG_DIR = "logs";
const LOG_FILE = path.join(
  LOG_DIR,
  `${new Date().toISOString().split("T")[0]}.log`,
);

const LEVELS = { debug: 0, info: 1, warn: 2, error: 3 };
const MIN_LEVEL = LEVELS.debug;

const COLORS = {
  debug: "\x1b[36m", // cyan
  info: "\x1b[32m", // green
  warn: "\x1b[33m", // yellow
  error: "\x1b[31m", // red
  reset: "\x1b[0m",
};

if (!fs.existsSync(LOG_DIR)) fs.mkdirSync(LOG_DIR);

// ─────────────────────────────────────────
// HELPER INTERNO
// ─────────────────────────────────────────

/**
 * Formatea y escribe el log en consola y en disco.
 *
 * @param {'debug' | 'info' | 'warn' | 'error'} level
 * @param {string} message
 * @param {object} [meta]
 */
function write(level, message, meta) {
  if (LEVELS[level] < MIN_LEVEL) return;

  const timestamp = new Date().toISOString();
  const metaStr = meta ? ` ${JSON.stringify(meta)}` : "";
  const fileLine = `[${timestamp}] [${level.toUpperCase().padEnd(5)}] ${message}${metaStr}\n`;
  const color = COLORS[level];
  const consoleLine = `${color}[${level.toUpperCase().padEnd(5)}]${COLORS.reset} ${message}${metaStr}`;

  if (level === "error") console.error(consoleLine);
  else if (level === "warn") console.warn(consoleLine);
  else console.log(consoleLine);

  fs.appendFileSync(LOG_FILE, fileLine, "utf8");
}

// ─────────────────────────────────────────
// API PÚBLICA
// ─────────────────────────────────────────

/** @param {string} message @param {object} [meta] */
export const debug = (message, meta) => write("debug", message, meta);

/** @param {string} message @param {object} [meta] */
export const info = (message, meta) => write("info", message, meta);

/** @param {string} message @param {object} [meta] */
export const warn = (message, meta) => write("warn", message, meta);

/** @param {string} message @param {object} [meta] */
export const error = (message, meta) => write("error", message, meta);

/**
 * Crea un logger con contexto para identificar el origen del log.
 *
 * @param {string} context
 * @returns {{ debug, info, warn, error }}
 *
 * @example
 * const log = createLogger('products');
 * log.info('Producto agregado', { productId: 5 });
 * // [INFO ] [products] Producto agregado {"productId":5}
 */
export function createLogger(context) {
  return {
    debug: (message, meta) => write("debug", `[${context}] ${message}`, meta),
    info: (message, meta) => write("info", `[${context}] ${message}`, meta),
    warn: (message, meta) => write("warn", `[${context}] ${message}`, meta),
    error: (message, meta) => write("error", `[${context}] ${message}`, meta),
  };
}
