const socket=io();
let myPlayerId=0;
// elements
const playersList=document.getElementById("playersList");
const log=document.getElementById("log");
const chatBox=document.getElementById("chatBox");
const chatInput=document.getElementById("chatInput");
const sendBtn=document.getElementById("sendBtn");
const rollBtn=document.getElementById("rollBtn");
const restartBtn=document.getElementById("restartBtn");
const currentPlayerEl=document.getElementById("currentPlayer");
const lastRollEl=document.getElementById("lastRoll");
const winnerEl=document.getElementById("winner");
const canvas=document.getElementById("boardCanvas");
const ctx=canvas.getContext("2d");

// snakes and ladders data
const snakes={16:6,47:26,49:11,56:53,62:19,64:60,87:24,93:73,95:75,98:78,99:40};
const ladders={2:38,4:25,9:31,21:42,28:84,36:44,51:72,71:91,79:97};

let state=null;

socket.on("state:init",s=>{state=s;renderState();});
socket.on("state:update",s=>{state=s;renderState();});
socket.on("chat:broadcast",msg=>{
  const div=document.createElement("div");
  const player="P"+(msg.pid+1);
  const flag= msg.flag==="warn"?"⚠️ Warning!": msg.flag==="kick"?"❌ Kicked!":"";
  div.textContent=`${player}: ${msg.text} ${flag} [${msg.p.toFixed(2)}]`;
  div.className= msg.flag==="kick"?"toxicity-high": msg.flag==="warn"?"toxicity-warn":"toxicity-ok";
  chatBox.appendChild(div); chatBox.scrollTop=chatBox.scrollHeight;
});

rollBtn.onclick=()=>socket.emit("game:roll");
restartBtn.onclick=()=>socket.emit("game:restart",{names:["P1","P2","P3","P4"]});
const headerRestartBtn=document.getElementById("headerRestartBtn");
if(headerRestartBtn){headerRestartBtn.onclick=()=>socket.emit("game:restart",{names:["P1","P2","P3","P4"]});}

sendBtn.onclick=()=>{
  const text=chatInput.value.trim(); if(!text) return;
  socket.emit("chat:message",{pid:myPlayerId,text});
  chatInput.value="";
};

function renderState(){
  if(!state) return;
  currentPlayerEl.textContent="P"+(state.turn+1);
  // ensure die is between 1 and 6
  let dieVal = state.die_last;
  if(dieVal === null || dieVal === undefined) {
    lastRollEl.textContent = "-";
  } else {
    dieVal = Math.max(1, Math.min(6, dieVal));
    lastRollEl.textContent = dieVal;
  }
  winnerEl.textContent= state.winner_pid!==null?"P"+(state.winner_pid+1):"No winner yet";
  playersList.innerHTML="";
  state.players.forEach((p,i)=>{
    const div=document.createElement("div");
    div.className="player-card"+(i===state.turn?" current":"");
    div.textContent=`${p.name} – pos ${p.position}${p.active?"":" (kicked)"} warnings:${p.warnings}`;
    playersList.appendChild(div);
  });
  drawBoard();
}

function drawBoard(){
  const size=600; const cells=10;
  const cellSize=size/cells;
  ctx.clearRect(0,0,size,size);
  // checkerboard
  for(let r=0;r<cells;r++){
    for(let c=0;c<cells;c++){
      ctx.fillStyle=((r+c)%2===0)?"#fffbdd":"#fff3c0";
      ctx.fillRect(c*cellSize,r*cellSize,cellSize,cellSize);
      ctx.strokeRect(c*cellSize,r*cellSize,cellSize,cellSize);
      let gameRow = cells - 1 - r;
      let num = gameRow * cells + (gameRow % 2 === 0 ? c + 1 : cells - c);
      ctx.fillStyle="#333";ctx.font="12px sans-serif";
      ctx.fillText(num,c*cellSize+4,r*cellSize+12);
    }
  }
  Object.entries(snakes).forEach(([s,e])=>drawArrow(+s,+e,"red"));
  Object.entries(ladders).forEach(([s,e])=>drawLadder(+s,+e));
  if(state) state.players.forEach((p,i)=>{
    const rawPos = p.position;
    // do not draw tokens for players who haven't entered the board (position 0 or negative)
    if (!rawPos || rawPos < 1) return;
    const pos = Math.min(rawPos, 100);
    const row = Math.floor((pos - 1) / 10);
    const col = (row % 2 === 0) ? (pos - 1) % 10 : 9 - ((pos - 1) % 10);
    const x = col * cellSize + cellSize/2 + (i-1.5)*8;
    const y = (9 - row) * cellSize + cellSize/2;
    ctx.beginPath();
    ctx.arc(x, y, 8, 0, 2 * Math.PI);
    ctx.fillStyle=["red","blue","green","purple"][i];
    ctx.fill();
  });
}

function cellCenter(n){
  const cells=10; const size=600; const cellSize=size/cells;
  let row=Math.floor((n-1)/cells);
  let col=(row%2===0)?(n-1)%cells:cells-1-((n-1)%cells);
  return{ x: col*cellSize + cellSize/2, y: (cells-1-row)*cellSize + cellSize/2 };
}

function drawArrow(a,b,color){
  const p1=cellCenter(a); const p2=cellCenter(b);
  ctx.strokeStyle=color; ctx.lineWidth=3; ctx.beginPath();
  ctx.moveTo(p1.x,p1.y); ctx.lineTo(p2.x,p2.y); ctx.stroke();
  const ang=Math.atan2(p2.y-p1.y,p2.x-p1.x);
  const headlen=10;
  ctx.beginPath();
  ctx.moveTo(p2.x,p2.y);
  ctx.lineTo(p2.x-headlen*Math.cos(ang-Math.PI/6),p2.y-headlen*Math.sin(ang-Math.PI/6));
  ctx.lineTo(p2.x-headlen*Math.cos(ang+Math.PI/6),p2.y-headlen*Math.sin(ang+Math.PI/6));
  ctx.lineTo(p2.x,p2.y);
  ctx.fillStyle=color; ctx.fill();
}

function drawLadder(a,b){
  const p1=cellCenter(a); const p2=cellCenter(b);
  ctx.strokeStyle="green"; ctx.lineWidth=4;
  ctx.beginPath(); ctx.moveTo(p1.x-5,p1.y); ctx.lineTo(p2.x-5,p2.y); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(p1.x+5,p1.y); ctx.lineTo(p2.x+5,p2.y); ctx.stroke();
  const steps=Math.floor(Math.hypot(p2.x-p1.x,p2.y-p1.y)/20);
  for(let i=1;i<steps;i++){
    let fx=p1.x + (p2.x-p1.x)*(i/steps);
    let fy=p1.y + (p2.y-p1.y)*(i/steps);
    ctx.beginPath();
    ctx.moveTo(fx-5,fy); ctx.lineTo(fx+5,fy); ctx.stroke();
  }
}
