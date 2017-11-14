var Doc = window.document;

window.toggle = function (elem) {
	var hidden_menu = Doc.querySelector('.hide_menu');
	var opened = hidden_menu.style.opacity ? Boolean(parseInt(hidden_menu.style.opacity)) : false;

	hidden_menu.style.opacity = opened ? 0 : 1;
};

function getBooks(elem){
	var data = elem.value;
	$.get("/api/textbooks?key=bookname&curr="+data, function(data){
	    console.log(JSON.parse(data).result);
    })
}