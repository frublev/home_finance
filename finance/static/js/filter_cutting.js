function updateFilterLabels() {
    const width = window.innerWidth;
    const isMobile = width < 576; // порог можно изменить

    document.querySelectorAll('.filter-link').forEach(link => {
        const originalText = link.dataset.original; // храним полное название
        if (!originalText) {
            link.dataset.original = link.textContent.trim();
        }

        if (isMobile) {
            if (link.dataset.original === "Quarter") link.textContent = "Quart";
            else link.textContent = link.dataset.original; // остальные оставляем
        } else {
            link.textContent = link.dataset.original; // возвращаем полное название
        }
    });
}

// вызываем при загрузке и при изменении размера
document.addEventListener("DOMContentLoaded", updateFilterLabels);
window.addEventListener("resize", updateFilterLabels);
