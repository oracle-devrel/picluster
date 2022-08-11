 document.querySelector("button").onclick = function() {
     document.querySelector("#loadingScreen").style.display = "none"
     document.querySelector("#bgSoundtrack").volume = 0.09;
     document.querySelector("#bgSoundtrack").loop = true;
     document.querySelector("#bgSoundtrack").play()
   };