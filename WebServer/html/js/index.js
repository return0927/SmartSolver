var Doc = window.document;

window.onload = onReady();

function onReady() {
    console.log("Script enabled");

    getQuestions();
    getTodayQuestions();
    getPoint();
    getDayLimit();
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
            var index;

            for (index=0; index<data.data.length; index++) {
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
            var index;

            for (index=0; index<data.data.length; index++) {
                var elem = Doc.createElement("option");
                elem.value = data.data[index];
                elem.innerHTML = data.data[index];
                select.add(elem, null);
            }
        }
    });
}

function getMessage() {
    var subject = Doc.getElementById("subject").value;
    var bookseries = Doc.getElementById("book_series").value;
    var year = Doc.getElementById("year").value;

    $.get("/api/get_message", , function(response){
       var data = JSON.parse(response);

       if (data.code === "ERR") {
           console.log("Error on get My Point.");
       } else {
           Doc.getElementById("now_point").innerHTML = data.data[0]+"p";
       }
    });
}

function getPoint() {
    $.get("/api/me/my_point", function(response){
       var data = JSON.parse(response);

       if (data.code === "ERR") {
           console.log("Error on get My Point.");
       } else {
           Doc.getElementById("now_point").innerHTML = data.data[0]+"p";
       }
    });
}

function submit() {
    var subject = Doc.getElementById("subject").value;
    var bookseries = Doc.getElementById("book_series").value;
    var year = Doc.getElementById("year").value;
    var page = Doc.getElementById("page").value;
    var q_no = Doc.getElementById("q_no").value;

    $.post("/submit", {"subject": subject, "bookseries": bookseries, "year": year, "page": page, "q_no": q_no}, function(response){
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

function getQuestions(){
    $.get("/api/me/questions", function(response){
        var data = JSON.parse(response);

       if (data.code === "ERR") {
           console.log("Error on Get Questions.");
       } else {
           Doc.getElementById("total_questions").innerHTML = data.data.length +"개";
           var table = Doc.getElementById("questions").getElementsByTagName("tbody")[0];
           table.innerHTML = '';
           // table.remove();
           console.log(data.data);
            var n;

            for (n=0; n<data.data.length; n++) {
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
               if(stat === 0)
                   //status.innerHTML = "<p><div class='circle pending'></div>"+data.data[n][6]+"</p>";
                   status.innerHTML = "<div class='status pending'>● "+data.data[n][6]+"</div>";
               else if(stat === 1) {
                   //status.innerHTML = "<p><div class='circle success'></div><a href='"+data.data[n][7]+"'>영상확인</a>"+data.data[n][6]+"</p>";
                   status.innerHTML = "<div class='status success'>● <a target='_blank' href='"+data.data[n][7]+"'>영상확인</a> | "+data.data[n][6]+"</div>";
               } else if(stat === 2) {
                   //status.innerHTML = "<p><div class='circle error'></div>"+data.data[n][6]+"</p>";
                   status.innerHTML = "<div class='status error'>● "+data.data[n][6]+"</div>";
               }

           }
       }
    });
}

function getTodayQuestions(){
    $.get("/api/me/questions_today", function(response){
        var data = JSON.parse(response);

       if (data.code === "ERR") {
           console.log("Error on Get Today Questions.");
       } else {
           Doc.getElementById("today_questions").innerHTML = data.data.length +"개";
       }
    });
}

function getDayLimit() {
    $.get("/api/me/day_rate_limit", function(response){
        var data = JSON.parse(response);

       if (data.code === "ERR") {
           console.log("Error on Get Day Limit.");
       } else {
           Doc.getElementById("max_questions").innerHTML = data.data +"개/일";
       }
    });
}