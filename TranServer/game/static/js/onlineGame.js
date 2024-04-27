var popup = document.querySelector(".popup");
var blurBackground = document.querySelector(".blur-background");

blurBackground.addEventListener("click", function (event) {
  if (event.target === blurBackground) {
    popup.style.display = "none";
    blurBackground.style.display = "none";
  }
});

function openPopup() {
  var popup = document.getElementById("popup");
  popup.style.display = "block";
  document.body.style.overflow = "hidden";
  document.querySelector(".blur-background").style.display = "block";
  fetchFrom("/api/friends/").then((data) => {
    for (friend in data) {
      const username = data[friend].username;
      add_user(username, "user-list", "Invite", "#4CAF50");
    }
  });
}

function closePopup() {
  var popup = document.getElementById("popup");
  popup.style.display = "none";
  document.body.style.overflow = "";
  document.querySelector(".blur-background").style.display = "none";
}

var createButton = document.querySelector(".create-link");

createButton.addEventListener("click", function (event) {
  event.preventDefault();
  if (
    document.getElementById("game-mode").value == "1" ||
    document.getElementById("game-mode").value == "2"
  ) {
    openPopup();
  } else {
    var gameSettings = {
      ballwidth: document.getElementById("ball-size").value,
      planksize: document.getElementById("raquet-size").value,
      Speed: document.getElementById("game-speed").value,
      acceleration: document.getElementById("game-acceleration").value,
      winpoint: document.getElementById("win-point").value,
      gamemode: document.getElementById("game-mode").value,
      participants: [],
    };
    console.log(JSON.stringify(gameSettings));
    fetch("", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify(gameSettings),
    })
      .then((response) => {
        if (!response.ok) throw new Error("Network response was not ok");
        return response.json();
      })
      .then((data) => {
        console.log("Success:", data);
        if (data.gameLink) {
          window.history.pushState(null, null, data.gameLink);
          fetchPage(data.gameLink);
        } else console.error("No game link received from server");
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }
});

function searchUsers() {
  var searchText = document.getElementById("searchInput").value.toLowerCase();
  var users = document.querySelectorAll(".user-item");
  var searchResultDiv = document.getElementById("searchResult");
  searchResultDiv.innerHTML = "";
  searchResultDiv.style.display = "none";
}

document.getElementById("searchInput").addEventListener("input", searchUsers);

document
  .querySelector(".search-container button")
  .addEventListener("click", searchUsers);

function handleInviteButtonClick(event) {
  const userItem = event.target.closest(".user-item");
  const userName = userItem.querySelector(".user-name").textContent;
  const isInvited = event.target.textContent === "Invite";

  event.target.textContent = isInvited ? "✖" : "Invite";
  event.target.style.backgroundColor = isInvited ? "red" : "#4CAF50";

  const targetContainerId = isInvited ? "invitedUsers" : "user-list";
  const targetContainer = document.getElementById(targetContainerId);
  const sourceContainerId = isInvited ? "user-list" : "invitedUsers";
  const sourceContainer = document.getElementById(sourceContainerId);

  const sourceUserItems = sourceContainer.querySelectorAll(".user-item");
  sourceUserItems.forEach(function (item) {
    const itemUserName = item.querySelector(".user-name").textContent;
    if (itemUserName === userName) {
      item.remove();
    }
  });

  targetContainer.appendChild(userItem);

  document.getElementById("searchInput").value = "";
  document.getElementById("searchResult").style.display = "none";
  document.getElementById("searchResult").innerHTML = "";
}

document.querySelectorAll(".invite-button").forEach((button) => {
  button.addEventListener("click", handleInviteButtonClick);
});

blurBackground.addEventListener("click", function () {
  closePopup();
});

var createChatButton = document.querySelector(".start-button");
createChatButton.addEventListener("mousedown", function (event) {
  event.preventDefault();
});

createChatButton.addEventListener("click", function (event) {
  var items = document.querySelectorAll("#invitedUsers .user-item");

  var gameSettings = {
    ballwidth: document.getElementById("ball-size").value,
    planksize: document.getElementById("raquet-size").value,
    Speed: document.getElementById("game-speed").value,
    acceleration: document.getElementById("game-acceleration").value,
    winpoint: document.getElementById("win-point").value,
    gamemode: document.getElementById("game-mode").value,
    participants: [],
  };
  console.log(JSON.stringify(gameSettings));
  items.forEach(function (item) {
    gameSettings.participants.push(
      item.querySelector(".user-name").textContent
    );
  });
  fetch("", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify(gameSettings),
  })
    .then((response) => {
      if (!response.ok) throw new Error("Network response was not ok");
      return response.json();
    })
    .then((data) => {
      console.log("Success:", data);
      if (data.gameLink) {
        window.history.pushState(null, null, data.gameLink);
        fetchPage(data.gameLink);
      } else console.error("No game link received from server");
    })
    .catch((error) => {
      console.error("Error:", error);
    });
  var items = document.querySelectorAll(".user-item");
  items.forEach(function (item) {
    item.remove();
  });
});

async function fetchFrom(link) {
  try {
    const response = await fetch(link);
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

function add_user(username, list, text, color) {
  removeFromInvitedList(username);
  removeFromUserList(username);
  fetch("/api/profile_pic/" + username + "/")
    .then((response) => response.blob())
    .then((blob) => {
      // Convert the blob to a base64 encoded string
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(blob);
      });
    })
    .then((data) => {
      const sourceUserItems = document.querySelectorAll(".user-item");
      sourceUserItems.forEach(function (item) {
        const itemUserName = item.querySelector(".user-name").textContent;
        if (itemUserName === username) {
            item.remove();
        }
      });
      var userItem = document.createElement("div");
      userItem.classList.add("user-item");
      var img = document.createElement("img");
      img.src = data;
      img.alt = username;
      img.classList.add("user-image");
      userItem.appendChild(img);
      var div_username = document.createElement("div");
      div_username.textContent = username;
      div_username.classList.add("user-name");
      userItem.appendChild(div_username);
      var invite_button = document.createElement("button");
      invite_button.textContent = text;
      invite_button.style.backgroundColor = color;
      invite_button.classList.add("invite-button");
      userItem.appendChild(invite_button);
      invite_button.addEventListener("click", handleInviteButtonClick);
      document.getElementById(list).appendChild(userItem);
    });
}

var searchBox = document.getElementById("searchInput");

document
  .getElementById("searchBtn")
  .addEventListener("click", function (event) {
    if (!searchBox.value) return;
    fetch("/api/exist/" + searchBox.value + "/")
      .then((response) => response.json())
      .then((data) => {
        if (data) {
          add_user(searchBox.value, "invitedUsers", "✖", "red");
        } else {
          throw new Error("User does not exist");
        }
      })
      .catch((error) => {
        displayError(error.message || "Error during the user invitation.");
      });
  });

function removeFromUserList(userName) {
  var items = document.querySelectorAll("#user-list .user-item");
  items.forEach(function (item) {
    if (item.querySelector(".user-name").textContent === userName) {
      item.remove();
    }
  });
}

function removeFromInvitedList(userName) {
  var items = document.querySelectorAll("#invitedUsers .user-item");
  items.forEach(function (item) {
    if (item.querySelector(".user-name").textContent === userName) {
      item.remove();
    }
  });
}
