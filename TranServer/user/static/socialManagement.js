var users = [];

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

async function update_all() {
  update_user(await fetchFrom("/api/friends/"), "friend");
  update_user(await fetchFrom("/api/blocked/"), "blocked");
  update_user(await fetchFrom("/api/invite/"), "waiting");
  update_user(await fetchFrom("/api/pending_invite/"), "pending");
}

function update_user(data, type) {
  for (var user in data) {
    users.push({ username: data[user].username, status: type });
  }
}

function refresh_view() {
  users = [];
  update_all().then((data) => {
    displayUsers(users);
  });
}
refresh_view();

var searchBox = document.querySelector(".search-box");
var dropdownMenu = document.createElement("div");
dropdownMenu.classList.add("dropdown-menu");
document.querySelector(".search-selection").appendChild(dropdownMenu);

function update_search_box() {
  var searchText = searchBox.value.toLowerCase();
  if (!searchText) {
    dropdownMenu.innerHTML = "";
    return;
  }
  fetchFrom("/api/search/" + searchText + "/")
    .then((data) => {
      dropdownMenu.innerHTML = "";
      data.usernames.forEach((item) => {
        const autocompleteItem = document.createElement("div");
        autocompleteItem.classList.add("autocomplete-item");
        autocompleteItem.textContent = item;
        autocompleteItem.addEventListener("click", function () {
          searchBox.value = item;
          dropdownMenu.innerHTML = "";
        });
        dropdownMenu.appendChild(autocompleteItem);
      });
    })
    .catch((error) => {
      console.error("Error fetching data: ", error);
    });
}

document.getElementById("invite_btn").addEventListener("click", function () {
  if (searchBox.value == "") {
    displayError("Please, enter a username");
    return;
  }
  fetch("/api/exist/" + searchBox.value + "/")
    .then((response) => response.json())
    .then((data) => {
      if (data) {
        addFriend(searchBox.value);
        refresh_view();
        clearError();
      } else {
        throw new Error("User does not exist");
      }
    })
    .catch((error) => {
      displayError(error.message || "Error during the user invitation.");
    });
});

document.getElementById("block_btn").addEventListener("click", function () {
  if (searchBox.value == "") {
    displayError("Please, enter a username");
    return;
  }
  fetch("/api/exist/" + searchBox.value + "/")
    .then((response) => response.json())
    .then((data) => {
      if (data) {
        // ici aussi, ajustez en utilisant simplement 'data'
        blockUser(searchBox.value);
        refresh_view();
        clearError();
      } else {
        throw new Error("User does not exist");
      }
    })
    .catch((error) => {
      displayError(error.message || "Error during the user blocking.");
    });
});

function blockUser(username) {
  doRequest("blocked", "POST", username);
}

function doRequest(path, method, username) {
  if (username === getCurrentUser()) {
    displayError("You cannot add or block yourself.");
    return Promise.reject(new Error("Attempt to add or block self"));
  }

  return fetch("/api/" + path + "/" + username + "/", {
    method: method,
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Failed to execute request");
      }
      return response.json();
    })
    .catch((error) => {
      console.error("Error in doRequest:", error);
      displayError(error.message || "Error during the API request.");
      throw error;
    });
}

function displayError(message) {
  const errorMessage = document.getElementById("error_message");
  errorMessage.textContent = message;
  errorMessage.style.display = "block";
}

function clearError() {
  const errorMessage = document.getElementById("error_message");
  errorMessage.style.display = "none";
}

searchBox.addEventListener("input", function () {
  update_search_box();
});
searchBox.addEventListener("click", function () {
  update_search_box();
});

function updateExistingUserElement(li, user) {
  li.querySelector(".username").textContent = user.username;
  const actionButtons = getActionButtons(user);
  const buttonContainer = li.querySelector(".action-buttons");
  if (!buttonContainer) {
    li.innerHTML += `<div class="action-buttons">${actionButtons}</div>`;
  } else {
    buttonContainer.innerHTML = actionButtons;
  }
}

