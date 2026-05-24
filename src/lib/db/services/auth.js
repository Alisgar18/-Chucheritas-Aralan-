// src/lib/db/services/auth.js
import { supabase } from "../public-client.js";

// ─────────────────────────────────────────
// REGISTRO DE CLIENTE
// ─────────────────────────────────────────

/**
 * Registra un nuevo cliente en Supabase Auth.
 * El trigger handle_new_user se encarga de insertar en clients.clients.
 *
 * @param {{ name: string, email: string, password: string, phone: string }} data
 * @returns {{ error: string | null }}
 */
export async function registerClient({ name, email, password, phone }) {
  const { error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      data: {
        role: "client",
        name,
        phone,
      },
    },
  });

  if (error) return { error: error.message };
  return { error: null };
}

// ─────────────────────────────────────────
// LOGIN
// ─────────────────────────────────────────

/**
 * Inicia sesión con email y password.
 * Funciona para clientes y empleados.
 *
 * @param {{ email: string, password: string }} data
 * @returns {{ role: 'client' | 'employee' | null, level: number | null, error: string | null }}
 */
export async function login({ email, password }) {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });

  if (error) return { role: null, level: null, error: error.message };

  // Determinar si es cliente o empleado y su nivel
  const role = await resolveRole(data.user.id);
  return { ...role, error: null };
}

// ─────────────────────────────────────────
// LOGOUT
// ─────────────────────────────────────────

/**
 * Cierra la sesión del usuario actual.
 *
 * @returns {{ error: string | null }}
 */
export async function logout() {
  const { error } = await supabase.auth.signOut();
  if (error) return { error: error.message };
  return { error: null };
}

// ─────────────────────────────────────────
// SESIÓN ACTUAL
// ─────────────────────────────────────────

/**
 * Devuelve el usuario autenticado actual y su rol.
 * Útil para proteger rutas y mostrar UI según rol.
 *
 * @returns {{ user: object | null, role: 'client' | 'employee' | null, level: number | null, error: string | null }}
 */
export async function getSession() {
  const {
    data: { user },
    error,
  } = await supabase.auth.getUser();

  if (error || !user)
    return {
      user: null,
      role: null,
      level: null,
      error: error?.message ?? null,
    };

  const role = await resolveRole(user.id);
  return { user, ...role, error: null };
}

// ─────────────────────────────────────────
// HELPER INTERNO — resolver rol del usuario
// ─────────────────────────────────────────

/**
 * Determina si el auth_id pertenece a un cliente o empleado
 * y devuelve su nivel (null para clientes, 1 o 2 para empleados).
 *
 * @param {string} authId
 * @returns {{ role: 'client' | 'employee' | null, level: number | null }}
 */
async function resolveRole(authId) {
  // ¿Es cliente?
  const { data: client } = await supabase
    .from("clients")
    .select("client_id")
    .eq("auth_id", authId)
    .maybeSingle();

  if (client) return { role: "client", level: null };

  // ¿Es empleado?
  const { data: employee } = await supabase
    .from("employees")
    .select("employee_id, jobs(level)")
    .eq("auth_id", authId)
    .maybeSingle();

  if (employee) return { role: "employee", level: employee.jobs.level };

  return { role: null, level: null };
}
