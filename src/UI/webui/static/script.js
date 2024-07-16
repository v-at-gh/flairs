/* script.js */
document.addEventListener('DOMContentLoaded', function () {
    var header = document.querySelector('.sticky-header');

    window.onscroll = function () {
        if (window.pageYOffset > 100) { // Adjust the value based on when you want the header to become sticky
            header.classList.add('sticky');
        } else {
            header.classList.remove('sticky');
        }
    };
});

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

            // Check if the column is for IP addresses
            var isIPAddress = isIPAddressColumn(header, columnIndex);

            if (dir === "asc") {
                if ((isNumeric && parseFloat(x.innerHTML) > parseFloat(y.innerHTML)) ||
                    (!isNumeric && !isIPAddress && x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) ||
                    (!isNumeric && isIPAddress && compareIPAddresses(x.innerHTML, y.innerHTML) > 0)) {
                    shouldSwitch = true;
                    break;
                }
            } else if (dir === "desc") {
                if ((isNumeric && parseFloat(x.innerHTML) < parseFloat(y.innerHTML)) ||
                    (!isNumeric && !isIPAddress && x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) ||
                    (!isNumeric && isIPAddress && compareIPAddresses(x.innerHTML, y.innerHTML) < 0)) {
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

// TODO: for some reason cannot make it work. Think out the other way.
// Function to check if the column is for IP addresses
function isIPAddressColumn(header, columnIndex) {
    if (header && header.getElementsByTagName("TH")[columnIndex]) {
        // var columnName = header.getElementsByTagName("TH")[columnIndex].innerText;
        // var columnName = header.getElementsByTagName("TH")[columnIndex].textContent;
        var columnName = header.getElementsByTagName("TH")[columnIndex].innerHTML;
        return columnName === "Local Address" || columnName === "Remote Address";
    }
    return false;
}

// Function to compare IP addresses
function compareIPAddresses(ip1, ip2) {
    var parts1 = ip1.split(".");
    var parts2 = ip2.split(".");
    for (var i = 0; i < 4; i++) {
        var num1 = parseInt(parts1[i], 10);
        var num2 = parseInt(parts2[i], 10);
        if (num1 < num2) {
            return -1;
        } else if (num1 > num2) {
            return 1;
        }
    }
    return 0;
}
