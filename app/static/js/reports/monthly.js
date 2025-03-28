document.addEventListener("DOMContentLoaded", function() {
    const ctx = document.getElementById('monthlySpendingChart').getContext('2d');
    const monthlySpendingChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: window.monthlyChartData.labels,
        datasets: [{
          label: 'Total Spending',
          data: window.monthlyChartData.totals,
          backgroundColor: 'rgba(255, 159, 64, 0.5)',
          borderColor: 'rgba(255, 159, 64, 1)',
          borderWidth: 1
        }]
      },
      options: {
        onClick: (evt, elements) => {
          if (elements.length > 0) {
            const index = elements[0].index;
            const label = monthlySpendingChart.data.labels[index];
            const [yearMonth] = label.split(" ");
            const [year, month] = yearMonth.split("-");
            const start_date = `${year}-${month}-01`;
            const lastDay = getLastDay(year, parseInt(month));
            const end_date = `${year}-${month}-${lastDay.toString().padStart(2, '0')}`;
            const baseUrl = window.monthlyChartData.urlTransactions;
            const url = new URL(window.location.origin + baseUrl);
            url.searchParams.append('time_filter', 'custom');
            url.searchParams.append('start_date', start_date);
            url.searchParams.append('end_date', end_date);
            url.searchParams.append('filter', 'expense');
            
            const categorySelect = document.getElementById('category_id');
            if (categorySelect && categorySelect.value) {
              url.searchParams.append('category_id', categorySelect.value);
            }
            const accountSelect = document.getElementById('account_id');
            if (accountSelect && accountSelect.value) {
              url.searchParams.append('account_id', accountSelect.value);
            }
            
            window.location.href = url;
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: function(value) {
                return '$' + value.toLocaleString();
              }
            }
          }
        }
      }
    });
  });
  