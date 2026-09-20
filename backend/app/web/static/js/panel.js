document.addEventListener("DOMContentLoaded", () => {
  const lienzo = document.querySelector("#grafico-incidentes");
  if (!lienzo || typeof Chart === "undefined") return;

  new Chart(lienzo, {
    type: "line",
    data: {
      labels: ["00", "04", "08", "12", "16", "20"],
      datasets: [{
        label: "Incidentes",
        data: [0, 0, 0, 0, 0, 0],
        borderColor: "#63e6be",
        backgroundColor: "rgba(99, 230, 190, .12)",
        fill: true,
        tension: .35,
      }],
    },
    options: {
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: "rgba(159, 176, 192, .08)" }, ticks: { color: "#9fb0c0" } },
        y: { beginAtZero: true, grid: { color: "rgba(159, 176, 192, .08)" }, ticks: { color: "#9fb0c0", precision: 0 } },
      },
    },
  });
});
