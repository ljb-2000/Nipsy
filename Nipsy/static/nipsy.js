namespace = '/test';
var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);

socket.on('my response', function(msg) {
    // cache selector.. pff
    var $msgId = $('#' + msg.id);
    if (!$msgId.length) {
        // TODO
        // rewrite this duplicate later
        $('#notifications').prepend(
            sprintf(
                html,
                msg.status,
                msg.id,
                msg.id,
                msg.id,
                msg.status,
                msg.task,
                msg.task,
                msg.user,
                msg.sdate,
                msg.fdate,
                msg.roles
            )
        );
    } else {
        $msgId.replaceWith(
            sprintf(
                html,
                msg.status,
                msg.id,
                msg.id,
                msg.id,
                msg.status,
                msg.task,
                msg.task,
                msg.user,
                msg.sdate,
                msg.fdate,
                msg.roles
            )
        );
    }
});

function sprintf( format )
{
  for( var i=1; i < arguments.length; i++ ) {
    format = format.replace( /%s/, arguments[i] );
  }
  return format;
}

function settings() {
    $.ajax({
        url: "/settings",
        type: "GET",
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        success: function (response) {
            $.each(response, function (key, data) {
                $( "#" + key ).remove();
                $( "#settings_div" ).append(
                    '<h4 id="' + key +'">' + key + ":    <small>"+ data + '</small></h4>');
            })
        }
    });
}

var html;
// seems slash concat much faster than array join
html = '<li><div class="alert alert-%s" id="%s"> \
<div class="row"> \
        <div class= "col-lg-4 text-left"> \
            <a href="/tasks/deployments/%s"> \
                <strong>#%s - %s</strong> \
            </a> \
        </div> \
     </div> \
     <div class="row"> \
        <div class="col-lg-4 text-left"> \
            <ul class="list-unstyled"> \
                <li> \
                    <strong>Task: <a href="/tasks/%s"> \
                        %s</a> \
                    </strong> \
                </li> \
                <li> \
                    <strong>User: </strong> %s \
                </li> \
            </ul> \
        </div> \
        <div class="col-lg-4 text-left"> \
            <ul class="list-unstyled"> \
                <li> \
                    <strong>Started at:</strong> %s \
                </li> \
                <li> \
                    <strong>Finished at:</strong> %s \
                </li> \
            </ul> \
        </div> \
        <div class="col-lg-4"> \
                <span class="glyphicon glyphicon-ok"></span> \
        </div> \
     </div> \
     <div class="row"> \
         <div class="col-lg-12 text-left"> \
            <strong> Hosts: </strong> %s \
        </div> \
     </div> \
</div></li>';