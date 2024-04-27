var participants = { participants: [] };
var socket;

var blocked = [];

async function fetchBlocked() {
  try {
    const response = await fetch(`/api/blocked/`);
    if (!response.ok) {
      throw new Error("Failed to fetch blocked users");
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching blocked users:", error);
    return [];
  }
}

function startChatSocket(chatId) {
  if (socket) socket.close();
  socket = new WebSocket(
    "wss://" + window.location.host + "/ws/chat/" + chatId + "/"
  );
  socket.addEventListener("open", function (event) {
    console.log("WebSocket connection established.");
  });

  socket.addEventListener("error", function (event) {
    console.error("WebSocket error:", event);
  });

  socket.addEventListener("message", function (event) {
    const message = JSON.parse(event.data);
    renderMessage(message);
  });
}

function selectChat(chatName, chatId, is_personal) {
  document.querySelector(".selected-user").textContent =
    "Chatting with: " + chatName;
  if (is_personal)
    document.querySelector(".selected-user").textContent = "Game Invitations";
  document.getElementById("messages").innerHTML = "";
  open_chat(chatId);
}

// Function that take the url and make it a button
function linkify(inputText) {
  var replacePattern1;

  replacePattern1 = /(\b(https?|ftp):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/gim;
  var replacedText = inputText.replace(replacePattern1, function (url) {
    if (url[8] == "/") {
      url = url.slice(0, 8) + window.location.host + url.slice(8);
    }
    return (
      '<button class="join-game-button" onclick="window.location.href=\'' +
      url +
      "';\">Join the Game</button>"
    );
  });

  return replacedText;
}

async function renderMessage(message) {
  var messageBox = document.createElement("div");
  messageBox.style.display = "flex";
  messageBox.style.alignItems = "center";

  var usernameElement = document.createElement("span");
  usernameElement.textContent = message.username + ": ";
  usernameElement.style.fontWeight = "bold";
  usernameElement.style.fontFamily = "'Poppins', sans-serif";
  usernameElement.style.marginRight = "5px";
  messageBox.appendChild(usernameElement);

  if (message.message) {
    const messageElement = document.createElement("div");
    messageElement.innerHTML = linkify(message.message); // Convert text urls to clickable links
    messageBox.appendChild(messageElement);
    for (user in blocked) {
      if (blocked[user].username == message.username)
        messageElement.innerHTML = "BLOCKED";
    }
    if (await fetchBlockStatus(message.username))
      messageElement.innerHTML = "BLOCKED";
    messageElement.classList.add("message-box");
    messageBox.appendChild(messageElement);
  }
  if (message.image) {
    const img = document.createElement("img");
    img.src = message.image;
    img.classList.add("image");
    img.classList.add("message-box");
    messageBox.appendChild(img);
  }
  document.getElementById("messages").appendChild(messageBox);
  scrollToBottom();
}

async function fetchBlockStatus(username) {
  try {
    const response = await fetch(`/api/is_blocked/` + username);
    if (!response.ok) {
      throw new Error("Failed to fetch status");
    }
    const data = await response.json();

    return data;
  } catch (error) {
    console.error("Error fetching status:", error);
    return false;
  }
}

async function fetchChats() {
  try {
    const response = await fetch(`/api/chat/`);
    if (!response.ok) {
      throw new Error("Failed to fetch chats");
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching messages:", error);
    return [];
  }
}

async function fetchMessages(chatId) {
  try {
    const response = await fetch(`/api/messages/${chatId}/`);
    if (!response.ok) {
      throw new Error("Failed to fetch messages");
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching messages:", error);
    return [];
  }
}

function load_chats() {
  fetchChats().then((chats) => {
    const userList = document.getElementById("userList");
    userList.innerHTML = ""; // Effacer le contenu existant
    for (const chat of chats) {
      let usernames = chat.participants
        .map((participant) => participant.username)
        .join(", ");
      if (chat.is_personal) usernames = "Game Invitations"; // Nom spécial pour les chats personnels

      const userDiv = document.createElement("div");
      userDiv.classList.add("user");
      if (chat.is_personal) {
        userDiv.classList.add("game-invitation"); // Ajouter une classe spécifique pour les invitations de jeu
      }
      userDiv.textContent = usernames;
      userDiv.addEventListener("click", () =>
        selectChat(usernames, chat.id, chat.is_personal)
      );
      userList.appendChild(userDiv);
    }
  });
}

async function renderMessagesInOrder(messages) {
  for (const mess of messages) {
    await renderMessage({
      message: mess.content,
      username: mess.sender,
      image: mess.image,
    });
  }
}

function open_chat(chatId) {
  fetchMessages(chatId).then((messages) => {
    renderMessagesInOrder(messages);
  });
  startChatSocket(chatId);
}

function scrollToBottom() {
  const messagesContainer = document.getElementById("messages");
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

document.getElementById("sendMessage").addEventListener("click", sendMessage);

function sendMessage() {
  if (!socket) return;
  const messageText = document.getElementById("messageText").value.trim();
  const imageData = document.getElementById("imageData").value;

  if (messageText !== "") socket.send(JSON.stringify({ message: messageText }));
  if (imageData !== "") socket.send(JSON.stringify({ image: imageData }));
  document.getElementById("messageText").value = "";
  document.getElementById("imageData").value = "";
  document.getElementById("imagePreview").innerHTML = "";
}

fetchBlocked().then((data) => {
  blocked = data;
  load_chats();
});

// Pour les tests

/*simulateGameInvitation();

function simulateGameInvitation() {
  // Créer un faux message d'invitation à un jeu
  var fakeMessage = {
      username: "System",
      message: "Join the game now! https://youtube.com"
  };

  // Appeler renderMessage pour afficher le message dans le chat
  renderMessage(fakeMessage);
}*/

document
  .getElementById("messageText")
  .addEventListener("keypress", function (event) {
    scrollToBottom();
    if (event.key === "Enter") {
      event.preventDefault();
      sendMessage();
    }
  });

document
  .getElementById("messageText")
  .addEventListener("paste", function (event) {
    const clipboardData = event.clipboardData || window.clipboardData;

    for (const item of clipboardData.items) {
      if (item.type.indexOf("image") !== -1) {
        const reader = new FileReader();
        reader.onload = function (event) {
          const imageData = event.target.result;
          const imagePreview = document.getElementById("imagePreview");
          const img = document.createElement("img");
          img.src = imageData;
          imagePreview.innerHTML = "";
          imagePreview.appendChild(img);
          document.getElementById("imageData").value = imageData;
        };
        reader.readAsDataURL(item.getAsFile());
      }
    }
  });

document
  .getElementById("messageText")
  .addEventListener("keypress", function (event) {
    scrollToBottom();
    if (event.key === "Enter") {
      event.preventDefault();
      sendMessage();
    }
  });
