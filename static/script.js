/* script.js */
// Add JavaScript to handle collapsible sections
var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
    coll[i].addEventListener("click", function() {
        this.classList.toggle("active");
        var content = this.nextElementSibling;
        if (content.style.display === "block") {
            content.style.display = "none";
        } else {
            content.style.display = "block";
        }
    });
}

// // Function to sort table columns
// function sortTable(columnIndex) {
//     var table, rows, switching, i, x, y, shouldSwitch;
//     table = document.getElementById("connectionsTable");
//     switching = true;

//     while (switching) {
//         switching = false;
//         rows = table.getElementsByTagName("tr");

//         for (i = 1; i < (rows.length - 1); i++) {
//             shouldSwitch = false;
//             x = rows[i].getElementsByTagName("td")[columnIndex];
//             y = rows[i + 1].getElementsByTagName("td")[columnIndex];

//             // Check if the column contains numbers and convert them for proper sorting
//             if (!isNaN(x.innerHTML) && !isNaN(y.innerHTML)) {
//                 shouldSwitch = parseFloat(x.innerHTML) > parseFloat(y.innerHTML);
//             } else {
//                 shouldSwitch = x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase();
//             }

//             if (shouldSwitch) {
//                 rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
//                 switching = true;
//             }
//         }
//     }
// }
