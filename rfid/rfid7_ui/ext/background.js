chrome.runtime.onInstalled.addListener(function() {
	// initialize these variables with some zeros for fun
	chrome.storage.local.set({"pid": "SCAN"}, function() {
		console.log("The pid is SCAN");
    });
	chrome.storage.local.set({"sid": "SCAN"}, function() {
		console.log("The sid is 000000000000");
    });
	chrome.storage.local.set({"bar": "SCAN........"}, function() {
		console.log("The bar is 000000000000");
    });
	
	chrome.declarativeContent.onPageChanged.removeRules(undefined, function() {
      chrome.declarativeContent.onPageChanged.addRules([{
        conditions: [new chrome.declarativeContent.PageStateMatcher({
			// this will need to be updated to dairylandlabs.com etc
			pageUrl: {hostEquals: "104.154.157.222:8080"},
        })
        ],
			// activate icon
			actions: [new chrome.declarativeContent.ShowPageAction()]
      }]);
    });
});

// format of all requests used internally is
// sid: 4 digit sample ID value
// pid: 4 digit product ID value 
// bar: 12 digit barcode value
// command: one of three commands, "read", "write" and "update", the idea behind "update" is just to re-output
// 		the information from the last tag w/o forcing a actual read operation
// rfidurl: the URL to send the GET request to to get the JSON formatted request, usually this would be
//		localhost:8000, but this could be a remote machine etc

function rfidhandler(request, sender) { {
    if (request.command == "read") {
		let xhr = new XMLHttpRequest();

		xhr.open("GET", request.rfidurl);
		xhr.setRequestHeader("Content-Type", "application/json");
		xhr.send();
  
		xhr.onreadystatechange = (e) => {
			if (xhr.readyState == 4 && (xhr.status == 200)) {
				var Data = JSON.parse(xhr.responseText);
		
				chrome.storage.local.set( {"sid": Data.sid}, function(sidinputvalue) {
					console.log("The sid is set", sidinputvalue);
				});
  
				chrome.storage.local.set( {"pid": Data.pid}, function(pidinputvalue) {
					console.log("The pid is set", pidinputvalue);
				});

				chrome.storage.local.set( {"bar": Data.bar}, function(barinputvalue) {
					console.log("The bar is set", barinputvalue);
				});
						
				chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
					chrome.tabs.sendMessage(tabs[0].id, {sid:Data.sid, pid:Data.pid, command:Data.command, rfidurl:Data.rfidurl, bar:Data.bar} );
				});
			} else console.log("not ready yet");      
		};
		console.log(xhr.responseText);
	};
		
	if (request.command == "write") {
		var rfiddata = { "sid" : request.sid, "pid" : request.pid, "bar" : request.bar };              // request.sid  request.pid  request.bar 
		rfidjson = JSON.stringify( rfiddata );
  
		let xhr = new XMLHttpRequest();
		xhr.open("POST", rfidurl, true);
  
		xhr.onreadystatechange = function () { 
			if (xhr.readyState === 4 && xhr.status === 200) { 
				// Print received data from server 
				console.log(this.responseText); 
			};
		}; 
		
		chrome.storage.local.set( {"sid": request.sid}, function(sidinputvalue) {
			console.log("The sid is set", sidinputvalue);
		});
		
		chrome.storage.local.set( {"pid": request.pid}, function(pidinputvalue) {
			console.log("The pid is set", pidinputvalue);
		});
		
		chrome.storage.local.set( {"bar": request.bar}, function(barinputvalue) {
			console.log("The bar is set", barinputvalue);
		});
			
		xhr.setRequestHeader("Content-Type", "application/json");
		xhr.send(rfidjson);
	};
}};

chrome.extension.onMessage.addListener(
	function(request, sender) {
		rfidhandler( {sid: request.sid, pid:request.pid, bar:request.bar,command:request.command,rfidurl:request.rfidurl}, sender );
});
