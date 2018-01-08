$(document).ready(function(){
    getQuestions();
    getVideos();
});

var Doc = document;

function getQuestions(){
    var count = Doc.getElementById("count").value;

    $.get("/panel/api/questions?c="+count, function(response){
        var data = JSON.parse(response);

       if (data.code === "ERR") {
           console.log("Error on Get Questions.");
       } else {
           var table = Doc.getElementById("questions").getElementsByTagName("tbody")[0];
           table.innerHTML = '';
           console.log(data.data);
           for(const n in data.data) {
               var row = table.insertRow(table.rows.length);
               // 처리번호(qid)	문제번호(pid) 등록자(sid)	등록일시(date+time)	과목(curr)	교재(bookname+year)	페이지(page)	번호(number)	상태(status) 메세지(message)
               var pid = row.insertCell(0);
               var qid = row.insertCell(1);
               var sid = row.insertCell(2);
               var time = row.insertCell(3);
               var curr = row.insertCell(4);
               var book = row.insertCell(5);
               var page = row.insertCell(6);
               var number = row.insertCell(7);
               var status = row.insertCell(8);
               var message = row.insertCell(9);

               pid.innerHTML = data.data[n][0];
               qid.innerHTML = data.data[n][1];
               sid.innerHTML = data.data[n][2];
               time.innerHTML = data.data[n][3];
               curr.innerHTML = data.data[n][4];
               book.innerHTML = data.data[n][5];
               page.innerHTML = data.data[n][6];
               number.innerHTML = data.data[n][7];
               message.innerHTML = data.data[n][9];

               var stat = data.data[n][8];
               if(stat === 0)
                   //status.innerHTML = "<p><div class='circle pending'></div>"+data.data[n][6]+"</p>";
                   status.innerHTML = "<div class='status pending'>●</div>";
               else if(stat === 1) {
                   //status.innerHTML = "<p><div class='circle success'></div><a href='"+data.data[n][7]+"'>영상확인</a>"+data.data[n][6]+"</p>";
                   status.innerHTML = "<div class='status success'>●</div>";
               } else if(stat === 2) {
                   //status.innerHTML = "<p><div class='circle error'></div>"+data.data[n][6]+"</p>";
                   status.innerHTML = "<div class='status error'>●</div>";
               }

           }
       }
    });
}

function getVideos(){
    $.get("/panel/api/videos?c=", function(response){
        var data = JSON.parse(response);

       if (data.code === "ERR") {
           console.log("Error on Get Questions.");
       } else {
           var table = Doc.getElementById("videos").getElementsByTagName("tbody")[0];
           table.innerHTML = '';
           console.log(data.data);
           for(const n in data.data) {
               var row = table.insertRow(table.rows.length);
               // 질문번호(pid) 영상주소(url)   과목(curr)   책정보(bookname+year)  페이지(page)   번호(number)  강사(tutor)   조회수(hit)
               var pid = row.insertCell(0);
               var url = row.insertCell(1);
               var curr = row.insertCell(2);
               var book = row.insertCell(3);
               var page = row.insertCell(4);
               var number = row.insertCell(5);
               var tutor = row.insertCell(6);
               var hit = row.insertCell(7);

               pid.innerHTML = data.data[n][0];
               curr.innerHTML = data.data[n][2];
               book.innerHTML = data.data[n][3];
               page.innerHTML = data.data[n][4];
               number.innerHTML = data.data[n][5];
               tutor.innerHTML = data.data[n][6];
               hit.innerHTML = data.data[n][7];

               url.innerHTML = "<a target='blank' href='"+data.data[n][1]+"'>(새탭)</a>";

           }
       }
    });
}
