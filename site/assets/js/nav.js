// Highlights the active nav link based on the current page filename.
document.addEventListener("DOMContentLoaded", function () {
  var path = window.location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll(".nav__links a").forEach(function (a) {
    var href = a.getAttribute("href");
    if (href === path || (path === "" && href === "index.html")) {
      a.classList.add("active");
    }
  });
});
