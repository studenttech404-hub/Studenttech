// Ensure session user id exists by calling a light GET (server sets session on first requests).
// Not required but good to ensure consistent user id.
fetch('/testimonials').catch(()=>{});

// Attach behavior after DOM loaded
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.testimonial-card').forEach(card => {
    const id = card.dataset.id;
    const likeBtn = card.querySelector('.like-btn');
    const likeCountEl = card.querySelector('.like-count');
    const commentForm = card.querySelector('.comment-form');
    const commentList = card.querySelector('.comment-list');

    // Like button
    likeBtn?.addEventListener('click', () => {
      fetch(`/like/${id}`, { method: 'POST' })
        .then(resp => resp.json().then(data => ({ ok: resp.ok, data })))
        .then(result => {
          if (result.ok) {
            likeCountEl.textContent = result.data.likes;
            likeBtn.disabled = true;
            likeBtn.textContent = '👍 Liked';
          } else {
            // already liked or error
            if (result.data && result.data.error === 'already_liked') {
              likeBtn.disabled = true;
              likeBtn.textContent = '👍 Liked';
            } else {
              alert('Error liking post.');
            }
          }
        })
        .catch(err => console.error(err));
    });

    // Comment submit
    commentForm?.addEventListener('submit', (e) => {
      e.preventDefault();
      const name = commentForm.querySelector('input[name="name"]').value.trim();
      const text = commentForm.querySelector('input[name="comment"]').value.trim();
      if (!text) return;

      fetch(`/comment/${id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_name: name || 'Visitor', comment: text })
      })
      .then(r => r.json())
      .then(data => {
        if (data && data.text) {
          const div = document.createElement('div');
          div.className = 'comment';
          div.innerHTML = `<strong>${data.user_name}</strong>: ${data.text}`;
          commentList.appendChild(div);
          commentForm.querySelector('input[name="comment"]').value = '';
        } else {
          alert('Failed to post comment.');
        }
      })
      .catch(err => console.error(err));
    });
  });
});
