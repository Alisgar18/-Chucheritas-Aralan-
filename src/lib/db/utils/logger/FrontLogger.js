// src/lib/utils/logger/frontlogger.js
// ⚠️  Solo browser — no importar en +page.server.js ni +server.js

// ─────────────────────────────────────────
// CONFIGURACIÓN
// ─────────────────────────────────────────

const LEVELS = { debug: 0, info: 1, warn: 2, error: 3 };
const MIN_LEVEL = LEVELS.debug;

const STYLES = {
  debug: "color: #06b6d4; font-weight: bold", // cyan
  info: "color: #22c55e; font-weight: bold", // green
  warn: "color: #f59e0b; font-weight: bold", // yellow
  error: "color: #ef4444; font-weight: bold", // red
};

// ─────────────────────────────────────────
// HELPER INTERNO
// ─────────────────────────────────────────

/**
 * Formatea y escribe el log en consola del browser con estilo.
 *
 * @param {'debug' | 'info' | 'warn' | 'error'} level
 * @param {string} message
 * @param {object} [meta]
 */
function write(level, message, meta) {
  if (LEVELS[level] < MIN_LEVEL) return;

  const timestamp = new Date().toLocaleTimeString("es-MX", { hour12: false });
  const label = `%c[${level.toUpperCase().padEnd(5)}]%c ${timestamp} — ${message}`;
  const style = STYLES[level];
  const args = [label, style, "color: inherit", ...(meta ? [meta] : [])];

  if (level === "error") console.error(...args);
  else if (level === "warn") console.warn(...args);
  else console.log(...args);
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
 * const log = createLogger('carrito');
 * log.warn('Producto sin stock', { productId: 3 });
 * // [WARN ] 18:32:01 — [carrito] Producto sin stock {productId: 3}
 */
export function createLogger(context) {
  return {
    debug: (message, meta) => write("debug", `[${context}] ${message}`, meta),
    info: (message, meta) => write("info", `[${context}] ${message}`, meta),
    warn: (message, meta) => write("warn", `[${context}] ${message}`, meta),
    error: (message, meta) => write("error", `[${context}] ${message}`, meta),
  };
}
