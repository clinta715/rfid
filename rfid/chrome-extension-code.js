// Configuration
const EXTENSION_ID = 'ncaahfhclojalfgeiopbamlalgjhclok';
const ALLOWED_COMMANDS = ['read', 'update', 'write'];

// Helper functions
function isValidMessage(data) {
    return data && 
           typeof data === 'object' &&
           typeof data.command === 'string' &&
           ALLOWED_COMMANDS.includes(data.command) &&
           typeof data.sid === 'string' &&
           typeof data.pid === 'string' &&
           typeof data.bar === 'string' &&
           typeof data.rfidurl === 'string';
}

function createMessage(data) {
    return {
        sid: data.sid,
        pid: data.pid,
        bar: data.bar,
        command: data.command,
        rfidurl: data.rfidurl
    };
}

// Main functions
function updater(requestData, sender) {
    try {
        if (!isValidMessage(requestData)) {
            throw new Error('Invalid message format');
        }
        window.postMessage(createMessage(requestData), window.origin);
    } catch (error) {
        console.error('Error in updater:', error);
    }
}

function handleWindowMessage(event) {
    try {
        if (event.source !== window) {
            return;
        }
        
        if (!isValidMessage(event.data)) {
            throw new Error('Invalid message format');
        }

        chrome.runtime.sendMessage(EXTENSION_ID, createMessage(event.data), response => {
            if (chrome.runtime.lastError) {
                throw new Error(`Chrome runtime error: ${chrome.runtime.lastError.message}`);
            }
            console.log('Message sent successfully:', response);
        });
    } catch (error) {
        console.error('Error in handleWindowMessage:', error);
    }
}

function handleChromeMessage(request, sender, sendResponse) {
    try {
        if (!isValidMessage(request)) {
            throw new Error('Invalid message format');
        }
        updater(createMessage(request), sender);
        sendResponse({success: true});
    } catch (error) {
        console.error('Error in handleChromeMessage:', error);
        sendResponse({success: false, error: error.message});
    }
}

// Event listeners
window.addEventListener('message', handleWindowMessage);
chrome.runtime.onMessage.addListener(handleChromeMessage);
