var Doc = window.document;

window.toggle = function (elem) {
	var hidden_menu = Doc.querySelector('.hide_menu');
	var opened = hidden_menu.style.opacity ? Boolean(parseInt(hidden_menu.style.opacity)) : false;

	hidden_menu.style.opacity = opened ? 0 : 1;
};