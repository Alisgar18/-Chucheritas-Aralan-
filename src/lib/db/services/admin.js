// src/lib/db/services/admin.js
import { supabase } from "../public-client.js";

// ─────────────────────────────────────────
// STATS
// ─────────────────────────────────────────

/**
 * Devuelve las ventas del día desde la vista v_today_sales.
 *
 * @returns {{ data: object | null, error: string | null }}
 */
export async function getTodaySales() {
  const { data, error } = await supabase
    .from("v_today_sales")
    .select("*")
    .maybeSingle();

  if (error) return { data: null, error: error.message };
  return { data, error: null };
}

/**
 * Devuelve el top 10 de productos más vendidos desde v_top_products.
 *
 * @returns {{ data: object[] | null, error: string | null }}
 */
export async function getTopProducts() {
  const { data, error } = await supabase.from("v_top_products").select("*");

  if (error) return { data: null, error: error.message };
  return { data, error: null };
}

// ─────────────────────────────────────────
// GESTIÓN DE CLIENTES
// ─────────────────────────────────────────

/**
 * Devuelve todos los clientes.
 *
 * @returns {{ data: object[] | null, error: string | null }}
 */
export async function getClients() {
  const { data, error } = await supabase
    .from("clients")
    .select("*")
    .order("name");

  if (error) return { data: null, error: error.message };
  return { data, error: null };
}

/**
 * Suspende o reactiva un cliente.
 *
 * @param {number} clientId
 * @param {'active' | 'suspended'} status
 * @returns {{ error: string | null }}
 */
export async function setClientStatus(clientId, status) {
  const { error } = await supabase
    .from("clients")
    .update({ status })
    .eq("client_id", clientId);

  if (error) return { error: error.message };
  return { error: null };
}

// ─────────────────────────────────────────
// GESTIÓN DE EMPLEADOS
// ─────────────────────────────────────────

/**
 * Devuelve todos los empleados con su puesto.
 *
 * @returns {{ data: object[] | null, error: string | null }}
 */
export async function getEmployees() {
  const { data, error } = await supabase
    .from("employees")
    .select(`*, jobs(name, level)`)
    .order("name");

  if (error) return { data: null, error: error.message };
  return { data, error: null };
}

/**
 * Devuelve solo los repartidores activos.
 * Útil al crear un pedido para asignar repartidor.
 *
 * @returns {{ data: object[] | null, error: string | null }}
 */
export async function getDeliverers() {
  const { data, error } = await supabase
    .from("employees")
    .select(`employee_id, name, phone, jobs!inner(level)`)
    .eq("status", "active")
    .eq("jobs.level", 1)
    .order("name");

  if (error) return { data: null, error: error.message };
  return { data, error: null };
}

/**
 * Suspende o reactiva un empleado.
 *
 * @param {number} employeeId
 * @param {'active' | 'inactive'} status
 * @returns {{ error: string | null }}
 */
export async function setEmployeeStatus(employeeId, status) {
  const { error } = await supabase
    .from("employees")
    .update({ status })
    .eq("employee_id", employeeId);

  if (error) return { error: error.message };
  return { error: null };
}

// ─────────────────────────────────────────
// PERFILES
// ─────────────────────────────────────────

/**
 * Actualiza el perfil de un cliente (nombre y/o teléfono).
 *
 * @param {number} clientId
 * @param {{ name?: string, phone?: string }} fields
 * @returns {{ error: string | null }}
 */
export async function updateClientProfile(clientId, { name, phone }) {
  const { error } = await supabase.rpc("update_profile", {
    p_client_id: clientId,
    p_name: name ?? null,
    p_phone: phone ?? null,
  });

  if (error) return { error: error.message };
  return { error: null };
}

/**
 * Actualiza el perfil de un empleado (nombre y/o teléfono).
 *
 * @param {number} employeeId
 * @param {{ name?: string, phone?: string }} fields
 * @returns {{ error: string | null }}
 */
export async function updateEmployeeProfile(employeeId, { name, phone }) {
  const { error } = await supabase.rpc("update_employee_profile", {
    p_employee_id: employeeId,
    p_name: name ?? null,
    p_phone: phone ?? null,
  });

  if (error) return { error: error.message };
  return { error: null };
}
