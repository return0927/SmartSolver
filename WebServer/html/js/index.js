var Doc = window.document;

$(document).ready(function () {
    console.log("Script enabled");

    getQuestions();
    getTodayQuestions();
    getPoint();
    getDayLimit();
    getBooks();
//    getLastestQuestion();
});

function getLastestQuestion() {
    $.get("/api/me/lastest_question", function(response){
        var result = JSON.parse(response);

        if(result.code === "ERR"){
            console.log("ERR on fetching Lastest Question");
        } else {
            setTimeout(function(){$("select#subject").val(result.data.curr);getBooks();}, 100);
            setTimeout(function(){$("select#book_series").val(result.data.bookname);getYears();}, 200);
            setTimeout(function(){$("select#year").val(result.data.year);}, 300);
        }
    });
}

function getBooks() {
    $.get("/api/get_bookseries", function (response) {
        var result = JSON.parse(response);

        if (result.code === "ERR") {
            console.log("Error on Getting BookSeries.");
        } else {
            $("#book_series").empty();
            for (var i = 0; i < result.data.length; i++) {
                $("#book_series").append(new Option(result.data[i], result.data[i]));
            }
        }
        getYears();
    });
}

function getYears() {
    var subject = Doc.getElementById("subject").value;
    var bookseries = Doc.getElementById("book_series").value;

    console.log(subject, bookseries);

    $.post("/api/get_bookinfo", {"subject": subject, "bookseries": bookseries}, function (response) {
        var data = JSON.parse(response);

        if (data.code === "ERR") {
            console.log("Error on Getting Years.");
        } else {
            var select = Doc.getElementById("year");
            select.length = 0;
            var index;


            if (!data.data.length) {
                $("#page").attr("disabled", "disabled");
                $("#q_no").attr("disabled", "disabled");
                $("#submit").attr("disabled", "disabled");
                $("#message").html("지원하지 않는 교재입니다.");
            } else {
                $("#q_no").removeAttr("disabled");
                $("#submit").removeAttr("disabled");
                $("#message").html(data.msg);
            }
            $("#chapter_info").html("페이지(단원)");
            $("#page").val("");
            $("#q_no").val("");

            for (index = 0; index < data.data.length; index++) {
                var elem = Doc.createElement("option");
                elem.value = data.data[index][0];
                elem.innerHTML = data.data[index][0];

                if (!data.data[index][1]) {
                    $("#page").attr("disabled", "disabled");
                } else {
                    $("#page").removeAttr("disabled");
                    switch (data.data[index][1]) {
                        case 1:
                            $("#chapter_info").html("페이지");
                            break;
                        case 2:
                            $("#chapter_info").html("챕터번호");
                            break;
                        case 3:
                            $("#chapter_info").html("단원표기");
                            break;
                    }
                }
                select.add(elem, null);
            }
        }
    });
}

function getPoint() {
    $.get("/api/me/my_point", function (response) {
        var data = JSON.parse(response);

        if (data.code === "ERR") {
            console.log("Error on get My Point.");
        } else {
            Doc.getElementById("now_point").innerHTML = data.data[0] + "p";
        }
    });
}

function submit() {
    var subject = Doc.getElementById("subject").value;
    var bookseries = Doc.getElementById("book_series").value;
    var year = Doc.getElementById("year").value;
    var page = Doc.getElementById("page").value;
    var q_no = Doc.getElementById("q_no").value;

    $.post("/submit", {
        "subject": subject,
        "bookseries": bookseries,
        "year": year,
        "page": page,
        "q_no": q_no
    }, function (response) {
        var data = JSON.parse(response);

        if (data.code === "ERR") { // 오류
            console.log("Error on Submit Question.");
            alert("질문을 등록하는 중에 오류가 발생하였습니다.");
            alert(data.data);
            location.reload();
        } else { // 성공
            alert(data.data); // 결과값 리턴메세지 표시

            page = ''; // 제출 성공 후 제출창 리폼
            q_no = '';

            getQuestions(); // 질문리스트 새로고침
            getTodayQuestions(); // 오늘 질문 새로고침
            getPoint(); // 현재 포인트 새로고침
        }
    });
}

function getQuestions() {
    $.get("/api/me/questions", function (response) {
        var data = JSON.parse(response);

        if (data.code === "ERR") {
            console.log("Error on Get Questions.");
        } else {
            Doc.getElementById("total_questions").innerHTML = data.data.length + "개";
            var table = Doc.getElementById("questions").getElementsByTagName("tbody")[0];
            table.innerHTML = '';
            // table.remove();
            console.log(data.data);
            var n;

            for (n = 0; n < data.data.length; n++) {
                var row = table.insertRow(table.rows.length);
                var date = row.insertCell(0);
                var curr = row.insertCell(1);
                var book = row.insertCell(2);
                var page = row.insertCell(3);
                var number = row.insertCell(4);
                var status = row.insertCell(5);

                date.innerHTML = data.data[n][0];
                curr.innerHTML = data.data[n][1];
                book.innerHTML = data.data[n][2];
                page.innerHTML = data.data[n][3];
                number.innerHTML = data.data[n][4];

                var stat = data.data[n][5];
                if (stat === 0)
                //status.innerHTML = "<p><div class='circle pending'></div>"+data.data[n][6]+"</p>";
                    status.innerHTML = "<div class='status pending'>● " + data.data[n][6] + "</div>";
                else if (stat === 1) {
                    //status.innerHTML = "<p><div class='circle success'></div><a href='"+data.data[n][7]+"'>영상확인</a>"+data.data[n][6]+"</p>";
                    status.innerHTML = "<div class='status success'>● <a href='javascript: window.open(\"" + data.data[n][7] + '", "_blank", "width=1010, height=680, scrollbars=auto, left=150, top=0");location.history(-1);' + "'>영상확인</a> | " + data.data[n][6] + "</div>";
                } else if (stat === 2) {
                    //status.innerHTML = "<p><div class='circle error'></div>"+data.data[n][6]+"</p>";
                    status.innerHTML = "<div class='status error'>● " + data.data[n][6] + "</div>";
                }

            }
        }
    });
}

function getTodayQuestions() {
    $.get("/api/me/questions_today", function (response) {
        var data = JSON.parse(response);

        if (data.code === "ERR") {
            console.log("Error on Get Today Questions.");
        } else {
            Doc.getElementById("today_questions").innerHTML = data.data.length + "개";
        }
    });
}

function getDayLimit() {
    $.get("/api/me/day_rate_limit", function (response) {
        var data = JSON.parse(response);

        if (data.code === "ERR") {
            console.log("Error on Get Day Limit.");
        } else {
            Doc.getElementById("max_questions").innerHTML = data.data + "개/일";
        }
    });
}
