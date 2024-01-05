document.addEventListener('DOMContentLoaded', function () {

    const clickable_tooltips = false
    // ------------------
    // Popovers show/hide
    // ------------------
    if (clickable_tooltips) {
        const buttons = document.querySelectorAll('.popover-button');

        function hide_all_popovers() {
            document.querySelectorAll('.popover').forEach(function (popover) {
                popover.style.display = 'none';
            });
        }

        buttons.forEach(function (button) {
            button.addEventListener('click', function (event) {
                event.stopPropagation();
                let targetId = this.getAttribute('data-popover-target');
                let popover = document.getElementById(targetId);
                // Check if the popover is already visible
                if (popover.style.display === 'block') {
                    popover.style.display = 'none';
                    return;
                }
                hide_all_popovers();
                popover.style.display = popover.style.display === 'block' ? 'none' : 'block';
            });
        });
        document.addEventListener('click', function () {
            hide_all_popovers();
        });
    }
    // -------------------------
    // Searchbar history display
    // -------------------------
    const searchbar = document.getElementById("uid");

    searchbar.addEventListener("keyup", function (event) {
        // check if the key was enter, and stop if it was
        if (event.key === "Enter") {
            // remove focus from searchbar
            searchbar.blur()
            console.log('Detected enter keypress')
            return;
        }
        let searchbar_content = searchbar.value;
        // console.log("Searchbar content: " + searchbar_content)
        generateTable(searchbar_content)
    });

    const searchbar_history_display = document.getElementById("searchbar_history_display");
    searchbar.addEventListener("focus", function () {
        generateTable()
        searchbar_history_display.style.display = "block";
    });
    searchbar.addEventListener("blur", function () {
        if (searchbar_history_display.querySelector(":hover") == null) {
            searchbar_history_display.style.display = 'none';
        }
    });
    // ------------------------
    // Search history load/save
    // ------------------------

    // --------------
    // Generate table
    // --------------

    
});
// ------------------------
// Functions called by HTML
// ------------------------

const max_elements_to_display = 5
function generateTable(must_contain = "") {
    stringList = load_search_history()
    // Create a table element
    let table = document.createElement('table');
    table.className = 'table-fixed w-full' // border border-1';
    //table.style.borderColor = 'rgba(255, 255, 255, 0.8)';
    // Iterate over the stringList and create a row for each string
    let rows = 0
    for (let i = 0; i < stringList.length && rows < max_elements_to_display; i++) {
        // console.log("Checking " + stringList[i])
        if (must_contain !== "" && !stringList[i].includes(must_contain)) {
            // console.log("Skipping " + stringList[i])
            continue
        }
        // console.log("Adding " + stringList[i])
        let row = table.insertRow(rows);
        row.className = 'hover:bg-gray-200';
        let cell = row.insertCell(0);
        cell.setAttribute('class', 'w-5/6')
        let link = document.createElement('a');
        link.setAttribute('onclick', `hide_searchbar_history('${stringList[i]}')`);
        let paragraph = document.createElement('p');
        paragraph.className = 'p-2 cursor-pointer';
        paragraph.style.display = 'block';
        paragraph.textContent = stringList[i];
        link.appendChild(paragraph);
        cell.appendChild(link);
        let deletebuttoncell = row.insertCell(1);
        deletebuttoncell.setAttribute('class', 'w-1/6 text-right font-light')
        let deletebuttonparagraph = document.createElement('p');
        deletebuttonparagraph.className = 'p-2 cursor-pointer';
        deletebuttonparagraph.style.display = 'block';
        deletebuttonparagraph.textContent = 'X';
        deletebuttonparagraph.setAttribute('onclick', `delete_from_search_history('${stringList[i]}')`);
        deletebuttoncell.appendChild(deletebuttonparagraph);

        // TODO: implement this
        // cell.appendChild(deletebuttonparagraph);

        rows++;
    }
    // Append the table to the body or any other container element
    let tableContainer = document.getElementById('searchbar_history_display');
    tableContainer.innerHTML = '';
    tableContainer.appendChild(table);
}

function load_search_history() {
    let history = JSON.parse(localStorage.getItem('search_history')) || []
    history.reverse()
    return history
}

function search() {
    function unique(value, index, array) {
        return array.indexOf(value) === index;
    }
    function save_to_search_history(query) {
        if (query >= 100000000 && query <= 999999999) {
            // console.log("Saving " + query + " to search history.")
            let search_history = JSON.parse(localStorage.getItem('search_history')) || [];
            if (search_history.includes(query)) {
                let index = search_history.indexOf(query)
                search_history.splice(index, 1)
            }
            search_history.push(query); // add the new query to the beginning of the array
            // search_history = search_history.filter(unique)
            localStorage.setItem('search_history', JSON.stringify(search_history));
        }
    }
    const query = document.getElementById("uid").value
    if (query !== "") {
        save_to_search_history(query);
        const uid = document.getElementById("uid").value;
        window.location.href = "/uid/" + uid;
    }
}

function hide_searchbar_history(uid) {
    // console.log("Clicked on " + uid)
    const searchbar_history_display = document.getElementById("searchbar_history_display");
    searchbar_history_display.style.display = 'none';
    const searchbar = document.getElementById("uid");
    searchbar.value = uid;
    search()
}

function sortTable(n) {
    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementById("mytable");
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
            x = rows[i].getElementsByTagName("td")[n];
            y = rows[i + 1].getElementsByTagName("td")[n];
            /* Check if the two rows should switch place,
            based on the direction, asc or desc: */
            if (dir == "asc") {
                if (parseFloat(x.innerHTML.toLowerCase()) > parseFloat(y.innerHTML.toLowerCase())) {
                    // If so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                }
            } else if (dir == "desc") {
                if (parseFloat(x.innerHTML.toLowerCase()) < parseFloat(y.innerHTML.toLowerCase())) {
                    // If so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                }
            }
        }
        if (shouldSwitch) {
            /* If a switch has been marked, make the switch
            and mark that a switch has been done: */
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
            // Each time a switch is done, increase this count by 1:
            switchcount++;
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

function delete_from_search_history(query) {
    document.getElementById("uid").focus()
    console.log("Deleting " + query + " from search history.")
    let search_history = JSON.parse(localStorage.getItem('search_history')) || [];
    if (search_history.includes(query)) {
        let index = search_history.indexOf(query)
        search_history.splice(index, 1)
    }
    localStorage.setItem('search_history', JSON.stringify(search_history));
    const stringList = load_search_history();
    generateTable(stringList);
    console.log("Displaying again the search history.")
}

function toggleRows(rowId) {
    let row_simple = document.getElementById(rowId + "_simple");
    console.log(rowId + "_simple")
    let row_detailed = document.getElementById(rowId + "_detailed");
    if (row_simple.style.display === 'none') {
        row_simple.style.display = '';
    } else {
        row_simple.style.display = 'none';
    }
    if (row_detailed.style.display === 'none') {
        row_detailed.style.display = '';
    } else {
        row_detailed.style.display = 'none';
    }
}