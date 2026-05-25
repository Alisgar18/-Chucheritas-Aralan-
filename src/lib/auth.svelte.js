// src/lib/auth.svelte.js
import { onMount } from 'svelte';

// Función para inicializar el estado desde localStorage (solo si estamos en el navegador)
function getInitialAuth() {
    if (typeof window !== 'undefined') {
        const savedAuth = localStorage.getItem('auth');
        if (savedAuth) {
            return JSON.parse(savedAuth);
        }
    }
    return { isLoggedIn: false, user: null };
}

export const auth = $state(getInitialAuth());

export function login(userData) {
    auth.isLoggedIn = true;
    auth.user = userData;
    // Guardamos en localStorage
    if (typeof window !== 'undefined') {
        localStorage.setItem('auth', JSON.stringify({ isLoggedIn: true, user: userData }));
    }
}

export function logout() {
    auth.isLoggedIn = false;
    auth.user = null;
    // Limpiamos localStorage
    if (typeof window !== 'undefined') {
        localStorage.removeItem('auth');
    }
}