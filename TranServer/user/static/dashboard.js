// Récupère la liste envoyée depuis Django
var username = document.getElementById("username").textContent;

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
    document.getElementById("profile-pic").src = data;
  });

  
  function displayData(gameData) {
    const scrollContainer = document.querySelector('.scroll-container');
    
    gameData.forEach(entry => {
      const date = entry.date;
      const users = entry.users;
      const points = entry.points;
      
      // Créer un élément de liste pour la date
      const dateItem = document.createElement('div');
      dateItem.textContent = `Date: ${date}`;
      scrollContainer.appendChild(dateItem);
      
      // Créer un élément de liste pour les noms d'utilisateurs et les points
      const userList = document.createElement('ul');
      users.forEach((user, index) => {
        const listItem = document.createElement('li');
        listItem.textContent = `${user} - ${points[index]} points`;
        userList.appendChild(listItem);
      });
      scrollContainer.appendChild(userList);
      
      // Ajouter une séparation entre les entrées
      const separator = document.createElement('hr');
      separator.className = 'separation-hr';
      scrollContainer.appendChild(separator);
    });
  }
  
fetch("/api/gameHistory/" + username + "/")
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json(); // Convertit la réponse en JSON
    })
    .then(data => {
      displayData(data.historyGames)
    })
    .catch(error => {
      console.log('There was a problem with the fetch operation:', error.message);
    });
// Appeler la fonction pour afficher les données