$(document).ready(function(){
	
	var ws4redis;
    listMessage('test');

	function listMessage (message){
		$('#status_messages').append('<li> '+message+' </li>');
		console.log(message);
	}

	function getUserInput(){
		var msg = $('#input_word').val();
		return msg;
	}

	function createSocket(){
		ws4redis = WS4Redis({
        uri: WEBSOCKET_URI+'wordify?subscribe-group',
        receive_message: receiveMessage,
        heartbeat_msg: WS4REDIS_HEARTBEAT
    	});
	}

	function receiveMessage(msg) {
        if (msg == '#start')
        {
        	listMessage("now starting...");
            $('#session_start_notice').hide();
            $('#game_elements').show();
            $.post(GANSWER_POST, function (data){
                playWord(data['next']);
            });
        }
        else{

        	listMessage(msg);        
        }
    }
    $('#connect_button').click(function(){
    	$('#connect_button').hide();
    	createSocket();
    	//notify the server about this connection
    	$.post(GCONNECT_POST, {
            user : $('#user').html()
        });
    });

    $('#test_publish').click(function(){
        $.get('/words/test_publish');
    });

    $('#my_form').submit(function(event){
        event.preventDefault();
        $.post(GANSWER_POST,{input_word:getUserInput()}, function (data){
            if(data['done']){
                //redirect here!
                //alert("you are done!");
                var redirectionUrl = data['next'];
                //window.location.replace(redirectionUrl);
                $('#redirecion_url').attr('href', redirectionUrl);
                $('#redirection_url').show();
                $('#game_elements').hide();
            }
            else{
                //alert("hello");               
                playWord(data['next']);
            }
        });
    });

        function playWord(url){
        $("#audio_word").attr('src', url).trigger('play');
        //var a = new Audio(url);
        //a.play();
    }

    });