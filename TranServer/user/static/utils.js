var websockets = {};

function openWebSocket(url) {
  console.log("Opening websocket");
  const ws = new WebSocket(url);
  ws.onopen = function () {
    console.log("Websocket opened");
  };
  if (websockets[url]) {
    websockets[url].close();
  }
  websockets[url] = ws;
  return ws;
}

function closeAllWebSockets() {
  console.log("Closing all websockets");
  for (const ws of Object.values(websockets)) {
    ws.close();
  }
  websockets = {};
}

async function fetchPage(url) {
  closeAllWebSockets();
  try {
    const response = await fetch(url);
    const html = await response.text();
    await replaceContent(html);
    await loadScriptsFromHTML(html);
  } catch (error) {
    console.error("Error fetching page:", error);
  }
}

function replaceContent(html) {
  return new Promise((resolve, reject) => {
    console.log("html replaced");
    const parsedHTML = new DOMParser().parseFromString(html, "text/html");

    const contentToReplace = parsedHTML.querySelector(
      "#content-container-replace"
    );
    const newHeadElement = document.createElement("head");
    newHeadElement.innerHTML = parsedHTML.head.innerHTML;

    // Find the existing <head> element in the document
    const originalHead = document.querySelector("head");

    // Replace the content of the existing <head> with the content of the new <head>
    originalHead.parentNode.replaceChild(newHeadElement, originalHead);
    document.body.innerHTML = "";
    document.body.appendChild(contentToReplace);
    // document.getElementById('content-container-replace').innerHTML = contentToReplace.innerHTML;
    resolve(); // Resolve the promise after content replacement
  });
}

function loadScript(url) {
  return new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = url;
    script.onload = () => {
      resolve();
    };
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

async function loadScriptsFromHTML(html) {
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, "text/html");
  const scriptTags = doc.querySelectorAll("script");

  const scriptUrls = Array.from(scriptTags)
    .map((scriptTag) => scriptTag.getAttribute("src"))
    .filter((src) => src);

  await Promise.all(scriptUrls.map(loadScript));
}

window.onpopstate = function () {
  closeAllWebSockets();
  const url = window.location.pathname;
  fetchPage(url);
};

document.addEventListener("DOMContentLoaded", function () {
  document.addEventListener("click", function (event) {
    const target = event.target;
    if (target.tagName === "A" && target.getAttribute("href") !== "#") {
      event.preventDefault();
      closeAllWebSockets();
      const url = target.getAttribute("href");
      fetchPage(url);
      history.pushState(null, null, url);
    }
  });
});

function getCookie(name) {
  const cookieValue = document.cookie
    .split(";")
    .find((cookie) => cookie.trim().startsWith(name + "="));
  if (cookieValue) {
    return cookieValue.split("=")[1];
  } else {
    return null;
  }
}
