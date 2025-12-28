function toggleTag(tagName) {
    const input = document.getElementById('transaction_tags_input');
    let tags = input.value ? input.value.split(',') : [];

    const index = tags.indexOf(tagName);
    const badges = document.querySelectorAll(`[data-tag-name="${tagName}"]`);

    if (index === -1) {
        // ✅ добавить тег
        tags.push(tagName);
        badges.forEach(b => {
            b.classList.remove('bg-secondary');
            b.classList.add('bg-primary');
        });

        // добавить в description
        const field = document.getElementById("id_description");
        if (field) {
            if (field.value && !field.value.endsWith(" ")) field.value += " ";
            field.value += tagName + " ";
        }
    } else {
        // ❌ удалить тег
        tags.splice(index, 1);
        badges.forEach(b => {
            b.classList.remove('bg-primary');
            b.classList.add('bg-secondary');
        });

        // убрать из description
        const field = document.getElementById("id_description");
        if (field) {
            // аккуратно убираем слово + пробел
            const regex = new RegExp(`\\b${tagName}\\b\\s*`, 'g');
            field.value = field.value.replace(regex, '');
        }
    }

    input.value = tags.join(',');
}

function insertTag(tagName) {
    const input = document.getElementById('transaction_tags_input');
    let tags = input.value ? input.value.split(',') : [];
    if (!tags.includes(tagName)) {
        tags.push(tagName);
    }
    input.value = tags.join(',');
    // визуально подсвечиваем
    const badges = document.querySelectorAll(`[data-tag-name="${tagName}"]`);
    badges.forEach(b => {
        b.classList.remove('bg-secondary', 'me-1');
        b.classList.add('bg-primary', 'me-1');
    });

    const field = document.getElementById("id_description");
    if (!field) return;

    if (field.value && !field.value.endsWith(" ")) {
        field.value += " ";
    }

    field.value += tagName + " ";
    field.focus();
}
