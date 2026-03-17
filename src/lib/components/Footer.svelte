<footer>
  <div class="container footer-grid">

    <div class="footer-marca">
      <span class="footer-nombre">Chucheritas Aralan 💗</span>
      <p>Lo mejor para tu estilo, con amor desde México.</p>
    </div>

    <div class="footer-col">
      <h4>Contacto</h4>
      <p>📧 info@chucheritas.com</p>
      <p>ig: chucheritas aralan</p>
      <p>📞 +52 55 1234 5678</p>
    </div>

  </div>

  <div class="footer-bottom">
    <p>© {new Date().getFullYear()} Chucheritas Aralan. Todos los derechos reservados.</p>
  </div>
</footer>

<style>
  @reference "../../app.css";
footer {
  @apply text-[white] mt-20 pt-[50px];
  background: var(--rosa);
}
.footer-grid {
  @apply grid grid-cols-[2fr_1fr] gap-12 pb-10;
}
.footer-nombre {
  @apply text-[1.3rem] block mb-[0.6rem];
  font-family: var(--font-display);
}
.footer-marca p {
  @apply opacity-[0.85] text-[0.92rem];
}
.footer-col h4 {
  @apply text-[0.82rem] font-bold uppercase tracking-[0.06em] opacity-90 mb-4;
}
.footer-col p {
  @apply opacity-[0.85] text-[0.9rem] mb-[0.4rem];
}
.footer-bottom {
  @apply text-center text-[0.82rem] opacity-75 px-6 py-[18px] border-t-[rgba(255,255,255,0.25)] border-t border-solid;
}
@media (max-width: 768px) {
  .footer-grid {
    @apply grid-cols-[1fr] gap-8;
  }
}
</style>