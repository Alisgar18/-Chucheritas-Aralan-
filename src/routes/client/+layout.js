// src/routes/client/+layout.js
// Solo clientes activos
import { getSession } from "$lib/db/services/auth.js";
import { redirect } from "@sveltejs/kit";

export async function load() {
  const { role, user, error } = await getSession();

  if (error || !role) redirect(303, "/auth/login");
  if (role !== "client") redirect(303, "/auth/login");

  // Pasar datos del usuario a todas las páginas hijas
  return { user };
}
