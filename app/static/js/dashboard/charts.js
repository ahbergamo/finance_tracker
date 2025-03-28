document.addEventListener("DOMContentLoaded", function() {
    const currentYear = window.dashboardData.currentYear;
    const monthLabels = window.monthLabels; // Provided by server
  
    // --- Combined Monthly Income & Expenses Chart ---
    const monthlyCombinedCtx = document.getElementById('monthlyCombinedChart').getContext('2d');
    new Chart(monthlyCombinedCtx, {
      type: 'bar',
      data: {
        labels: monthLabels,
        datasets: [
          {
            label: 'Income',
            data: window.dashboardData.monthlyIncome,
            backgroundColor: 'rgba(75, 192, 192, 0.5)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
          },
          {
            label: 'Expenses',
            data: window.dashboardData.monthlyExpenses,
            backgroundColor: 'rgba(255, 99, 132, 0.5)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1
          }
        ]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } },
        onClick: (evt, elements) => {
          if (elements.length > 0) {
            const element = elements[0];
            const index = element.index;
            const datasetIndex = element.datasetIndex;
            const firstMonthStart = new Date(window.dashboardData.pieStartDate);
            const monthStart = new Date(firstMonthStart.getFullYear(), firstMonthStart.getMonth() + index + 1, 1);
            const monthEnd = new Date(monthStart.getFullYear(), monthStart.getMonth() + 1, 0);
  
            const formatDate = (d) => {
              const month = (d.getMonth() + 1).toString().padStart(2, '0');
              const day = d.getDate().toString().padStart(2, '0');
              return `${d.getFullYear()}-${month}-${day}`;
            };
  
            const start_date = formatDate(monthStart);
            const end_date = formatDate(monthEnd);
            const url = new URL(window.transactionsUrl, window.location.origin);
            url.searchParams.append('time_filter', 'custom');
            url.searchParams.append('start_date', start_date);
            url.searchParams.append('end_date', end_date);
            url.searchParams.append('filter', datasetIndex === 0 ? 'income' : 'expense');
            window.location.href = url;
          }
        }
      }
    });
  
    // --- Monthly Net Chart (Line Chart) ---
    const netData = window.dashboardData.monthlyIncome.map((inc, i) => inc - window.dashboardData.monthlyExpenses[i]);
    const monthlyNetCtx = document.getElementById('monthlyNetChart').getContext('2d');
    const monthlyNetChart = new Chart(monthlyNetCtx, {
      type: 'line',
      data: {
        labels: monthLabels,
        datasets: [{
          label: 'Net',
          data: netData,
          fill: false,
          borderColor: 'rgba(153, 102, 255, 1)',
          tension: 0.1,
          pointRadius: 5,
          pointHoverRadius: 7
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: false } },
        onClick: (evt) => {
          const points = monthlyNetChart.getElementsAtEventForMode(evt, 'nearest', { intersect: true }, true);
          if (points.length > 0) {
            const point = points[0];
            const index = point.index;
            const firstMonthStart = new Date(window.dashboardData.pieStartDate);
            const monthStart = new Date(firstMonthStart.getFullYear(), firstMonthStart.getMonth() + index, 1);
            const monthEnd = new Date(monthStart.getFullYear(), monthStart.getMonth() + 1, 0);
            const formatDate = (d) => {
              const month = (d.getMonth() + 1).toString().padStart(2, '0');
              const day = d.getDate().toString().padStart(2, '0');
              return `${d.getFullYear()}-${month}-${day}`;
            };
            const start_date = formatDate(monthStart);
            const end_date = formatDate(monthEnd);
            const url = new URL(window.transactionsUrl, window.location.origin);
            url.searchParams.append('time_filter', 'custom');
            url.searchParams.append('start_date', start_date);
            url.searchParams.append('end_date', end_date);
            window.location.href = url;
          }
        }
      }
    });
  
    // --- Expense Categories Chart (Pie Chart) ---
    window.dashboardData.expenseCategoriesLabels = window.dashboardData.expenseCategoriesLabels.map(label => {
      const maxLength = 10;
      return label.length > maxLength ? label.substring(0, maxLength) + '...' : label;
    });
    const expenseCategoriesCtx = document.getElementById('expenseCategoriesChart').getContext('2d');
    new Chart(expenseCategoriesCtx, {
      type: 'pie',
      data: {
        labels: window.dashboardData.expenseCategoriesLabels,
        datasets: [{
          label: 'Expenses',
          data: window.dashboardData.expenseCategoriesData,
          // backgroundColor: [
          //     'rgba(255, 99, 132, 0.6)',
          //     'rgba(54, 162, 235, 0.6)',
          //     'rgba(255, 206, 86, 0.6)',
          //     'rgba(75, 192, 192, 0.6)',
          //     'rgba(153, 102, 255, 0.6)',
          //     'rgba(201, 203, 207, 0.6)',
          //     'rgba(100, 149, 237, 0.6)',
          //     'rgba(160, 82, 45, 0.6)' // in case "Rest" exists, extra color available
          // ],
          // borderColor: [
          //     'rgba(255, 99, 132, 1)',
          //     'rgba(54, 162, 235, 1)',
          //     'rgba(255, 206, 86, 1)',
          //     'rgba(75, 192, 192, 1)',
          //     'rgba(153, 102, 255, 1)',
          //     'rgba(201, 203, 207, 1)',
          //     'rgba(100, 149, 237, 1)',
          //     'rgba(160, 82, 45, 1)'
          // ],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'left', labels: { font: { size: 16 } } }
        },
        onClick: (evt, elements) => {
          if (elements.length > 0) {
            const index = elements[0].index;
            let selectedParam;
            if (window.dashboardData.expenseCategoriesIds[index] === 0) {
              selectedParam = window.dashboardData.expenseCategoriesRestIds.join(',');
            } else {
              selectedParam = window.dashboardData.expenseCategoriesIds[index].toString();
            }
            const url = new URL(window.transactionsUrl, window.location.origin);
            url.searchParams.append('filter', 'expense');
            if (selectedParam.indexOf(',') !== -1) {
              url.searchParams.append('category_ids', selectedParam);
            } else {
              url.searchParams.append('category_id', selectedParam);
            }
            url.searchParams.append('time_filter', 'custom');
            url.searchParams.append('start_date', window.dashboardData.pieStartDate);
            url.searchParams.append('end_date', window.dashboardData.pieEndDate);
            window.location.href = url;
          }
        }
      }
    });
  
    // --- Income Categories Chart (Doughnut Chart) ---
    window.dashboardData.incomeCategoriesLabels = window.dashboardData.incomeCategoriesLabels.map(label => {
      const maxLength = 10;
      return label.length > maxLength ? label.substring(0, maxLength) + '...' : label;
    });
    const incomeCategoriesCtx = document.getElementById('incomeCategoriesChart').getContext('2d');
    new Chart(incomeCategoriesCtx, {
      type: 'doughnut',
      data: {
        labels: window.dashboardData.incomeCategoriesLabels,
        datasets: [{
          label: 'Income',
          data: window.dashboardData.incomeCategoriesData,
          // backgroundColor: [
          //     'rgba(75, 192, 192, 0.6)',
          //     'rgba(255, 159, 64, 0.6)',
          //     'rgba(255, 205, 86, 0.6)',
          //     'rgba(201, 203, 207, 0.6)',
          //     'rgba(54, 162, 235, 0.6)',
          //     'rgba(100, 149, 237, 0.6)',
          //     'rgba(160, 82, 45, 0.6)',
          //     'rgba(220,20,60, 0.6)' // extra color for "Rest" if needed
          // ],
          // borderColor: [
          //     'rgba(75, 192, 192, 1)',
          //     'rgba(255, 159, 64, 1)',
          //     'rgba(255, 205, 86, 1)',
          //     'rgba(201, 203, 207, 1)',
          //     'rgba(54, 162, 235, 1)',
          //     'rgba(100, 149, 237, 1)',
          //     'rgba(160, 82, 45, 1)',
          //     'rgba(220,20,60, 1)'
          // ],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'left', labels: { font: { size: 16 } } }
        },
        onClick: (evt, elements) => {
          if (elements.length > 0) {
            const index = elements[0].index;
            let selectedParam;
            if (window.dashboardData.incomeCategoriesIds[index] === 0) {
              selectedParam = window.dashboardData.incomeCategoriesRestIds.join(',');
            } else {
              selectedParam = window.dashboardData.incomeCategoriesIds[index].toString();
            }
            const url = new URL(window.transactionsUrl, window.location.origin);
            url.searchParams.append('filter', 'income');
            if (selectedParam.indexOf(',') !== -1) {
              url.searchParams.append('category_ids', selectedParam);
            } else {
              url.searchParams.append('category_id', selectedParam);
            }
            url.searchParams.append('time_filter', 'custom');
            url.searchParams.append('start_date', window.dashboardData.pieStartDate);
            url.searchParams.append('end_date', window.dashboardData.pieEndDate);
            window.location.href = url;
          }
        }
      }
    });
  
    // --- Cash Flow Overview Chart (Line Chart) ---
    const cashFlowCtx = document.getElementById('cashFlowChart').getContext('2d');
    const cashFlowChart = new Chart(cashFlowCtx, {
      type: 'line',
      data: {
        labels: window.dashboardData.cashFlowDates,
        datasets: [{
          label: 'Cumulative Balance',
          data: window.dashboardData.cashFlowData,
          fill: false,
          borderColor: 'rgba(255, 206, 86, 1)',
          tension: 0.1,
          pointRadius: 5,
          pointHoverRadius: 7
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: false } },
        onClick: (evt) => {
          // Use the chart instance's method:
          const points = cashFlowChart.getElementsAtEventForMode(evt, 'nearest', { intersect: true }, true);
          if (points.length > 0) {
            const point = points[0];
            const index = point.index;
            const clickedDateStr = window.dashboardData.cashFlowDates[index];
            const clickedDate = new Date(clickedDateStr);
            const monthStart = new Date(clickedDate.getFullYear(), clickedDate.getMonth(), 1);
            const formatDate = (d) => {
              const month = (d.getMonth() + 1).toString().padStart(2, '0');
              const day = d.getDate().toString().padStart(2, '0');
              return `${d.getFullYear()}-${month}-${day}`;
            };
            const start_date = formatDate(monthStart);
            const end_date = formatDate(clickedDate);
            const url = new URL(window.transactionsUrl, window.location.origin);
            url.searchParams.append('time_filter', 'custom');
            url.searchParams.append('start_date', start_date);
            url.searchParams.append('end_date', end_date);
            window.location.href = url;
          }
        }
      }
    });
    
  });
  