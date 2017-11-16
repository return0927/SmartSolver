var Doc = window.document;

window.toggle = function (elem) {
	var hidden_menu = Doc.querySelector('.hide_menu');
	var opened = hidden_menu.style.opacity ? Boolean(parseInt(hidden_menu.style.opacity)) : false;

	hidden_menu.style.opacity = opened ? 0 : 1;
};

function setBooks(){
	var data = $("select#curr")[0].value;
	$.get("/api/textbooks?key=bookname&curr="+data, function(response){_setBooks(JSON.parse(response).result);});
}

function _setBooks(arr) {
	var book = $("select#book")[0], i;
	book.length = 0;

	for(i=0;i<arr.length;i++){
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


function setYears(){
	var curr = $("select#curr")[0].value;
	var book = $("select#book")[0].value;
	$.get("/api/bookModifiedYear?&curr="+curr+"&book="+book, function(response){_setYears(JSON.parse(response).result);});
}

function _setYears(arr) {
	var book = $("select#year")[0], i;
	book.length = 0;

	for(i=0;i<arr.length;i++){
		var data = arr[i];

		var elem = document.createElement("option");
		elem.value = data.toString();
		elem.innerHTML = data.toString();
		book.add(elem, null);
	}
	return true;
}


function setBookPublisher(){
	var curr = $("select#curr")[0].value;
	var book = $("select#book")[0].value;
	$.get("/api/bookPublisher?curr="+curr+"&book="+book, function(response){_setBookPublisher(JSON.parse(response).result);});
}

function _setBookPublisher(data) {
	var pub = $("#bookPublisher")[0];
	pub.innerHTML = "출판사: <font color='#8b0000'>"+data+"</font>";

	return true;
}


function setBookNotice(){
	var curr = $("select#curr")[0].value;
	var book = $("select#book")[0].value;
	$.get("/api/bookNotice?curr="+curr+"&book="+book, function(response){_setBookNotice(JSON.parse(response).result);});
}

function _setBookNotice(data) {
	$("#book_notice")[0].innerHTML = data;
}