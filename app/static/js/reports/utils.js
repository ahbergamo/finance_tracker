/**
 * Returns the last day of the given month.
 * @param {string|number} year - The year.
 * @param {number} month - The month (1-indexed).
 * @returns {number} The last day of the month.
 */
function getLastDay(year, month) {
    return new Date(year, month, 0).getDate();
  }
  