function displayUsers(users) {
  clearLists();
  users.forEach(function (user) {
    let li = document.querySelector(`li[data-username='${user.username}']`); // Recherche d'un élément existant
    if (!li) {
      li = createUserElement(user);
    } else {
      updateExistingUserElement(li, user);
    }
    switch (user.status) {
      case "friend":
        document.querySelector(".friends-list").appendChild(li);
        break;
      case "pending":
        document.querySelector(".pending-list").appendChild(li);
        break;
      case "blocked":
        document.querySelector(".blocked-list").appendChild(li);
        break;
      case "waiting":
        document.querySelector(".waiting-approval-list").appendChild(li);
        break;
    }
  });
}

function clearLists() {
  document.querySelector(".friends-list").innerHTML = "";
  document.querySelector(".pending-list").innerHTML = "";
  document.querySelector(".blocked-list").innerHTML = "";
  document.querySelector(".waiting-approval-list").innerHTML = "";
}

function createUserElement(user) {
  var li = document.createElement("li");
  li.addEventListener("click", function (event) {
    if (!event.target.closest(".action-buttons")) {
      url = "/dashboard/" + user.username + "/";
      window.history.pushState(null, null, url);
      fetchPage(url);
    }
  });
  li.className = "user-item";
  li.setAttribute("data-username", user.username);
  li.innerHTML = `
  <span class="username">${user.username}</span>
  <div class="action-buttons">${getActionButtons(user)}</div>
`;
  fetch("/api/profile_pic/" + user.username + "/")
    .then((response) => response.blob())
    .then((blob) => {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(blob);
      });
    })
    .then((data) => {
      li.innerHTML =
        '<div class="user-photo" style="background-image: url(' +
        data +
        ');"></div>' +
        li.innerHTML;
    });

  return li;
}

function getActionButtons(user) {
  switch (user.status) {
    case "waiting":
      return `
                <button class="button approve-button user-button" onclick="approveUser('${user.username}')">Approve</button>
                <button class="button decline-button user-button" onclick="declineUser('${user.username}')">Decline</button>
            `;
    case "friend":
      return `<button class="button remove-button" onclick="removeFriend('${user.username}')">Remove</button>`;
    case "pending":
      return `<button class="button request-sent-button" onclick="cancelRequest('${user.username}')">Cancel Request</button>`;
    case "blocked":
      return `<button class="button unblock-button" onclick="unblockUser('${user.username}')">Unblock</button>`;
    default:
      return `
                <button class="button add-button user-button" onclick="addFriend('${user.username}')">Add</button>
                <button class="button block-button user-button" onclick="blockUser('${user.username}')">Block</button>
            `;
  }
}

function approveUser(username) {
  doRequest("friends", "POST", username);
}

function declineUser(username) {
  doRequest("invite", "DELETE", username);
}

function doRequest(path, method, username) {
  fetch("/api/" + path + "/" + username + "/", {
    method: method,
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      // Process the data if needed
      refresh_view();
    })
    .catch((error) => {
      console.error("There was a problem with the fetch operation:", error);
    });
}

async function addFriend(username) {
  try {
    await doRequest("invite", "POST", username);
  } catch (error) {
    console.error("Error during API request:", error);
    displayError(error.message || "Error during the user invitation.");
  }
}

async function blockUser(username) {
  try {
    await doRequest("blocked", "POST", username);
  } catch (error) {
    console.error("Error during API request:", error);
    displayError(error.message || "Error during the user blocking.");
  }
}

function cancelRequest(username) {
  doRequest("undo_invite", "DELETE", username);
}

function removeFriend(username) {
  doRequest("friends", "DELETE", username);
}

function unblockUser(username) {
  doRequest("blocked", "DELETE", username);
}

function displaySuccess(message) {
  const successMessage = document.getElementById("success_message");
  successMessage.textContent = message;
  successMessage.style.display = "block";
  successMessage.style.fontStyle = "italic";
  successMessage.style.color = "green";
}
