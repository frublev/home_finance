document.addEventListener("DOMContentLoaded", function () {
    const categorySelect = document.getElementById("id_category");
    const tagsContainer = document.getElementById("tags-container");
    const tagsList = document.getElementById("tags-list");
    const tagsInput = document.getElementById("transaction_tags_input");

    function renderTags(tags) {
        tagsList.innerHTML = "";
        tags.forEach(tag => {
            const span = document.createElement("span");
            span.className = "badge bg-secondary me-1 tag-item";
            span.style.cursor = "pointer";
            span.dataset.tag = tag.name;
            span.innerText = tag.name;

            span.onclick = () => toggleTag(tag.name, span);
            tagsList.appendChild(span);
        });
    }

    function toggleTag(tagName, el) {
        let tags = tagsInput.value ? tagsInput.value.split(",") : [];
        const field = document.getElementById("id_description");

        if (tags.includes(tagName)) {
            tags = tags.filter(t => t !== tagName);
            el.classList.remove("bg-primary");
            el.classList.add("bg-secondary");

            if (field) {
                // аккуратно убираем слово + пробел
                const regex = new RegExp(`\\b${tagName}\\b\\s*`, 'g');
                field.value = field.value.replace(regex, '');
            }

        } else {
            tags.push(tagName);
            el.classList.remove("bg-secondary");
            el.classList.add("bg-primary");
            if (field) {
                if (field.value && !field.value.endsWith(" ")) field.value += " ";
                field.value += tagName + " ";
            }
        }

        tagsInput.value = tags.join(",");
    }

    categorySelect.addEventListener("change", function () {
        const categoryId = this.value;

        if (!categoryId) {
            tagsContainer.style.display = "none";
            tagsList.innerHTML = "";
            return;
        }

        fetch(`/categories/${categoryId}/tags/`)
            .then(res => res.json())
            .then(data => {
                renderTags(data.tags);
                tagsContainer.style.display = "block";
                tagsInput.value = "";
            });
    });

    const initialCategoryId = categorySelect.value;
    const initialTags = tagsInput.value ? tagsInput.value.split(",") : [];

    if (initialCategoryId) {
        fetch(`/categories/${initialCategoryId}/tags/`)
            .then(res => res.json())
            .then(data => {
                renderTags(data.tags);

                // подсветка уже выбранных тегов
                document.querySelectorAll(".tag-item").forEach(el => {
                    if (initialTags.includes(el.dataset.tag)) {
                        el.classList.remove("bg-secondary");
                        el.classList.add("bg-primary");
                    }
                });
                tagsContainer.style.display = "block";
            });
    }
});

