function updater(request) {
	if(request) {
		pid = document.getElementById("pid");
		sid = document.getElementById("sid");
		bar = document.getElementById("bar");
	
		pid.setAttribute("value", request.pid);
		sid.setAttribute("value", request.sid);
		bar.setAttribute("value", request.bar);
	} else {
		chrome.storage.local.get(["pid"], function(result) {
			pid.setAttribute("value", result.pid);
		});
	
		chrome.storage.local.get(["sid"], function(result) {
			sid.setAttribute("value", result.sid);
		});
	
		chrome.storage.local.get(["bar"], function(result) {
			bar.setAttribute("value", result.bar);
		});
	};
};

window.addEventListener('load', (event) => {
	updater();
});

readbutton = document.getElementById("rfidread");
readbutton.onclick = function(element) {
	var url = "http://localhost:8000";
	
	chrome.extension.sendMessage({sid: "0000", pid: "0000", bar: "000000000000", command: "read", rfidurl: url });
};

writebutton = document.getElementById("rfidwrite");
writebutton.onclick = function(element) {
	var url = "http://localhost:8000";
		
	let pidvalue = document.getElementById("pid");
	let sidvalue = document.getElementById("sid");
	let barvalue = document.getElementById("bar");
		
	chrome.extension.sendMessage({sid: sidvalue.value, pid: pidvalue.value, bar: barvalue.value, command: "write", rfidurl: url });
};			

chrome.extension.onMessage.addListener(
	function(request, sender) {
		updater( {sid: request.sid, pid:request.pid, bar:request.bar,command:request.command,rfidurl:request.rfidurl}, sender );
});

chrome.storage.onChanged.addListener(function(changes, area) {
    if (area == "local" && "sid" in changes) {
        updater();
    };
});