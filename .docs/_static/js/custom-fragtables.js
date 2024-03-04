document.addEventListener("DOMContentLoaded", () => {
  const fragtables = document.querySelectorAll("div.fragtable");
  fragtables.forEach(fragtable => {
    if (fragtable instanceof HTMLDivElement && !fragtable.classList.contains('fragtable-rendered')) {
      const table = fragtable.querySelector("table");
      if (table !== null) {
        fragtable.style.columnWidth = `${table.offsetWidth}px`;
        fragtable.classList.add('fragtable-rendered')
      }
    }
  });
});
