chrome.action.onClicked.addListener(async tab => {
    const uuid = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['scripts/content.js']
    });
    // open new tab
});