<script>
var msgs = [];
var peeked = "";
var who_last;
var users = "";
var user_name;

function maybeEnter(e) {
    if(e.keyCode==13) {
        push();
        document.getElementById("type_box").value = "";
    } else {
        leak();
    }
}

function robust(str) {
    var strs = str.split("&");
    var temp;
    for (var i = 0;i<strs.length;i++) {
        temp = strs[i].replace("<br>", "__br__");
        temp = temp.replace("<", "&lt");
        temp = temp.replace(">", "&gt");
        temp = temp.replace("__br__", "<br>");
        temp = temp.replace('"', "&quot");
        strs[i] = temp.replace("'", "&#39");
    }
    return strs.join("&amp");
}

function enter() {
    document.getElementById("warning").innerHTML ="";
    document.getElementById("naming").style.display="initial";
}

function nameMe() {
    user_name = getName().replace(" ", "_").padStart(12, "_");
    document.getElementById("naming").innerHTML = "";
    document.getElementById("history").innerHTML ="Loading... ";
    document.getElementById("my_name").innerHTML = user_name.concat(":&nbsp;");
    document.getElementById("type_box").style.display = "initial";
    setTimeout(timer, 400);
}

function timer() {
    pull();
}

function update() {
    var chunk = "Users online: ".concat(users,"<br><br>");
    if (msgs.length >= 1) {
        chunk = chunk.concat(robust(msgs[0]));
    }
    for (var i = 1; i<msgs.length; i++) {
        chunk = chunk.concat("<br>",robust(msgs[i]));
    }
    var peek_box = robust(peeked).concat("<br>");
    if (who_last=="us") {
        document.getElementById("below").innerHTML=peek_box;
    } else {
        chunk = chunk.concat("<br>",peek_box);
        document.getElementById("below").innerHTML="";
    }
    document.getElementById("history").innerHTML=chunk;
}

function push() {
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "push", true);
    xhttp.send(user_name.concat(document.getElementById("type_box").value));
}

function leak() {
    who_last = "us";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "leak", true);
    xhttp.send(user_name.concat(document.getElementById("type_box").value));
}

function pull() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            setTimeout(timer, 40);
            if (this.status == 200) {
                var head = this.responseText.substring(0, 5);
                var content = this.responseText.substring(5);
                if (head == "QUIET") {
                    users = content;
                } else if (head == "MSG__") {
                    msgs.push(content);
                } else if (head == "PEEK_") {
                    peeked = content;
                    who_last = "them";
                } else {
                    alert("Error: bad head: ".concat(head));
                }
                update();
            } else {
                close();
            }
        }
    };
    xhttp.open("POST", "pull", true);
    xhttp.send(user_name);
}
</script>
