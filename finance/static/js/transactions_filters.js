function pad(n){ return n<10 ? '0'+n : n; }

// Функция для получения даты "n" дней назад от today
function getPastDate(today, daysAgo) {
    return new Date(today.getFullYear(), today.getMonth(), today.getDate() - daysAgo);
}

// Функция для получения количества дней в предыдущем месяце
function daysInPreviousMonth(today) {
    let prevMonth = today.getMonth() - 1;
    let prevYear = today.getFullYear();
    if(prevMonth < 0){
        prevMonth = 11; // декабрь
        prevYear -= 1;
    }
    return new Date(prevYear, prevMonth + 1, 0).getDate();
}

// Основной обработчик клика
document.querySelectorAll('.filter-link').forEach(link => {
    link.addEventListener('click', function(e){
        e.preventDefault();
        const period = this.getAttribute('href').split('=')[1];
        const today = new Date();
        let fromDate;

        switch(period){
            case 'today': fromDate = today; break;
            case 'week': fromDate = getPastDate(today, 6); break;
            case 'month':
                const daysPrevMonth = daysInPreviousMonth(today);
                fromDate = getPastDate(today, daysPrevMonth - 1);
                break;
            default: return;
        }

        const f = fromDate.getFullYear() + '-' + pad(fromDate.getMonth()+1) + '-' + pad(fromDate.getDate());
        const t = today.getFullYear() + '-' + pad(today.getMonth()+1) + '-' + pad(today.getDate());

        const url = new URL(window.location.href);
        url.searchParams.set('from_date', f);
        url.searchParams.set('to_date', t);
        url.searchParams.set('filter', period);
        url.searchParams.delete('page'); // сброс страницы при смене фильтра
        window.location.href = url.toString();
    });
});
