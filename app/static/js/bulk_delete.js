document.addEventListener('DOMContentLoaded', function() {
    const selectAllCheckbox = document.getElementById('select_all');
    if (selectAllCheckbox) {
      selectAllCheckbox.addEventListener('click', function() {
        const checkboxes = document.querySelectorAll('input[name="transaction_ids"]');
        checkboxes.forEach(cb => cb.checked = selectAllCheckbox.checked);
      });
    }
  });
  