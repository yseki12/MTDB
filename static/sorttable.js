function sortTable(n) {
  var table, vartype, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
  table = document.getElementById("indexTable");
  switching = true;
  // Set the sorting direction to ascending:
  dir = "asc"; 
  /* Make a loop that will continue until
  no switching has been done: */
  while (switching) {
    // Start by saying: no switching is done:
    switching = false;
    rows = table.rows;
    /* Loop through all table rows (except the
    first, which contains table headers): */
    for (i = 1; i < (rows.length - 1); i++) {
      // Start by saying there should be no switching:
      shouldSwitch = false;
      /* Get the two elements you want to compare,
      one from current row and one from the next: */
      x = rows[i].getElementsByTagName("TD")[n];
      y = rows[i + 1].getElementsByTagName("TD")[n];

      if (isNaN(x.textContent) == false){
          vartype = "number";
      }
      else {
          vartype = "string";
      }
      /* Check if the two rows should switch place,
      based on the direction, asc or desc: */
      if (vartype == "string") {

        if (dir == "asc") {
            if (x.textContent.toLowerCase() > y.textContent.toLowerCase()) {
                // If so, mark as a switch and break the loop:
                shouldSwitch = true;
                break;
            }
        } 
        else if (dir == "desc") {
            if (x.textContent.toLowerCase() < y.textContent.toLowerCase()) {
                // If so, mark as a switch and break the loop:
                shouldSwitch = true;
                break;
            }
        }
      }
        else if (vartype == "number") {

            if (dir == "asc") {
                if (Number(x.textContent) > Number(y.textContent)) {
                    // If so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                }
            }
            else if (dir == "desc") {
                if (Number(x.textContent) < Number(y.textContent)) {
                    // If so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                }
            }
        }

    }
    if (shouldSwitch) {
      /* If a switch has been marked, make the switch
      and mark that a switch has been done: */
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      // Each time a switch is done, increase this count by 1:
      switchcount ++; 
    } else {
      /* If no switching has been done AND the direction is "asc",
      set the direction to "desc" and run the while loop again. */
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
}

function sortImage(object) {

  var object_id = object.id;
  var object_header = document.getElementById(object_id);
  var object_span = object_header.getElementsByTagName('span')[0].innerHTML;
  var presort = '<i class="fas fa-sort"></i>';
  var sortup = '<i class="fas fa-sort-up"></i>';
  var sortdown = '<i class="fas fa-sort-down"></i>';

  if (object_span === presort) {
    document.getElementById(object.id).getElementsByTagName('span')[0].innerHTML = sortup;
  }
  else if (object_span === sortup) {
    document.getElementById(object.id).getElementsByTagName('span')[0].innerHTML = sortdown;
  }
  else if (object_span === sortdown) {
    document.getElementById(object.id).getElementsByTagName('span')[0].innerHTML = sortup;
  }
}