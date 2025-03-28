document.addEventListener("DOMContentLoaded", function() {
    const ctx = document.getElementById('incomeExpenseChart').getContext('2d');
    const incomeExpenseChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: window.incomeExpenseData.labels,
        datasets: [
          {
            label: 'Income',
            data: window.incomeExpenseData.incomes,
            backgroundColor: 'rgba(75, 192, 192, 0.5)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
          },
          {
            label: 'Expense',
            data: window.incomeExpenseData.expenses,
            backgroundColor: 'rgba(255, 99, 132, 0.5)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1
          }
        ]
      },
      options: {
        onClick: (evt, elements) => {
          if (elements.length > 0) {
            const datasetIndex = elements[0].datasetIndex;
            const typeFilter = datasetIndex === 0 ? 'income' : 'expense';
            const label = incomeExpenseChart.data.labels[elements[0].index];
            const [year, month] = label.split('-');
            const start_date = `${year}-${month}-01`;
            const lastDay = getLastDay(year, parseInt(month));
            const end_date = `${year}-${month}-${lastDay.toString().padStart(2, '0')}`;
            const baseUrl = window.incomeExpenseData.urlTransactions;
            const url = new URL(window.location.origin + baseUrl);
            url.searchParams.append('time_filter', 'custom');
            url.searchParams.append('start_date', start_date);
            url.searchParams.append('end_date', end_date);
            url.searchParams.append('filter', typeFilter);
            
            const categorySelect = document.getElementById('category');
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
  