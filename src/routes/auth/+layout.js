// src/routes/auth/+layout.js
// Protección inversa — si ya hay sesión redirige según rol
import { getSession } from "$lib/db/services/auth.js";
import { redirect } from "@sveltejs/kit";

export async function load() {
  const { role, level, error } = await getSession();

  if (error || !role) return {}; // sin sesión, puede ver login/register

  // Ya tiene sesión — redirigir según rol
  if (role === "client") redirect(303, "/client/orders");
  if (role === "employee" && level === 1) redirect(303, "/deliverer");
  if (role === "employee" && level === 2) redirect(303, "/admin");
}
