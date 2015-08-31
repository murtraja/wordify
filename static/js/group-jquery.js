$(document).ready(function(){
	
	var ws4redis;


	var listMessage = function(message){
		$('#status_messages').append('<li> '+message+' </li>');
		console.log(message);
	};

	var getUserInput = function(){
		var msg = $('#input_word').val();
		return msg;
	};

	var createSocket = function(){
		ws4redis = WS4Redis({
        uri: WEBSOCKET_URI+'wordify?subscribe-group',
        receive_message: receiveMessage,
        heartbeat_msg: WS4REDIS_HEARTBEAT
    	});
	};

	function receiveMessage(msg) {
        if (msg == '#start')
        {
        	listMessage("now starting...")
        }
        else{

        	listMessage(msg);        
        }
    }
    $('#connect_button').click(function(){
    	$('#connect_button').hide();
    	createSocket();
    	//notify the server about this connection
    	$.post()
    })

});