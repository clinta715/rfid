// Configuration
const DEFAULT_RFID_URL = 'http://localhost:8000';
const ELEMENT_IDS = ['pid', 'sid', 'bar'];

// Helper functions
function getElement(id) {
    const element = document.getElementById(id);
    if (!element) {
        console.error(`Element with id "${id}" not found`);
    }
    return element;
}

function setElementValue(id, value) {
    const element = getElement(id);
    if (element) {
        element.value = value;
    }
}

function getElementValue(id) {
    const element = getElement(id);
    return element ? element.value : '';
}

async function getStorageItem(key) {
    return new Promise((resolve) => {
        chrome.storage.local.get([key], (result) => {
            resolve(result[key]);
        });
    });
}

function sendMessage(message) {
    return new Promise((resolve, reject) => {
        chrome.runtime.sendMessage(message, (response) => {
            if (chrome.runtime.lastError) {
                reject(chrome.runtime.lastError);
            } else {
                resolve(response);
            }
        });
    });
}

// Main functions
async function updater(request) {
    try {
        if (request) {
            ELEMENT_IDS.forEach(id => setElementValue(id, request[id]));
        } else {
            const values = await Promise.all(ELEMENT_IDS.map(id => getStorageItem(id)));
            ELEMENT_IDS.forEach((id, index) => setElementValue(id, values[index]));
        }
    } catch (error) {
        console.error('Error in updater:', error);
    }
}

async function handleReadButtonClick() {
    try {
        await sendMessage({
            sid: "0000",
            pid: "0000",
            bar: "000000000000",
            command: "read",
            rfidurl: DEFAULT_RFID_URL
        });
    } catch (error) {
        console.error('Error sending read message:', error);
    }
}

async function handleWriteButtonClick() {
    try {
        const message = {
            sid: getElementValue('sid'),
            pid: getElementValue('pid'),
            bar: getElementValue('bar'),
            command: "write",
            rfidurl: DEFAULT_RFID_URL
        };
        await sendMessage(message);
    } catch (error) {
        console.error('Error sending write message:', error);
    }
}

// Event listeners
window.addEventListener('load', updater);

chrome.runtime.onMessage.addListener((request, sender) => {
    updater(request);
    return true; // Keeps the message channel open for asynchronous responses
});

chrome.storage.onChanged.addListener((changes, area) => {
    if (area === "local" && "sid" in changes) {
        updater();
    }
});

// Initialize UI elements
document.addEventListener('DOMContentLoaded', () => {
    const readButton = getElement('rfidread');
    if (readButton) {
        readButton.addEventListener('click', handleReadButtonClick);
    }

    const writeButton = getElement('rfidwrite');
    if (writeButton) {
        writeButton.addEventListener('click', handleWriteButtonClick);
    }
});
