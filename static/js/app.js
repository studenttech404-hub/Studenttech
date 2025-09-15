
function lockNonPremium(isPremium, pageNum) {
  const overlay = document.getElementById('lockOverlay');
  if(!overlay) return;
  const locked = (!isPremium && pageNum > 1);
  overlay.classList.toggle('show', locked);
}

function showUpgrade() {
  const el = document.getElementById('upgradeModal');
  if(el) el.classList.remove('hidden');
}
function closeUpgrade() {
  const el = document.getElementById('upgradeModal');
  if(el) el.classList.add('hidden');
}
