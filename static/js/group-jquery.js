$(document).ready(function(){

    var ws4redis;
    //listMessage('test');
    var ws4redisBroadcast = WS4Redis({
        uri: WEBSOCKET_URI+MY_PREFIX+'?subscribe-broadcast&publish-broadcast&echo',
        receive_message: receiveMessageBroadcast,
        heartbeat_msg: WS4REDIS_HEARTBEAT
    });
    function receiveMessageBroadcast(message){
        message = $.parseJSON(message);
        if (message.type == 'new_group'){
            //alert(message);
            $('#broadcast_messages').append("<li>"+message.owner+" created the group "+message.name+"</li>");
            
        }
    }

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
   }else{

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
                $('#input_word').val('');               
                playWord(data['next']);
            }
        });
});

function playWord(url){
    $("#audio_word").attr('src', url).trigger('play');
        //var a = new Audio(url);
        //a.play();
    }

    $('#new_group_form').submit(function(event){
        event.preventDefault();
        console.log('preventDefault')
        $.post($('#new_group_form').attr('action'), {totwords:$('#totwords').val(), 
            totmembers:$('#totmembers').val(),
            groupname:$('#new_group').val()}, function (data){
                if(data['facility'] == ''){
                    alert("could not create the group! It might already exists.");
                    $('#new_group').val('');
                }
                else{
                    $('#pre_game_elements').show();
            //$('#group_choice').hide();
            FACILITY = data['facility'];
            //alert(FACILITY);
        }
    });
    });

});