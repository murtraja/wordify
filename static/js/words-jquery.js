$(document).ready(function(){
	$.get('/words/nextword/', {}, function(data) {
		var url = 'http://tts-api.com/tts.mp3?q='+data['next'];
		var a = new Audio(url);
		a.play();
	});
	/*
	$("#subb").click(function(){
		var cw = $('#cw').val()
		$.get('/words/nextword/', {cword: cw}, function(data){
			$('#myDiv').html(data);
			//var text = document.getElementById(id).value;
            var url = 'http://tts-api.com/tts.mp3?q='+data;
            var a = new Audio(url);
                a.play();
			//alert("The paragraph was clicked.");
                //the url should be retrieved from server <--- todo
		});
	});
	 */
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
				
			$('#myDiv').html(data['next']);
			//var text = document.getElementById(id).value;
			var url = 'http://tts-api.com/tts.mp3?q='+data['next'];
			var a = new Audio(url);
			a.play();
			}
			//alert("The paragraph was clicked.");
			//the url should be retrieved from server <--- todo
		});
	});
});