/* script.js */
function sortTable(header, columnIndex) {
    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = header.closest('table');
    switching = true;
    dir = "asc";
    while (switching) {
        switching = false;
        rows = table.rows;
        for (i = 1; i < (rows.length - 1); i++) {
            shouldSwitch = false;
            x = rows[i].getElementsByTagName("TD")[columnIndex];
            y = rows[i + 1].getElementsByTagName("TD")[columnIndex];
            var isNumeric = !isNaN(parseFloat(x.innerHTML)) && isFinite(x.innerHTML);
            if (dir === "asc") {
                if ((isNumeric && parseFloat(x.innerHTML) > parseFloat(y.innerHTML)) ||
                    (!isNumeric && x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase())) {
                    shouldSwitch = true;
                    break;
                }
            } else if (dir === "desc") {
                if ((isNumeric && parseFloat(x.innerHTML) < parseFloat(y.innerHTML)) ||
                    (!isNumeric && x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase())) {
                    shouldSwitch = true;
                    break;
                }
            }
        }
        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
            switchcount++;
        } else {
            if (switchcount === 0 && dir === "asc") {
                dir = "desc";
                switching = true;
            }
        }
    }
}
