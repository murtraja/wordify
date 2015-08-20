$(document).ready(function(){
	function playWord(url){
		var a = new Audio(url);
		a.play();
	}
	$.get('/words/nextword/', {}, function(data) {
		playWord(data['next']);

	});
	/*
	$("#subb").click(function(){
		//var cw = $('#cw').val()
		$.getJSON('/words/nextword/', function(data){
			if(data['done']){
				//redirect here!
				alert("you are done!")
				var redirectionUrl = data['next']
				window.location.replace(redirectionUrl);
			}
			else {
				playWord(data['next']);
			}
			//alert("The paragraph was clicked.");
		});
	});
	 */
	$('#my_form').submit(function(event){
		event.preventDefault();
		$.post('/words/nextword/',{inputWord:$('#input_word').val()}, function (data){
			if(data['done']){
				//redirect here!
				alert("you are done!");
				var redirectionUrl = data['next'];
				window.location.replace(redirectionUrl);
			}
			else{
				playWord(data['next']);
			}
		});

	});
});