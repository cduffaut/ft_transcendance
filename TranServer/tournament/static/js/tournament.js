var popup = document.querySelector(".popup");
var blurBackground = document.querySelector(".blur-background");

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

var createButton = document.querySelector(".create-button");

createButton.addEventListener("click", function (event) {
  event.preventDefault();
  openPopup();
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

  var tourSettings = {
    ballwidth: document.getElementById("ballwidth").value,
    planksize: document.getElementById("planksize").value,
    Speed: document.getElementById("speed").value,
    acceleration: document.getElementById("acceleration").value,
    winpoint: document.getElementById("winpoint").value,
    gamesettings: document.getElementById("gamesettings").value,
    playerNumber: document.getElementById("playerNumber").value,
    participants: [],
  };
  items.forEach(function (item) {
    tourSettings.participants.push(
      item.querySelector(".user-name").textContent
    );
  });
  console.log(JSON.stringify(tourSettings));

  fetch("", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify(tourSettings),
  })
    .then((response) => {
      if (!response.ok) throw new Error("Network response was not ok");
      return response.json();
    })
    .then((data) => {
      console.log("Success:", data);
      if (data["id"]) {
        window.history.pushState(null, null, "/tournament/" + data["id"] + "/");
        fetchPage("/tournament/" + data["id"] + "/");
      } else console.error("No tournament link received from server");
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


setupInitialPlayerAmountOptions();
disableCreateButton();  

document.getElementById("gamesettings").addEventListener("change", function() {
  updatePlayerAmountOptions();  
  enableCreateButtonIfNeeded();  
});

function setupInitialPlayerAmountOptions() {
  var playerNumberSelect = document.getElementById("playerNumber");
  playerNumberSelect.innerHTML = "";  
  playerNumberSelect.appendChild(new Option("Select Player Amount", "", false, true));  
}

function updatePlayerAmountOptions() {
  var gameSettings = document.getElementById("gamesettings");
  var playerNumberSelect = document.getElementById("playerNumber");
  var selectedGameMode = gameSettings.value;

  playerNumberSelect.innerHTML = "";
  var options = [];
  if (selectedGameMode === "2") {
    options = ["4", "8", "16"];
  } else if (selectedGameMode === "4") {
    options = ["8", "16"];
  } else if (selectedGameMode === "0") {
    options = ["6", "8", "10", "12", "14", "16"];
  }

  options.forEach(function(option) {
    playerNumberSelect.appendChild(new Option(option, option));
  });

  playerNumberSelect.disabled = options.length === 0;
}

function disableCreateButton() {
    var createButton = document.querySelector(".create-button");
    createButton.classList.add('disabled'); 
    createButton.onclick = function(event) { event.preventDefault(); } 
}


function enableCreateButtonIfNeeded() {
  var gameSettings = document.getElementById("gamesettings");
  var createButton = document.querySelector(".create-button");
  if (gameSettings.value && gameSettings.value !== "") {
    createButton.disabled = false;
    createButton.classList.remove('disabled'); 
  } else {
    createButton.disabled = true;
    createButton.classList.add('disabled'); 
  }
}

const sliders = [
  { sliderId: 'ballwidth', valueId: 'ballwidth-value' },
  { sliderId: 'speed', valueId: 'speed-value' },
  { sliderId: 'winpoint', valueId: 'winpoint-value' },
  { sliderId: 'planksize', valueId: 'planksize-value' },
  { sliderId: 'acceleration', valueId: 'acceleration-value' }
];

sliders.forEach(({ sliderId, valueId }) => {
  const slider = document.getElementById(sliderId);
  const valueDisplay = document.getElementById(valueId);
  slider.addEventListener('input', function() {
    valueDisplay.textContent = this.value;
  });
});
