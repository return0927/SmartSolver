var Doc = window.document;

window.toggle = function (elem) {
    var hidden_menu = Doc.querySelector('.hide_menu');
    var opened = hidden_menu.style.opacity ? Boolean(parseInt(hidden_menu.style.opacity)) : false;

    hidden_menu.style.opacity = opened ? 0 : 1;
};

function setBooks() {
    var data = $("select#curr")[0].value;
    $.get("/api/textbooks?key=bookname&curr=" + data, function (response) {
        _setBooks(JSON.parse(response).result);
    });
}

function _setBooks(arr) {
    var book = $("select#book")[0], i;
    book.length = 0;

    for (i = 0; i < arr.length; i++) {
        var data = arr[i];

        var elem = document.createElement("option");
        elem.value = data;
        elem.innerHTML = data;
        book.add(elem, null);
    }

    /* Iterable YearInfo */
    setYears();

    return true;
}


function setYears() {
    var curr = $("select#curr")[0].value;
    var book = $("select#book")[0].value;
    $.get("/api/bookModifiedYear?&curr=" + curr + "&book=" + book, function (response) {
        _setYears(JSON.parse(response).result);
    });
}

function _setYears(arr) {
    var book = $("select#year")[0], i;
    book.length = 0;

    for (i = 0; i < arr.length; i++) {
        var data = arr[i];

        var elem = document.createElement("option");
        elem.value = data.toString();
        elem.innerHTML = data.toString();
        book.add(elem, null);
    }
    return true;
}


function setBookPublisher() {
    var curr = $("select#curr")[0].value;
    var book = $("select#book")[0].value;
    $.get("/api/bookPublisher?curr=" + curr + "&book=" + book, function (response) {
        _setBookPublisher(JSON.parse(response).result);
    });
}

function _setBookPublisher(data) {
    console.log(data);
    var pub = $("#bookPublisher")[0];
    pub.innerHTML = "출판사: <font color='#8b0000'>" + data + "</font>";

    return true;
}


function setBookNotice() {
    var curr = $("select#curr")[0].value;
    var book = $("select#book")[0].value;
    $.get("/api/bookNotice?curr=" + curr + "&book=" + book, function (response) {
        _setBookNotice(JSON.parse(response).result);
    });
}

function _setBookNotice(data) {
    $("#book_notice")[0].innerHTML = data;
}


function getMyQuestions() {
    $.get("/api/pp/my_question", function(response){
        var resp = JSON.parse(response);
        console.log(resp);

        if(!resp.error) {
            _makeQuestionTable(resp.data);
        } else {
            alert("회원님의 질문을 불러오는 중에 오류가 발생하였습니다!");
        }
    });
}

function _makeQuestionTable(data) {
    var table = $("#questionTable tbody")[0];

    var i;
    for(i=0; i<data.length; i++) {
        var row = table.insertRow(table.rows.length);
        var timestamp = row.insertCell(0), book = row.insertCell(1), num = row.insertCell(2), status = row.insertCell(3);

        timestamp.innerHTML = data[i][0];
        // status.innerHTML = data[i][2] ? "<a href='" + data[i][4] + "' target='blank'>영상확인</a>" : "<p align='center'><div class='circle pending'></div>대기중</p>";
        var stat = JSON.parse(data[i][2]);
        console.log(stat);
        if(stat.status === 0) {
            status.innerHTML = "<p align='center'><div class='circle pending'></div>" + stat.message + "</p>";
        } else if(stat.status === 1) {
            status.innerHTML = "<a href='" + data[i][4] + "' target='blank'>영상확인</a>";
        } else {
            status.innerHTML = "<p align='center'><div class='circle error'></div>" + stat.message + "</p>";
        }

        num.innerHTML = data[i][6];
        book.classList.add("book");
        book.innerHTML = data[i][5];

    }
}

/*
    Submit my question
 */
function submitQuestion() {
    var data = {"curr": $("#curr")[0].value, "book": $("#book")[0].value, "year": $("#year")[0].value, "number": $("#number")[0].value, "question": $("#question")[0].value};
    $.post("/submit", data, function(data){
        document.write(data);
    })
}


/*
	Popup
 */

$('.btn-example').click(function () {
    var $href = $(this).attr('href');
    layer_popup($href);
});

function layer_popup(el) {

    var $el = $(el);        //레이어의 id를 $el 변수에 저장
    var isDim = $el.prev().hasClass('dimBg');   //dimmed 레이어를 감지하기 위한 boolean 변수

    isDim ? $('.dim-layer').fadeIn() : $el.fadeIn();

    var $elWidth = ~~($el.outerWidth()),
        $elHeight = ~~($el.outerHeight()),
        docWidth = $(document).width(),
        docHeight = $(document).height();

    // 화면의 중앙에 레이어를 띄운다.
    if ($elHeight < docHeight || $elWidth < docWidth) {
        $el.css({
            marginTop: -$elHeight / 2,
            marginLeft: -$elWidth / 2
        })
    } else {
        $el.css({top: 0, left: 0});
    }

    $el.find('a.btn-layerClose').click(function () {
        isDim ? $('.dim-layer').fadeOut() : $el.fadeOut(); // 닫기 버튼을 클릭하면 레이어가 닫힌다.
        return false;
    });

    $('.layer .dimBg').click(function () {
        $('.dim-layer').fadeOut();
        return false;
    });

}