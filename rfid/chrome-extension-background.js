// Configuration
const DEFAULT_RFID_URL = 'http://localhost:8000';
const ALLOWED_COMMANDS = ['read', 'write', 'update'];
const INITIAL_VALUES = {
    pid: 'SCAN',
    sid: 'SCAN',
    bar: 'SCAN........'
};

// Helper functions
function isValidRequest(request) {
    return request &&
           typeof request === 'object' &&
           typeof request.command === 'string' &&
           ALLOWED_COMMANDS.includes(request.command) &&
           typeof request.sid === 'string' &&
           typeof request.pid === 'string' &&
           typeof request.bar === 'string' &&
           typeof request.rfidurl === 'string';
}

function logStorageSet(key, value) {
    console.log(`The ${key} is set to ${value}`);
}

function setStorageItem(key, value) {
    return new Promise((resolve, reject) => {
        chrome.storage.local.set({ [key]: value }, () => {
            if (chrome.runtime.lastError) {
                reject(chrome.runtime.lastError);
            } else {
                logStorageSet(key, value);
                resolve();
            }
        });
    });
}

function sendMessageToActiveTab(message) {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        if (tabs[0]) {
            chrome.tabs.sendMessage(tabs[0].id, message);
        }
    });
}

// Main functions
function handleInstallation() {
    Object.entries(INITIAL_VALUES).forEach(([key, value]) => {
        setStorageItem(key, value);
    });

    chrome.declarativeContent.onPageChanged.removeRules(undefined, function() {
        chrome.declarativeContent.onPageChanged.addRules([{
            conditions: [new chrome.declarativeContent.PageStateMatcher({
                pageUrl: {hostEquals: "104.154.157.222:8080"}, // Update this as needed
            })],
            actions: [new chrome.declarativeContent.ShowPageAction()]
        }]);
    });
}

async function handleReadCommand(request) {
    try {
        const response = await fetch(request.rfidurl);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        await Promise.all([
            setStorageItem('sid', data.sid),
            setStorageItem('pid', data.pid),
            setStorageItem('bar', data.bar)
        ]);

        sendMessageToActiveTab({
            sid: data.sid,
            pid: data.pid,
            command: data.command,
            rfidurl: data.rfidurl,
            bar: data.bar
        });
    } catch (error) {
        console.error('Error in read command:', error);
    }
}

async function handleWriteCommand(request) {
    try {
        const rfidData = {
            sid: request.sid,
            pid: request.pid,
            bar: request.bar
        };

        const response = await fetch(request.rfidurl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(rfidData),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const responseData = await response.text();
        console.log('Server response:', responseData);

        await Promise.all([
            setStorageItem('sid', request.sid),
            setStorageItem('pid', request.pid),
            setStorageItem('bar', request.bar)
        ]);
    } catch (error) {
        console.error('Error in write command:', error);
    }
}

function rfidHandler(request, sender) {
    if (!isValidRequest(request)) {
        console.error('Invalid request format:', request);
        return;
    }

    switch (request.command) {
        case 'read':
            handleReadCommand(request);
            break;
        case 'write':
            handleWriteCommand(request);
            break;
        case 'update':
            // Implement update logic if needed
            console.log('Update command received');
            break;
        default:
            console.error('Unknown command:', request.command);
    }
}

// Event listeners
chrome.runtime.onInstalled.addListener(handleInstallation);

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    rfidHandler(request, sender);
    sendResponse({success: true}); // Always send a response
    return true; // Indicates that the response is sent asynchronously
});
