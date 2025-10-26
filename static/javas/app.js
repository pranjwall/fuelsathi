const header = document.querySelector("header");

window.addEventListener("scroll", function () {
  header.classList.toggle("sticky", window.scrollY > 0);
});

document.addEventListener("DOMContentLoaded", () => {
  const navLinks = document.querySelectorAll(".nav-link[data-section]");
  const sections = document.querySelectorAll(".section");
  const welcomeSection = document.getElementById("welcome-section");

  navLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();

      // Remove active class from all links
      navLinks.forEach((l) => l.classList.remove("active"));
      link.classList.add("active");

      // Hide all sections
      sections.forEach((sec) => sec.classList.add("hidden"));

      // Hide welcome only if a section clicked
      const sectionId = link.getAttribute("data-section");
      if (sectionId) {
        document.getElementById(sectionId).classList.remove("hidden");
        welcomeSection.classList.add("hidden");
      }
    });
  });
});
