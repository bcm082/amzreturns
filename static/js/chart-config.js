document.addEventListener("DOMContentLoaded", function () {
    const yearColors = {
        '2023': 'darkgreen',
        '2024': 'red',
        '2025': 'blue',
    };

    const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    const datasets = Object.keys(salesGraphData).map(year => {
        return {
            label: year,
            data: salesGraphData[year],
            fill: false,
            borderColor: yearColors[year] || 'gray',
            tension: 0.1,
            pointBackgroundColor: yearColors[year] || 'gray',
        };
    });

    const ctx = document.getElementById('returnsChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets,
        },
        options: {
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `${context.dataset.label}: ${context.raw} returns`;
                        },
                    },
                },
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Months',
                    },
                },
                y: {
                    title: {
                        display: true,
                        text: 'Return Quantity',
                    },
                },
            },
        },
    });

    // Populate the table
    const tableBody = document.getElementById("returnsTableBody");

    Object.keys(salesGraphData).forEach(year => {
        const monthlyData = salesGraphData[year].map(quantity => parseInt(quantity, 10)); // Convert strings to integers
        const total = monthlyData.reduce((sum, value) => sum + value, 0); // Calculate sum of all months


            // Format numbers with commas
        const formattedMonthlyData = monthlyData.map(quantity => quantity.toLocaleString()); // Format each month's data
        const formattedTotal = total.toLocaleString(); // Format the total

        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${year}</td>
            ${formattedMonthlyData.map(quantity => `<td>${quantity}</td>`).join('')}
            <td class="fw-bold">${formattedTotal}</td> <!-- Display total in the last column -->
        `;
        tableBody.appendChild(row);
    });
});