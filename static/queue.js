const slider = document.getElementById('myRange');
const progressBar = document.getElementById('progressBar');
let isDown = false;
let audio = new Audio("data:audio/wav;base64,");
let masterPlay = document.getElementById("masterPlay");
let song_name = document.getElementsByClassName('name_song');
let song_artist = document.getElementsByClassName('song_artist');
let img = document.getElementsByClassName('img');
let lyrics = document.getElementsByClassName('lyrics');


const playalbum = (album_name)=>{
  let album_request = new XMLHttpRequest();
  masterPlay.classList.replace('fa-pause','fa-play');
  album_request.onreadystatechange = function(){
    if(this.status == 200 && this.readyState == 4){
      let queue = JSON.parse(this.responseText)['songs'];
      for(let song=0;song<queue.length-1;song++){
        let temp = queue[song];
        delete temp['song'];
        delete temp['img'];
        if(sessionStorage.getItem('queue') != null){
          let temp_queue = JSON.parse(sessionStorage.getItem("queue"));
          temp_queue.push(temp)
          sessionStorage.setItem('queue',JSON.stringify(temp_queue));
        }
        else{
          let temp_queue = [] 
          temp_queue.push(temp)
          sessionStorage.setItem('queue',JSON.stringify(temp_queue));
        }
      }
      masterPlay.classList.replace('fa-play','fa-pause');
      let temp_queue = queue[queue.length-1];
      audio.src = ("data:audio/wav;base64," + temp_queue['song']);
      audio.currentTime = 0;
      audio.play();
      delete temp_queue['song'];
      setdata_in_nav(temp_queue);
      delete temp_queue['img'];
      audio.currentTime = 0;
      audio.play();
      console.log('ok')
    }
  }
  let request = "/album_details/"+album_name;
  album_request.open('GET',request,true);
  album_request.send();
}


const playsong = (element)=>{
  var xhttp = new XMLHttpRequest();
  var queue = "";
  masterPlay.classList.replace('fa-pause','fa-play');
  xhttp.onreadystatechange = function(){
      if(this.readyState == 4 &&  this.status == 200){
        console.log(queue)
        queue = JSON.parse(this.responseText);
        audio.src = ("data:audio/wav;base64," + queue['song']);
        setdata_in_nav(queue);
        delete queue['song'];
        delete queue['img'];
        audio.currentTime = 0;
        audio.play();
        masterPlay.classList.replace('fa-play','fa-pause');
        if(sessionStorage.getItem('queue') != null){
          let temp_queue = JSON.parse(sessionStorage.getItem("queue"));
          temp_queue.push(queue)
          sessionStorage.setItem('queue',JSON.stringify(temp_queue));
        }
        else{
          let temp_queue = [] 
          temp_queue.push(queue)
          sessionStorage.setItem('queue',JSON.stringify(temp_queue));
        }
      }
    }
    let request = '/add_song_queue/'+(element.childNodes[1].childNodes[0].childNodes[0].childNodes[0].nodeValue);
    xhttp.open('GET',request,true);
    xhttp.send(); 
  }
  
  audio.onended = ()=>{
    masterPlay.classList.replace('fa-pause','fa-play');
    audio.currentTime = 0;
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function(){
      if(this.readyState == 4 &&  this.status == 200){
        let queue = JSON.parse(this.responseText);
      audio.src = ("data:audio/wav;base64," + queue['song']);
      audio.play();
      setdata_in_nav(queue);
      masterPlay.classList.replace('fa-play','fa-pause');
      delete queue['song'];
      delete queue['img'];
      console.log(queue)
    }
  }
  var queue_list = JSON.parse(sessionStorage.getItem('queue'));
  if (queue_list.length != 1){
    queue_list.pop();
    let request = '/add_song_queue/'+queue_list[queue_list.length-1]['name'];
    sessionStorage.setItem('queue',JSON.stringify(queue_list));
    xhttp.open('GET',request,true);
    xhttp.send(); 
  }
  else{
    queue_list.pop();
    sessionStorage.setItem('queue',JSON.stringify([]));
    console.log('empty queue')
  }
}

const setdata_in_nav = (queue)=>{
    for (const iterator of song_name) {
        iterator.innerHTML = queue['name'];
    }
    for (const iterator of song_artist) {
        iterator.innerHTML = queue['artist'];
    }
    for (const iterator of lyrics) {
        iterator.innerHTML = queue['lyrics'];
    }
    for (const iterator of img) {
      iterator.src = "data:image/jpg;base64,"+ queue['img'];
    }
}

slider.addEventListener('mousedown', (e) => {
    isDown = true;
    updateProgressBar(e);
});

slider.addEventListener('mouseup', () => {
    isDown = false;
});

slider.addEventListener('mousemove', (e) => {
  if (isDown) {
    updateProgressBar(e);
  }
});

function updateProgressBar(event) {
  const sliderRect = slider.getBoundingClientRect();
  const percentage = (event.clientX - sliderRect.left) / slider.offsetWidth * 100;
  const clampedPercentage = Math.min(100, Math.max(0, percentage+1));
  progressBar.style.width = `${clampedPercentage}%`;
  audio.currentTime = clampedPercentage*audio.duration/100;
}

masterPlay.addEventListener("click",()=>{
  if(audio.paused || audio.currentTime<=0){
    audio.play();
    masterPlay.classList.replace('fa-play','fa-pause');
  }
  else{
    audio.pause();
    masterPlay.classList.replace('fa-pause','fa-play');
  }
})
audio.addEventListener("timeupdate",()=>{
  let progressValue = parseInt((audio.currentTime/audio.duration)*100);
  progressBar.style.width = `${progressValue}%`;
  console.log(progressValue);
});

function toggleCollapse() {
  var collapsible = document.getElementById('collapseExample');
      collapsible.classList.toggle('collapsed');
}