let studying = false;

function startTimer() {
  fetch("http://localhost:5000/start", { method: "POST" });
}

function stopTimer() {
  fetch("http://localhost:5000/stop", { method: "POST" });
}

chrome.tabs.onActivated.addListener(async (info) => {
  const tab = await chrome.tabs.get(info.tabId);
  handleTab(tab);
});

chrome.tabs.onUpdated.addListener((id, change, tab) => {
  handleTab(tab);
});

function handleTab(tab) {
  if (!tab.url) return;

  const isPW =
    tab.url.includes("physicswallah") ||
    tab.url.includes("pw.live");

  if (isPW && !studying) {
    studying = true;
    startTimer();
  }

  if (!isPW && studying) {
    studying = false;
    stopTimer();
  }
}
