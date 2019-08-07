function SearchAndFilterThingy() {
  var input, filter, table, tr, td, x;
  input = document.getElementById("UserInput");
  filter = input.value.toUpperCase();
  table = document.getElementById("ServicesTable");
  tr = table.getElementsByTagName("tr");

  for (x = 0; x < tr.length; x++) {
    td = tr[x].getElementsByTagName("td")[0];
    if (td) {
      if (td.innerHTML.toUpperCase().indexOf(filter) > -1) {
        tr[x].style.display = "";
      }
      else {
        tr[x].style.display = "none";
      }
    }
  }
}
