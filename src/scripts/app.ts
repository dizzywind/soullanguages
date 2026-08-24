// Soul Languages — minimal client enhancements

// Episode facade: swap thumbnail for the YouTube iframe on first interaction.
document.querySelectorAll<HTMLButtonElement>('.play-btn').forEach((btn) => {
  btn.addEventListener('click', () => {
    const yt = btn.dataset.yt;
    if (!yt) return;
    const frame = document.createElement('iframe');
    frame.src = `https://www.youtube-nocookie.com/embed/${yt}?autoplay=1&rel=0`;
    frame.title = btn.getAttribute('aria-label') ?? 'YouTube video';
    frame.allow = 'accelerometer; autoplay; encrypted-media; picture-in-picture';
    frame.allowFullscreen = true;
    frame.style.border = '0';
    btn.parentElement?.append(frame);
    btn.remove();
  });
});

// Traditional / Simplified toggle.
const toggle = document.querySelector<HTMLElement>('.script-toggle');
if (toggle) {
  const sections = document.querySelectorAll<HTMLElement>('[data-script-section]');
  const buttons = toggle.querySelectorAll<HTMLButtonElement>('button[data-script]');
  const activate = (key: string) => {
    sections.forEach((s) => {
      s.hidden = s.dataset.scriptSection !== key;
    });
    buttons.forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.script === key)));
  };
  buttons.forEach((b) =>
    b.addEventListener('click', () => activate(b.dataset.script ?? 'hant'))
  );
}
