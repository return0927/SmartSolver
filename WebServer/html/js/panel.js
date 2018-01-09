$(document).ready(function(){
    getQuestions();
    getProblems();
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

               var modify = row.insertCell(10);
               var del = row.insertCell(11);
               var err = row.insertCell(12);

               pid.innerHTML = data.data[n][0];
               qid.innerHTML = data.data[n][1];
               sid.innerHTML = data.data[n][2];
               time.innerHTML = data.data[n][3];
               curr.innerHTML = data.data[n][4];
               book.innerHTML = data.data[n][5];
               page.innerHTML = data.data[n][6];
               number.innerHTML = data.data[n][7];
               message.innerHTML = data.data[n][9];

               modify.innerHTML = "<a onclick='modifyMessage(this);'>수정 </a>";
               del.innerHTML = "<a onclick='removeQuestion(this);'>삭제 </a>";
               err.innerHTML = "<a onclick='markQuestion(this);'>오류로 표기</a>";

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

function getProblems(){
    $.get("/panel/api/problems?c=", function(response){
        var data = JSON.parse(response);

       if (data.code === "ERR") {
           console.log("Error on Get Questions.");
       } else {
           var table = Doc.getElementById("problems").getElementsByTagName("tbody")[0];
           table.innerHTML = '';
           console.log(data.data);
           for(const n in data.data) {
               var row = table.insertRow(table.rows.length);

               var pid = row.insertCell(0);
               var curr = row.insertCell(1);
               var book = row.insertCell(2);
               var page = row.insertCell(3);
               var number = row.insertCell(4);

               pid.innerHTML = data.data[n][0];
               curr.innerHTML = data.data[n][1];
               book.innerHTML = data.data[n][2];
               page.innerHTML = data.data[n][3];
               number.innerHTML = data.data[n][4];

               var del = row.insertCell(5);
               del.innerHTML = "<a onclick='removeProblem(this);'>삭제</a>";

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

               var del = row.insertCell(8);
               del.innerHTML = "<a onclick='removeVideo(this);'>삭제</a>";

           }
       }
    });
}


function modifyMessage(elem){
    var qid = elem.parentElement.parentElement.getElementsByTagName("td")[0].innerHTML;
    new_message = prompt(qid+"번 질문의 메세지를 수정합니다.","");
    if(new_message) {
        try {
            $.post("/panel/api/editMessage", {"qid": qid, "msg": new_message}, function (resp) {
                try {
                    var data = JSON.parse(resp);

                    if (data.code === "ERR") {
                        alert("수정하는데 오류가 발생하였습니다.");
                        alert(data.data);
                        location.reload();
                    } else {
                        alert("수정되었습니다.");
                        location.reload();
                    }
                } catch(e) {
                    alert("수정하는데 오류가 발생하였습니다.");
                    alert(e);
                    location.reload();
                }
            });
        } catch(e){
            alert("수정하는데 오류가 발생하였습니다.");
            alert(e);
            location.reload();
        }
    }
}

function markQuestion(elem){
    var qid = elem.parentElement.parentElement.getElementsByTagName("td")[0].innerHTML;
    p = confirm("정말로 "+qid+" 번 질문을 오류로 표기하시겠습니까?");

    if(p) {
        try {
            $.post("/panel/api/markQuestion", {"qid": qid}, function (resp) {
                try {
                    var data = JSON.parse(resp);

                    if (data.code === "ERR") {
                        alert("표기하는데 오류가 발생하였습니다.");
                        alert(data.data);
                        location.reload();
                    } else {
                        alert("수정되었습니다.");
                        location.reload();
                    }
                } catch(e) {
                    alert("요청을 처리하는동안 오류가 발생하였습니다.");
                    alert(e);
                }
            });
        } catch(e) {
            alert("수정하는 도중 오류가 발생하였습니다.");
            alert(e);
        }
    }
}

function removeQuestion(elem){
    var qid = elem.parentElement.parentElement.getElementsByTagName("td")[0].innerHTML;
    p = confirm("정말로 "+qid+" 번 질문을 삭제하시겠습니까?");

    if(p) {
        try {
            $.post("/panel/api/delQuestion", {"qid": qid}, function (resp) {
                try {
                    var data = JSON.parse(resp);

                    if (data.code === "ERR") {
                        alert("삭제하는데 오류가 발생하였습니다.");
                        alert(data.data);
                        location.reload();
                    } else {
                        alert("삭제되었습니다.");
                        location.reload();
                    }
                } catch(e) {
                    alert("요청을 처리하는동안 오류가 발생하였습니다.");
                    alert(e);
                }
            });
        } catch(e) {
            alert("삭제하는 도중 오류가 발생하였습니다.");
            alert(e);
        }
    }
}

function removeProblem(elem){
    var pid = elem.parentElement.parentElement.getElementsByTagName("td")[0].innerHTML;
    p = confirm("정말로 "+pid+" 번 문제을 삭제하시겠습니까?");

    if(p) {
        try {
            $.post("/panel/api/delProblem", {"pid": pid}, function (resp) {
                try {
                    var data = JSON.parse(resp);

                    if (data.code === "ERR") {
                        alert("삭제하는데 오류가 발생하였습니다.");
                        alert(data.data);
                        location.reload();
                    } else {
                        alert("삭제되었습니다.");
                        location.reload();
                    }
                } catch(e) {
                    alert("요청을 처리하는동안 오류가 발생하였습니다.");
                    alert(e);
                }
            });
        } catch(e) {
            alert("삭제하는 도중 오류가 발생하였습니다.");
            alert(e);
        }
    }
}

function removeVideo(elem){
    var vid = elem.parentElement.parentElement.getElementsByTagName("td")[0].innerHTML;
    p = confirm("정말로 "+vid+" 번 문제의 영상을 삭제하시겠습니까?");

    if(p) {
        try {
            $.post("/panel/api/delVideo", {"vid": vid}, function (resp) {
                try {
                    var data = JSON.parse(resp);

                    if (data.code === "ERR") {
                        alert("삭제하는데 오류가 발생하였습니다.");
                        alert(data.data);
                        location.reload();
                    } else {
                        alert("삭제되었습니다.");
                        location.reload();
                    }
                } catch(e) {
                    alert("요청을 처리하는동안 오류가 발생하였습니다.");
                    alert(e);
                }
            });
        } catch(e) {
            alert("삭제하는 도중 오류가 발생하였습니다.");
            alert(e);
        }
    }
}