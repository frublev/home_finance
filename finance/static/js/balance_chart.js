const ctx = document.getElementById('balanceChart').getContext('2d');

const labels = balancesData.map(item => item.date);
const data = balancesData.map(item => item.balance);

new Chart(ctx, {
    type: 'line',
    data: {
        labels: labels,
        datasets: [{
            label: 'Balance',
            data: data,
            tension: 0.3,
            borderWidth: 2,
            pointRadius: 2,
            fill: true,
            borderColor: data[data.length - 1] < 0 ? '#dc3545' : '#198754',
            backgroundColor: data[data.length - 1] < 0
                ? 'rgba(220,53,69,0.1)'
                : 'rgba(25,135,84,0.1)'
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: {
                callbacks: {
                    label: ctx => ` ${ctx.raw.toLocaleString()}`
                }
            }
        },
        scales: {
            x: {
                grid: { display: false }
            },
            y: {
                ticks: {
                    callback: value => value.toLocaleString()
                }
            }
        }
    }
});

const toggleLink = document.querySelector('[data-bs-target="#balancesTable"]');
const tableBlock = document.getElementById('balancesTable');

tableBlock.addEventListener('show.bs.collapse', () => {
    toggleLink.textContent = 'Hide table';
});

tableBlock.addEventListener('hide.bs.collapse', () => {
    toggleLink.textContent = 'Show table';
});
