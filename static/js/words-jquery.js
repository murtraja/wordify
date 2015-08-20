$(document).ready(function(){
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
});