var Doc = window.document;

window.onload = onReady();

function onReady() {
    console.log("Script enabled");

    getBooks();
}

function getBooks(self) {
    $.get("/api/get_bookseries", function (response) {
        var data = JSON.parse(response);

        if (data.code === "ERR") {
            console.log("Error on Getting BookSeries.");
        } else {
            var select = Doc.getElementById("book_series");
            select.length = 0;

            for (const index in data.data) {
                var elem = Doc.createElement("option");
                elem.value = data.data[index];
                elem.innerHTML = data.data[index];
                select.add(elem, null);
            }
        }
    });
    setInterval(getYears(null), 5000);
}

function getYears(self) {
    var subject = Doc.getElementById("subject").value;
    var bookseries = Doc.getElementById("book_series").value;

    console.log(subject, bookseries);

    $.post("/api/get_year", {"subject": subject, "bookseries": bookseries}, function (response) {
        var data = JSON.parse(response);

        if (data.code === "ERR") {
            console.log("Error on Getting Years.");
        } else {
            var select = Doc.getElementById("year");
            select.length = 0;

            for (const index in data.data) {
                var elem = Doc.createElement("option");
                elem.value = data.data[index];
                elem.innerHTML = data.data[index];
                select.add(elem, null);
            }
        }
    });
}
