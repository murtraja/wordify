$(document).ready(function(){

    /*
        when this page is requested for the first time,
        it should contain a list of already created groups,
        so populateGroups() does that

        but as this is single page, it must also update
        continuously upon receiving new_group info,
        so receiveMessageBroadcast() does that

        now when the user wishes to join/create a valid group,
        the group_selection portion is hidden and pre_game
        portion is visible, wherein the user waits for other
        users to connect. 

        as soon as user creates/joins any group he/she is subscribed
        to its group specific messages, so receiveMessage() does that

        and when required users are connected the competition starts automatically

        */

    // creating broadcast socket
    var ws4redisBroadcast = WS4Redis({
        uri: WEBSOCKET_URI+MY_PREFIX+'?subscribe-broadcast',
        receive_message: receiveMessageBroadcast,
        heartbeat_msg: WS4REDIS_HEARTBEAT
    });

    // receiver for broadcast messages
    function receiveMessageBroadcast(message){
        /*
            as the broadcast messages can be of different types,
            it is better to send it in json format and then parse it
            */
            var message_original = message;
            message = $.parseJSON(message);
            if (message.type == 'new_group'){
                listBroadcastMessage(message.owner+" created the group "+message.name);
                populateGroups();            
            }
            else if(message.type=='new_join'){
                listBroadcastMessage(message.who+" joined the group "+message.name);
                populateGroups();
            }
            else if(message.type == 'test'){
                listBroadcastMessage(message.message);
            }
            else if(message.type == 'group_delete'){
                listBroadcastMessage("group '"+message.name+"' was removed from available groups");
                if(FACILITY == message.name){
                    //this group itself was removed
                    $('#pre_game_elements').hide();
                    $('#group_choice').show();
                }
                populateGroups();
            }
            else if(message.type == 'group_busy'){
                listBroadcastMessage("group '"+message.name+"' competition commenced!");
                if (message.name!= FACILITY){
                    populateGroups();                }
            }
            else{
                alert("broadcast message of unknown type received:"+message_original)
            }
        }

    //empty the group selection
    function depopulateGroups(){
        $('#group_select').html('');
    }
    
    //populate the groups by querying the server
    populateGroups();
    function populateGroups(){
        $.get(GINFO, function(data){
            if (data['group_count'] > 0)
            {
                // there are some groups created
                // console.log("group count > 0");
                // console.log(data['group_list']);
                depopulateGroups();
                $.each(data['group_list'], function(index, item){
                    //console.log(item);
                    addGroup(item['name'], item['owner'], item['totwords'], item['totmembers'], item['curmembers']);
                });
                $('#group_list_updated').show();
            }
            else
            {
                //there are no groups created
                depopulateGroups();
            }
        });

    }

    // this ensures that user knows when some new group was created
    $('#group_select').click(function(){
        $('#group_list_updated').hide();
        $('#new_group').val($(this).val());        
    });

    //for user convenience only
    $('#group_select').change(function(event){
        console.log("changed");
        $('#new_group').val($(this).val());
    });

    //used by populateGroups() to append new group info
    function addGroup(name, owner, words, members, cmembers){
        $('#group_select').append("<option value = '"+name+"'>"+ 
            name+" by "+owner+" of "+words+" words "+
            "having "+cmembers+"/"+members+" members");
    }

    // as the name suggests
    function listBroadcastMessage(message){
      $('#broadcast_messages').append('<li> '+message+' </li>');
      console.log(message);
  }

$('#test_publish').click(function(){
    $.get('/words/test_publish',{facility:FACILITY});
});

// to create/join group
$('#new_group_form').submit(function(event){
    event.preventDefault();
    console.log('preventing Default for group join form');
    if($('#new_group').val() == ''){
    alert("group name can't be empty!");
    return;
}
    $.post($('#new_group_form').attr('action'), {totwords:$('#totwords').val(), 
        totmembers:$('#totmembers').val(),
        groupname:$('#new_group').val()}, function (data){
            if(data['facility'] == ''){
                alert("unable to join you to the group.");
                $('#new_group').val('');
            }
            else{
                $('#pre_game_elements').show();
                $('#group_choice').hide();
                FACILITY = data['facility'];
                createSocket();
                if(data['new_group_created']){
                    console.log("new group was created:"+FACILITY);
                    $('#delete_group').show();
                }
                else{
                    $('#delete_group').hide();
                    console.log("user joined to existing group:"+FACILITY);
                }
            //alert(FACILITY);
        }
    });
});
    // appends group specific messages
    function listMessage (message){
      $('#status_messages').append('<li> '+message+' </li>');
      console.log(message);
  }


    // this creates a group specific socket
    // the value of FACILITY is nothing but the group
    // in which this user has joined
    function createSocket(){
      ws4redis = WS4Redis({
        uri: WEBSOCKET_URI+FACILITY+'?subscribe-broadcast',
        receive_message: receiveMessage,
        heartbeat_msg: WS4REDIS_HEARTBEAT
    });
  }

  // receiver for group specific messages
  // TODO msg must be converted to json and then parsed
  function receiveMessage(msg) {

    if (msg == '#start')
    {
       listMessage("now starting...");
       $('#session_start_notice').hide();
       $('#group_choice').hide();
       $('#game_elements').show();
       // necessary to supply facility in order to publish
       // messages on correct groups
       $.post(GANSWER_POST, {facility:FACILITY},function (data){
        playWord(data['next']);
    });
   }else{

       listMessage(msg);
   }
}
    // to get the answer given by user
    function getUserInput(){
      var msg = $('#input_word').val();
      return msg;
  }

  $('#delete_group').click(function(){
    console.log("now called delete_group");
    $.post(GDELETE, {name:FACILITY}, function(data){
        if(data['done']){
            //the group was deleted succesfully
            // now display the hidden fields or just refresh page
            alert('group deleted');
        }
        else{
            alert('not deleted');
        }
    });
  });

// game logic
$('#my_form').submit(function(event){
    event.preventDefault();
    $.post(GANSWER_POST,{input_word:getUserInput(), facility:FACILITY}, function (data){
        if(data['done']){
                //redirect here!
                var redirectionUrl = data['next'];
                $('#redirection_url').attr('href', redirectionUrl).show();
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
}

    $('#nullify').click(function(){
        ws4redisBroadcast = null;
    });

});