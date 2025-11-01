document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("tr[data-href]").forEach((row) => {
    row.addEventListener("click", () => {
      window.location = row.dataset.href;
    });
  });
});
