$(document).ready(function(){
	function playWord(url){
		$("#audio_word").attr('src', url).trigger('play');
		//var a = new Audio(url);
		//a.play();
	}
	//alert("something");
	$.get(SANSWER_POST, {}, function(data) {
		playWord(data['next']);

	});
	$('#my_form').submit(function(event){
		event.preventDefault();
		var input_word = $('#input_word');
		var user_input_word = input_word.val();
		input_word.val('');
		$.post(SANSWER_POST,{inputWord:user_input_word}, function (data){
			if(data['done']){
				//redirect here!
				//alert("you are done!");
				var redirectionUrl = data['next'];
				window.location.replace(redirectionUrl);
			}
			else{
				//alert("hello");				
				playWord(data['next']);
			}
		});

	});
});
