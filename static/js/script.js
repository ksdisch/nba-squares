// Note: This is just an example. You will need to modify this code to fit your needs.
//      You will also need to add this script to your HTML page.
//      See https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch for more info on using fetch()
function updateGrid(year, stat, value, positions, comparison) {
    // Generate the URL dynamically
    const url = `http://localhost:5000/api/v1/players?date=${year}&stat=${stat}&value=${value}&positions=${positions.join(',')}&comparison=${comparison}`;
  
    // Fetch data from your Flask API
    fetch(url)
      .then(response => response.json())
      .then(data => {
        // Now that you have your data, you can use it to update your grid
        data.forEach((item, index) => {
          // Assume you have a div with id 'grid' to hold your grid cells
          const grid = document.getElementById('grid');
  
          // Create a new div for this grid cell
          const cell = document.createElement('div');
          cell.textContent = item.someProperty;  // Replace 'someProperty' with the actual property name you want to display
  
          // Add the new cell to the grid
          grid.appendChild(cell);
        });
      })
      .catch(error => {
        console.error('Error:', error);
      });
  }
  