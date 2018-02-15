(function() {
  // Localize jQuery variable
  var jQuery;
  /******** Load jQuery if not present *********/
  if (window.jQuery === undefined || window.jQuery.fn.jquery !== '1.4.2') {
      var script_tag = document.createElement('script');
      script_tag.setAttribute("type","text/javascript");
      script_tag.setAttribute("src",
          "//ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js");
      if (script_tag.readyState) {
        script_tag.onreadystatechange = function () { // For old versions of IE
            if (this.readyState == 'complete' || this.readyState == 'loaded') {
                scriptLoadHandler();
            }
        };
      } else {
        script_tag.onload = scriptLoadHandler;
      }
      // Try to find the head, otherwise default to the documentElement
      (document.getElementsByTagName("head")[0] || document.documentElement).appendChild(script_tag);
  } else {
      // The jQuery version on the window is the one we want to use
      jQuery = window.jQuery;
      main();
  }
  /******** Called once jQuery has loaded ******/
  function scriptLoadHandler() {
    // Restore $ and window.jQuery to their previous values and store the
    // new jQuery in our local jQuery variable
    jQuery = window.jQuery.noConflict(true);
    // Call our main function
    main();
  }

  /******** Our main function ********/
  function main() {
    //---------------------------
    //VAR REGION
    //---------------------------
    //setup variables
    //var server = '//192.168.0.30:9090';
    var server ='https://a2.botprotec.com/backend/static/widget/';
    var botName = document.getElementById("chat-widget-container").getAttribute("botName");
    var botId = document.getElementById("chat-widget-container").getAttribute("botId");
    var botToken = document.getElementById("chat-widget-container").getAttribute("botToken");
    var backend = 'https://a2.botprotec.com/backend/webhook/hook/';
    var width = document.getElementById("chat-widget-container").getAttribute("width");
    var height = document.getElementById("chat-widget-container").getAttribute("height");
    var userId = '';
    var userName = '';
    //----------------------------------------
    //var for creating HTML Elements
    var HTMLString = '';
    var sampleText = '';
    var inputBoxHTML = '';
    var isSample = false;
    //---------------------------
    jQuery(document).ready(function($) {
      $.ajax({
          type: "GET",
          data: { token: botToken },
          url: backend + 'website/' + botId +'.json',
          contentType: 'application/x-www-form-urlencoded',
          dataType: "json",
          crossDomain: true,
          beforeSend: function(){},
          complete: function(data){},
          success: function(data){
            /*
            * Obtains a intenger that indicates if the token-bot values specified in the Widget
            * actually match to the data stored in the web-server.
            * Expected Results: 0-No Match, 1-Has a Match (OK to go ahead)
            */
            var result = data.verification;
            if (result == 1) {
              setupHostSettings();
              //userId = generateUserID();
            }
            else {
              //error handling
            }
          }
      });//END Ajax Petition

      function setupHostSettings() {
        //setting up css settings
        SetupCSS();
        //if is a sample display site
        try {
          if ('true' === document.getElementById("chat-widget-container").getAttribute("isSample")) {
            isSample = true;
            CreateSampleStructure();
          }
          //create the chat box
          CreateChatBox();
          CreateHelloBox();
          //
          //StartWidget();
        }
        catch(err) {

        }
      }//END setupHostSettings

      function SetupCSS() {
        var cssId = 'botprowidgetcss';  // you could encode the css path itself to generate id..
        if (!document.getElementById(cssId))
        {
            var head  = document.getElementsByTagName('head')[0];
            var link  = document.createElement('link');
            link.id   = cssId;
            link.rel  = 'stylesheet';
            link.type = 'text/css';
            link.href =  server + 'css/ChatWidget.css';
            link.media = 'all';
            head.appendChild(link);
        }
        if(typeof($.fn.modal) === 'undefined') {
          var head  = document.getElementsByTagName('head')[0];
          var link  = document.createElement('link');
          link.id   = cssId;
          link.rel  = 'stylesheet';
          link.type = 'text/css';
          link.href = 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css';
          link.media = 'all';
          head.appendChild(link);
        }
      }//END SetupCSS

      function CreateSampleStructure() {
        //single message item from the bot
        sampleText += '<li class="left clearfix">'
        sampleText += '<span class="chat-img pull-left">'
        sampleText += '<img src="' + server +'img/logo_no_text.png" alt="User Avatar">'
        sampleText += '</span>'
        sampleText += '<div class="chat-body clearfix">'
        sampleText += '<div class="header">'
        sampleText += '<strong class="primary-font">'+ botName +'</strong>'
        //sampleText += '<small class="pull-right text-muted"><i class="fa fa-clock-o"></i> 12 mins ago</small>'
        sampleText += '</div>'
        sampleText += '<p>'
        //sent message
        sampleText += 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
        sampleText += '</p>'
        sampleText += '</div>'
        sampleText += '</li>'
        //single message item from client
        sampleText += '<li class="right clearfix">'
        sampleText += '<span class="chat-img pull-right">'
        sampleText += '<img src="'+ server +'img/person_64.png" alt="User Avatar">'
        sampleText += '</span>'
        sampleText += '<div class="chat-body clearfix">'
        sampleText += '<div class="header">'
        //Client name
        sampleText += '<strong class="primary-font">Sarah</strong>'
        //sampleText += '<small class="pull-right text-muted"><i class="fa fa-clock-o"></i> 13 mins ago</small>'
        sampleText += '</div>'
        sampleText += '<p>'
        //recieved message
        sampleText += 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur bibendum ornare dolor, quis ullamcorper ligula sodales at. '
        sampleText += '</p>'
        sampleText += '</div>'
        sampleText += '</li>'
      }//END CreateSampleStructure

      function CreateChatBox() {
        var style = 'width:'+ width +'px; height:auto;';
        style += "position: fixed;    right: 10px;    bottom: 50px;";
        style += "z-index: 999999;    overflow: hidden;    box-shadow: black 0 0 34px;    background-color: white;";
        document.getElementById('chat-widget-container').setAttribute("style",style);
        HTMLString = '';

        HTMLString = '<div class="content">';
        HTMLString += '<div>';
        HTMLString += '<div>';
        HTMLString += '<div class="chatContainer container-fluid" id="chatContainer">';//chat container

        //CHAT BOX
        //---------------------
        HTMLString += '<div class="row">';
        HTMLString += '<div class="col-sm-12">';
        HTMLString += '<div class="chatbox">';
        HTMLString += '<div class="row">';
        HTMLString += '<div class="col-sm-12">';
        var scrollHeight = parseInt(height) - 50;
        HTMLString += '<div style="overflow:auto; height:'+ scrollHeight +'px;" id="messagescroll">';
        HTMLString += '<div class="chat-message" id="messagebox">';
        HTMLString += '<ul class="chat" id="message-list">';//list of chats
        if (isSample == true){ HTMLString += sampleText; }
        HTMLString += '</ul>';//end of chat messages

        HTMLString += '</div>';//end of scroll
        HTMLString += '</div>';//end col-sm-12
        HTMLString += '</div>';//end row
        HTMLString += '</div>';//end chatContainer
        HTMLString += '</div>';//end chatbox
        HTMLString += '</div>';//end col-sm-12
        HTMLString += '</div>';//end row
        //---------------------
        //CHAT BOX

        HTMLString += '<hr>';

        //REPLY BOX
        //---------------------
        HTMLString += '<div class="row">';
        HTMLString += '<div id="replybox" class="replybox" style="min-height:50px;padding:5px;">';
        HTMLString += '<div class="col-sm-12">';
        HTMLString += '<form class="form-inline" onsubmit="return false;">';
        HTMLString += '<input type="text" class="form-control input-sm" id="txtResponse" onkeypress="return function(e){if (e.keyCode == 13){$(\'#btnReply\')[0].click()}}(event);">';
        HTMLString += '<a id="btnReply" class="btn btn-success btn-sm" name="btnReply">Send</a>';
        HTMLString += '</form>';
        HTMLString += '</div>';//end col-sm-12
        HTMLString += '</div>';//end replybox
        HTMLString += '</div>';//end row
        //---------------------
        //REPLY BOX

        HTMLString += '</div>';//end of chat container
        HTMLString += '</div>';//end col-sm-12
        HTMLString += '</div>';//end row
        HTMLString += '</div>';//end content

        document.getElementById("chat-widget-container").innerHTML = HTMLString;
        btnReply.addEventListener("click", SendMessage, false);
      }//END CreateChatBox

      function CreateHelloBox() {
        try{
          var htmlCode = '';
          htmlCode += '<div class="col-sm-12">';
          htmlCode += '<form class="form-inline" onsubmit="return false;">';
          htmlCode += '<input type="text" class="form-control input-sm" placeHolder="Enter your employee ID" id="txtHello" onkeypress="return function(e){if (e.keyCode == 13){$(\'#btnStart\')[0].click()}}(event);">';
          htmlCode += '<a id="btnStart" class="btn btn-success btn-sm" name="btnStart">Start</a>';
          htmlCode += '</form>';
          htmlCode += '</div>';//end row
          document.getElementById("replybox").innerHTML = htmlCode;
          btnStart.addEventListener("click", setUserName, false);
        }
        catch(err){
          console.log('Error: ' + err);
        }
      }

      function setUserName(){
        try {

          //getting the userId
          userId = document.getElementById('txtHello').value;

          if(userId.length < 3) {
            alert("You must provide a valid employee ID");
          }
          else {
            //setting blank the control
            document.getElementById('txtHello').value = '';
            //setting the default view
            restoreReplyButton();
            document.getElementById('txtResponse').focus();
          }
        }
        catch(err) {
          console.log('Error: '+ err)
        }
      }

      function QuickReply(option){
        AddUserResponse(option);
        try{
          $.ajax({
              type: "POST",
              data: { text: option, id: userId },
              url: backend + 'website/' + botId +'.json',
              contentType: 'application/x-www-form-urlencoded',
              dataType: "text",
              crossDomain: true,
              beforeSend: function(){
                restoreReplyButton();
              },
              complete: function(data){},
              success: function(data){
                var serverResponse = JSON.parse(data);
                processResponse(serverResponse.envelope);
              }
            });
        }
        catch(ex)
        {
          console.log('error '+ ex);
        }
      }//END QuickReply

      function restoreReplyButton() {
        var htmlCode = '';
        htmlCode += '<div class="col-sm-12">';
        htmlCode += '<form class="form-inline" onsubmit="return false;">';
        htmlCode += '<input type="text" class="form-control input-sm" id="txtResponse" onkeypress="return function(e){if (e.keyCode == 13){$(\'#btnReply\')[0].click()}}(event);">';
        htmlCode += '<a id="btnReply" class="btn btn-success btn-sm" name="btnReply">Send</a>';
        htmlCode += '</form>';
        htmlCode += '</div>';//end col-sm-12
        document.getElementById("replybox").innerHTML = htmlCode;
        document.getElementById("txtResponse").focus();
        btnReply.addEventListener("click", SendMessage, false);
        console.log('done');
      }

      //Function that replys to the backend
      function SendMessage() {
        var userResponse = '';
        userResponse = document.getElementById('txtResponse').value;
        if (userResponse.length < 1)
        {
          alert("You must provide an asnwer.")
        }else {
          document.getElementById('txtResponse').value = '';
          AddUserResponse(userResponse);
          try{
            $.ajax({
                type: "POST",
                data: { text: userResponse, id: userId },
                url: backend + 'website/' + botId +'.json',
                contentType: 'application/x-www-form-urlencoded',
                dataType: "text",
                crossDomain: true,
                complete: function(data){},
                success: function(data){
                  var serverResponse = JSON.parse(data);
                  processResponse(serverResponse.envelope);
                }
              });
          }
          catch(ex)
          {
            console.log('error '+ ex);
          }
        }

      }//END SendMessage

      var possibleAnswers = [];

      function processResponse(serverResponse) {
        try {
          AddServerResponse(serverResponse.text);
          if(serverResponse.hasOwnProperty('reply_markup')){
            possibleAnswers = serverResponse.reply_markup.keyboard[0];
            var items = possibleAnswers.length;
            var btnWidth = Math.round(12/items);
            var htmlCode = '';
            var position = 0;
            htmlCode += '<div class="text-center">';
            possibleAnswers.forEach(function(option) {
                htmlCode += '<button id="option'+standarizeEntry(option)+'" class="btn btn-info btn-sm">'+option+'</button>';
            });
            htmlCode += '</div>';
            document.getElementById("replybox").innerHTML = '';
            document.getElementById("replybox").innerHTML = htmlCode;
            htmlCode = '';
            //adding event listeners
            possibleAnswers.forEach(function(option) {
              let btnName = 'option' + standarizeEntry(option);
              document.getElementById(btnName).addEventListener("click", function (e) {QuickReply(option)}, false);
            });
          }
          //{"envelope": {"text": "Hello there! Do you like MEMES?", "chat_id": "123456", "reply_markup": {"one_time_keyboard": true, "keyboard": [["yes", "no"]]}}, "method": "sendMessage"}
        } catch (e) {
          console.log('error ' + e);
        }
      }

      function standarizeEntry(string){
        // Definimos los caracteres que queremos eliminar
        var specialChars = "!@#$^&%*()+=-[]\/{}|:<>?,.";
        // Los eliminamos todos
        for (var i = 0; i < specialChars.length; i++) {
            string= string.replace(new RegExp("\\" + specialChars[i], 'gi'), '');
        }
        // Lo queremos devolver limpio en minusculas
        string = string.toLowerCase();
        // Quitamos espacios y los sustituimos por _ porque nos gusta mas asi
        string = string.replace(/ /g,"_");
        // Quitamos acentos y "ñ". Fijate en que va sin comillas el primer parametro
        string = string.replace(/á/gi,"a");
        string = string.replace(/é/gi,"e");
        string = string.replace(/í/gi,"i");
        string = string.replace(/ó/gi,"o");
        string = string.replace(/ú/gi,"u");
        string = string.replace(/ñ/gi,"n");
        return string;
      }

      //Starts the communication process
      function StartWidget() {
        try{
          $.ajax({
              type: "POST",
              data: { text: 'this is a text', id: userId },
              url: backend + 'website/' + botId +'.json',
              contentType: 'application/x-www-form-urlencoded',
              dataType: "text",
              crossDomain: true,
              complete: function(data){
                console.log('request completed');
              },
              success: function(data){
                console.log('made it');
                console.log(data);
              }
            });
        }
        catch(ex)
        {
          console.log('error '+ ex);
        }
      }//END StartWidget

      function AddServerResponse(response) {
        HTMLString = document.getElementById("message-list").innerHTML;
        //single message item from the bot
        HTMLString += '<li class="left clearfix">';
        HTMLString += '<span class="chat-img pull-left">';
        HTMLString += '<img src="' + server +'img/logo_no_text.png" alt="User Avatar">';
        HTMLString += '</span>';
        HTMLString += '<div class="chat-body clearfix">';
        HTMLString += '<div class="header">';
        HTMLString += '<strong class="primary-font">'+ botName +'</strong>';
        //sampleText += '<small class="pull-right text-muted"><i class="fa fa-clock-o"></i> 12 mins ago</small>'
        HTMLString += '</div>';
        HTMLString += '<p>';
        //sent message
        HTMLString += response;
        HTMLString += '</p>';
        HTMLString += '</div>';
        HTMLString += '</li>';
        document.getElementById("message-list").innerHTML = HTMLString;
        var elem = document.getElementById('messagescroll');
        elem.scrollTop = elem.scrollHeight;
      }

      function AddUserResponse(response) {
        HTMLString = document.getElementById("message-list").innerHTML;
        HTMLString += '<li class="right clearfix">';
        HTMLString += '<span class="chat-img pull-right">';
        HTMLString += '<img src="'+ server +'img/person_64.png" alt="User Avatar">';
        HTMLString += '</span>';
        HTMLString += '<div class="chat-body clearfix">';
        HTMLString += '<div class="header">';
        //Client name
        HTMLString += '<strong class="primary-font">'+ userId +'</strong>';
        //sampleText += '<small class="pull-right text-muted"><i class="fa fa-clock-o"></i> 13 mins ago</small>'
        HTMLString += '</div>';
        HTMLString += '<p>';
        //recieved message
        HTMLString += response;
        HTMLString += '</p>';
        HTMLString += '</div>';
        HTMLString += '</li>';
        document.getElementById("message-list").innerHTML = HTMLString;
        var elem = document.getElementById('messagescroll');
        elem.scrollTop = elem.scrollHeight;
      }

    });//END Document Ready

  }



function verifyStyle(selector) {
    var rules;
    var haveRule = false;
    if (typeof document.styleSheets != "undefined") {   //is this supported
        var cssSheets = document.styleSheets;
        outerloop:
        for (var i = 0; i < cssSheets.length; i++) {
           //using IE or FireFox/Standards Compliant
          rules =  (typeof cssSheets[i].cssRules != "undefined") ? cssSheets[i].cssRules : cssSheets[i].rules;
           for (var j = 0; j < rules.length; j++) {
               if (rules[j].selectorText == selector) {
                       haveRule = true;
                      break outerloop;
               }
          }//innerloop
      }//outer loop
  }//endif
  return haveRule;
}//eof



})(); // We call our anonymous function immediately


function createCORSRequest(method, url) {
  var xhr = new XMLHttpRequest();
  if ("withCredentials" in xhr) {
    xhr.open(method, url, true);
  } else if (typeof XDomainRequest != "undefined") {
    xhr = new XDomainRequest();
    xhr.open(method, url);
  } else {
    xhr = null;
  }
  return xhr;
}
