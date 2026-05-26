// src/routes/admin/+layout.js
import { getSession } from "$lib/db/services/auth.js";
import { redirect } from "@sveltejs/kit";

export async function load() {
  const { role, level } = await getSession();

  if (role !== "employee" || level !== 2) {
    redirect(303, "/auth/login");
  }
}
