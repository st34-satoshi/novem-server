var PLAYER_TYPE = "Viewer";  // Row, Column, or Viewer
var ROOM_ID = "";

function buttonClick(d, n){
    // Row or Column is selected
    console.log("selected " + d+n);
    if (PLAYER_TYPE == "Viewer"){
        return
    }
    if (PLAYER_TYPE == "Row" && d=="c"){
        return
    }
    if (PLAYER_TYPE == "Column" && d=="r"){
        return
    }
    // send the action to the server
    actionRequest(d+n, ROOM_ID);
    // display waiting view
    document.getElementById("waiting").style.display = "block";
}

function makeRoomList(data){
  console.log("make a room list!!");
  var room_list = document.getElementById("room_list");
  var join_room_select = document.getElementById("join-room-id");
  // room_list.remove();  // reset
  for (var room_id in data){
    if (room_id == "action"){
      continue;
    }
    // add room list
    var li = document.createElement("li");
    var text = "";
    for (var element in data[room_id]){
      text += element + "=" + data[room_id][element] + ", ";
    }
    li.appendChild(document.createTextNode(text));
    room_list.appendChild(li);

    // add join a room options
    var id_option = document.createElement("option");
    id_option.text = room_id;
    id_option.value = room_id;
    join_room_select.appendChild(id_option);
  }
}

function drawTile(tdId, bottom, top){
  document.getElementById(tdId).innerHTML = ""; // reset
  var svg = d3.select("#"+tdId)
              .append("svg")
              .attr("width", 100)
              .attr("height", 100);
  // console.log(svg);
  if(bottom == 0){
    // do nothing. no tile
  } else if (top == 0){
    // only 1 tile.
    svg.append("rect")
      .attr("x", 20)
      .attr("y", 20)
      .attr("rx", 10)  // 丸角にする
      .attr("ry", 10)
      .attr("fill", "white")
      .attr("stroke", "black")
      .attr("width", 60)
      .attr("height", 60);
    svg.append("text")
      .attr("x", 35)
      .attr("y", 65)
      .attr("stroke", "black")
      .attr("font-size", 40)
      .text(bottom);
  }else{
    // 2 tiles.
    // d3.select("#"+tdId).append("svg").attr("width", 100).attr("height", 100)
    svg.append("rect")
      .attr("x", 25)
      .attr("y", 15)
      .attr("rx", 10)  // 丸角にする
      .attr("ry", 10)
      .attr("fill", "white")
      .attr("stroke", "black")
      .attr("width", 60)
      .attr("height", 60);
    svg.append("rect")
      .attr("x", 15)
      .attr("y", 25)
      .attr("rx", 10)  // 丸角にする
      .attr("ry", 10)
      .attr("fill", "white")
      .attr("stroke", "black")
      .attr("width", 60)
      .attr("height", 60);
    svg.append("text")
      .attr("x", 30)
      .attr("y", 70)
      .attr("stroke", "black")
      .attr("font-size", 40)
      .text(top);
  }
}

function switchToPlayingView(data){
  document.getElementById("playing-view").style.display ="block";
  document.getElementById("home-view").style.display ="none";

  // set the board
  bottom_board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
  top_board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
  var board = data["board"];
  for (var c in board){
    if (c < 9){  // bottom
      bottom_board[c/3|0][c%3] = board[c]
    }else{
      top_board[(c-9)/3|0][c%3] = board[c]
    }
  }
  // draw the board
  for (let i=0;i<3;i++){
    for(let j=0;j<3;j++){
      cell_id = "cell" + i + j;
      drawTile(cell_id, bottom_board[i][j], top_board[i][j]);
    }
  }

  // set room id
  const playing_room_id = document.getElementById("playing-room-id");
  playing_room_id.innerHTML = "Room ID " + data["room_id"];
  // set player
  const player_type = document.getElementById("playing-type");
  player_type.innerHTML = "You are " + data["type"];
  // set Row or Column
  const player_rc = document.getElementById("playing-rc");
  if (data["type"] == "Row" || data["type"] == "Column"){
    player_rc.innerHTML = "<strong>Select a " + data["type"] + "</strong>";
  }else{
    player_rc.style.display = "none";
  }
  // set round and turn
  const playing_round = document.getElementById("playing-round");
  var round = data["round"];
  playing_round.innerHTML = "Round: " + round;
  const playing_turn = document.getElementById("playing-turn");
  if((data["type"] == "Row" && round%2 == 0) || (data["type"] == "Column" && round%2 == 1)){
    playing_turn.innerHTML = "You are Attacking";
  }else{
    playing_turn.innerHTML = "You are Defending";
  }
  if(data["type"] == "Viewer"){
    if (round % 2 ==0){
      playing_turn.innerHTML = "Row is Attacking";
    }else{
      playing_turn.innerHTML = "Row is Attacking";
    }
  }
  // set point
  const point_r = document.getElementById("point-r");
  point_r.innerHTML = "Row point: " + data["row_point"];
  const point_c = document.getElementById("point-c");
  point_c.innerHTML = "Column point: " + data["column_point"];
  
  // waiting
  document.getElementById("waiting").style.display = "none";

  // set global variable
  PLAYER_TYPE = data["type"];
  ROOM_ID = data["room_id"];
}

// websocket
var websocket = new WebSocket("ws://153.126.167.150:443/");
// var websocket = new WebSocket("ws://127.0.0.1:8080/");  // local

// send messages
function makeRoomRequest() {
  console.log("make a room button is clicked");
  const player_name = document.getElementById("player-name").value;
  const player_type = document.getElementById("player-type").value;
  const player_handicap = document.getElementById("player-handicap").value;
  websocket.send(JSON.stringify({action: "make-room", name: player_name, player_type: player_type, handicap: player_handicap}));
}
function joinRoomRequest() {
    console.log("join the room button is clicked");
    const room_id = document.getElementById("join-room-id").value;
    const player_name = document.getElementById("join-player-name").value;
    const player_type = document.getElementById("join-player-type").value;
    websocket.send(JSON.stringify({action: "join-room", name: player_name, player_type: player_type, room_id: room_id}));
}
function actionRequest(action, room_id) {
    websocket.send(JSON.stringify({action: "play-action", play_action: action, room_id: room_id}));
}

// receive messages
websocket.onmessage = function (event) {
    data = JSON.parse(event.data);
    console.log("receive data. " + data);
    console.log(data);
    switch (data.action) {
        case 'playing':
          console.log("playing");
          switchToPlayingView(data);
          break;
        case 'room_list':
          console.log("receive room list");
          makeRoomList(data);
          break
        default:
          // console.log("unsupported event", data);
          console.error("unsupported event", data);
    }
};
