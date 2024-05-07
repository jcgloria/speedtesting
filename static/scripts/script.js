document.addEventListener('DOMContentLoaded', function() {
  const buttons = document.querySelectorAll('.time-button');
  
  // Get query parameters
  const queryParams = new URLSearchParams(window.location.search);
  const selectedNumber = queryParams.get('number');
  const selectedUnit = queryParams.get('unit');
  
  buttons.forEach(button => {
    const number = button.getAttribute('data-number');
    const unit = button.getAttribute('data-unit');
    
    // Check if the button corresponds to the selected number and unit
    if (number === selectedNumber && unit === selectedUnit) {
      button.classList.add('active');
    }
    
    button.addEventListener('click', function() {
      // Construct the query string
      const queryString = `?number=${number}&unit=${unit}`;
      
      // Redirect to the same page with the query string
      window.location.href = window.location.pathname + queryString;
    });
  });
});
