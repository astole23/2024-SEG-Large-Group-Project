document.addEventListener('DOMContentLoaded', function () {
    fetch('/notifications/?format=json')
        .then(response => response.json())
        .then(data => {
            const unreadCountElement = document.getElementById('unread-count');
            if (unreadCountElement) {
                unreadCountElement.textContent = data.unread_count || 0;
            }
        })
        .catch(error => console.error('Error fetching notifications:', error));
});
