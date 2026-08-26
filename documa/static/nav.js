/* Shared top-nav menu toggle for the landing and docs pages.
   Below 860px the .nav__links list is re-used as a dropdown panel. */
(function () {
  var toggle = document.getElementById("nav-toggle");
  var menu = document.getElementById("nav-menu");
  if (!toggle || !menu) return;

  function setOpen(open) {
    menu.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", String(open));
  }

  toggle.addEventListener("click", function (e) {
    e.stopPropagation();
    setOpen(!menu.classList.contains("is-open"));
  });

  // Choosing a destination closes the panel, as does a click outside it.
  menu.addEventListener("click", function () { setOpen(false); });
  document.addEventListener("click", function (e) {
    if (!menu.contains(e.target) && !toggle.contains(e.target)) setOpen(false);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") setOpen(false);
  });

  // Returning to desktop widths must not strand the is-open class on what is
  // once again a plain inline row.
  window.addEventListener("resize", function () {
    if (window.innerWidth > 860) setOpen(false);
  });
})();
