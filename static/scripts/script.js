document.addEventListener('DOMContentLoaded', function () {
  // Filter button logic
  var buttons = document.querySelectorAll('.filter-btn');
  var active = window.activeFilter || {};

  buttons.forEach(function (btn) {
    var number = btn.getAttribute('data-number');
    var unit = btn.getAttribute('data-unit');

    if (number === active.number && unit === active.unit) {
      btn.classList.add('active');
    }

    btn.addEventListener('click', function () {
      window.location.href = window.location.pathname + '?number=' + number + '&unit=' + unit;
    });
  });

  // Chart.js initialization
  var canvas = document.getElementById('speedChart');
  if (!canvas || !window.speedtestData || !window.speedtestData.data.length) return;

  var raw = window.speedtestData.data;
  function parseTS(ts) {
    // Ensure UTC if no timezone info present
    if (!ts.endsWith('Z') && !ts.includes('+')) ts += 'Z';
    return new Date(ts);
  }
  var downloads = raw.map(function (d) { return { x: parseTS(d.timestamp), y: d.download }; });
  var uploads = raw.map(function (d) { return { x: parseTS(d.timestamp), y: d.upload }; });
  var pings = raw.map(function (d) { return { x: parseTS(d.timestamp), y: d.ping }; });

  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var uploadColor = style.getPropertyValue('--upload-color').trim();
  var pingColor = style.getPropertyValue('--ping-color').trim();

  new Chart(canvas, {
    type: 'line',
    data: {
      datasets: [
        {
          label: 'Download (Mbps)',
          data: downloads,
          borderColor: accent,
          backgroundColor: accent + '1a',
          borderWidth: 2,
          pointRadius: 2,
          pointHoverRadius: 4,
          tension: 0.3,
          fill: false,
          yAxisID: 'y',
        },
        {
          label: 'Upload (Mbps)',
          data: uploads,
          borderColor: uploadColor,
          backgroundColor: uploadColor + '1a',
          borderWidth: 2,
          pointRadius: 2,
          pointHoverRadius: 4,
          tension: 0.3,
          fill: false,
          yAxisID: 'y',
        },
        {
          label: 'Ping (ms)',
          data: pings,
          borderColor: pingColor,
          backgroundColor: pingColor + '1a',
          borderWidth: 2,
          borderDash: [5, 3],
          pointRadius: 2,
          pointHoverRadius: 4,
          tension: 0.3,
          fill: false,
          yAxisID: 'y1',
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      plugins: {
        legend: {
          position: 'top',
          labels: {
            usePointStyle: true,
            padding: 16,
            font: { family: 'Inter', size: 12 },
          },
        },
        tooltip: {
          backgroundColor: '#111827',
          titleFont: { family: 'Inter', size: 12 },
          bodyFont: { family: 'Inter', size: 12 },
          padding: 10,
          cornerRadius: 8,
        },
      },
      scales: {
        x: {
          type: 'time',
          time: {
            tooltipFormat: 'MMM d, yyyy  HH:mm',
            displayFormats: {
              minute: 'HH:mm',
              hour: 'ha',
              day: 'MMM d',
              week: 'MMM d',
              month: 'MMM yyyy',
            },
          },
          grid: { display: false },
          ticks: {
            font: { family: 'Inter', size: 11 },
            color: '#6b7280',
            maxTicksLimit: 12,
          },
        },
        y: {
          position: 'left',
          title: { display: true, text: 'Mbps', font: { family: 'Inter', size: 12 }, color: '#6b7280' },
          grid: { color: '#e5e7eb' },
          ticks: { font: { family: 'Inter', size: 11 }, color: '#6b7280' },
        },
        y1: {
          position: 'right',
          title: { display: true, text: 'Ping (ms)', font: { family: 'Inter', size: 12 }, color: '#6b7280' },
          grid: { drawOnChartArea: false },
          ticks: { font: { family: 'Inter', size: 11 }, color: '#6b7280' },
        },
      },
    },
  });
});
