function updater(requestData, sender) {
	window.postMessage({
		sid: requestData.sid,
		pid: requestData.pid,
		bar: requestData.bar,
		command: requestData.command,
		rfidurl: requestData.rfidurl }
	);
};

window.addEventListener("message", function(event) {
	if (event.source != window){
		return;
    };
	
	if( event.data.command == "read" || event.data.command == "update" || event.data.command == "write" ) {
		chrome.runtime.sendMessage( "ncaahfhclojalfgeiopbamlalgjhclok", { 
			sid: event.data.sid,
			pid: event.data.pid,
			bar: event.data.bar,
			command: event.data.command,
			rfidurl: event.data.rfidurl
		});
	};
});

chrome.runtime.onMessage.addListener(
	function(request) {
		updater( {sid: request.sid, pid:request.pid, bar:request.bar,command:request.command,rfidurl:request.rfidurl} );
});
