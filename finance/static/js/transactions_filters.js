function pad(n){ return n<10 ? '0'+n : n; }

function isLastDayOfMonth(date) {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate() === date.getDate();
}

function getPastDate(today, daysAgo) {
    return new Date(today.getFullYear(), today.getMonth(), today.getDate() - daysAgo);
}

// Получение первого дня текущего месяца (для this_month)
function firstDayOfThisMonth(today) {
    return new Date(today.getFullYear(), today.getMonth(), 1);
}

function isLastDayOfQuarter(date) {
    const endMonth = Math.floor(date.getMonth() / 3) * 3 + 2;
    const lastDay = new Date(date.getFullYear(), endMonth + 1, 0);
    return date.toDateString() === lastDay.toDateString();
}

function isLastDayOfHalf(date) {
    const endMonth = date.getMonth() < 6 ? 5 : 11;
    const lastDay = new Date(date.getFullYear(), endMonth + 1, 0);
    return date.toDateString() === lastDay.toDateString();
}

function isLastDayOfYear(date) {
    return date.getMonth() === 11 && date.getDate() === 31;
}

function fullMonthFromDate(today) {
    // если сегодня последний день месяца — берём текущий месяц целиком
    if (isLastDayOfMonth(today)) {
        return new Date(today.getFullYear(), today.getMonth(), 1);
    }

    // иначе: соответствующая дата прошлого месяца + 1 день
    const prevMonthSameDay = new Date(
        today.getFullYear(),
        today.getMonth() - 1,
        today.getDate()
    );

    prevMonthSameDay.setDate(prevMonthSameDay.getDate() + 1);
    return prevMonthSameDay;
}

function fullQuarterFromDate(today) {
    if (isLastDayOfQuarter(today)) {
        const qStartMonth = Math.floor(today.getMonth() / 3) * 3;
        return new Date(today.getFullYear(), qStartMonth, 1);
    }

    const prevQuarterSameDay = new Date(
        today.getFullYear(),
        today.getMonth() - 3,
        today.getDate()
    );

    prevQuarterSameDay.setDate(prevQuarterSameDay.getDate() + 1);
    return prevQuarterSameDay;
}

function fullHalfFromDate(today) {
    if (isLastDayOfHalf(today)) {
        const startMonth = today.getMonth() < 6 ? 0 : 6;
        return new Date(today.getFullYear(), startMonth, 1);
    }

    const prevHalfSameDay = new Date(
        today.getFullYear(),
        today.getMonth() - 6,
        today.getDate()
    );

    prevHalfSameDay.setDate(prevHalfSameDay.getDate() + 1);
    return prevHalfSameDay;
}

function fullYearFromDate(today) {
    if (isLastDayOfYear(today)) {
        return new Date(today.getFullYear(), 0, 1);
    }

    const prevYearSameDay = new Date(
        today.getFullYear() - 1,
        today.getMonth(),
        today.getDate()
    );

    prevYearSameDay.setDate(prevYearSameDay.getDate() + 1);
    return prevYearSameDay;
}

// Получение даты начала квартала
function firstDayOfQuarter(today) {
    const q = Math.floor(today.getMonth()/3);
    return new Date(today.getFullYear(), q*3, 1);
}

// Получение даты начала полугодия
function firstDayOfHalf(today) {
    const half = (today.getMonth() < 6) ? 0 : 6;
    return new Date(today.getFullYear(), half, 1);
}

// Получение даты начала года
function firstDayOfYear(today) {
    return new Date(today.getFullYear(), 0, 1);
}

// Основной обработчик клика на фильтры периода
document.querySelectorAll('.filter-link').forEach(link => {
    link.addEventListener('click', function(e){
        e.preventDefault();

        const period = this.getAttribute('href').split('=')[1];
        const today = new Date();
        let fromDate;

        switch(period){
            case 'today':
                fromDate = today;
                break;
            case 'week':
                fromDate = getPastDate(today, 6);
                break;
            case 'month':
                // обычный month (для совместимости)
                fromDate = fullMonthFromDate(today);
                break;
            case 'quarter':
                fromDate = fullQuarterFromDate(today)
                break;
            case 'half':
                fromDate = fullHalfFromDate(today)
                break;
            case 'year':
                fromDate = fullYearFromDate(today)
                break;
            case 'this_month':
                // новый период для категорий
                fromDate = firstDayOfThisMonth(today);
                break;
            case 'this_quarter':
                fromDate = firstDayOfQuarter(today);
                break;
            case 'this_half':
                fromDate = firstDayOfHalf(today);
                break;
            case 'this_year':
                fromDate = firstDayOfYear(today);
                break;
            default:
                return; // неизвестный фильтр
        }

        const f = fromDate.getFullYear() + '-' + pad(fromDate.getMonth()+1) + '-' + pad(fromDate.getDate());
        const t = today.getFullYear() + '-' + pad(today.getMonth()+1) + '-' + pad(today.getDate());

        const url = new URL(window.location.href);
        url.searchParams.set('from_date', f);
        url.searchParams.set('to_date', t);
        url.searchParams.set('filter', period);

        // сохраняем type, если есть
        const currentType = url.searchParams.get('type');
        if(currentType){
            url.searchParams.set('type', currentType);
        }

        url.searchParams.delete('page'); // сброс страницы при смене фильтра
        window.location.href = url.toString();
    });
});

//function pad(n){ return n<10 ? '0'+n : n; }
//
//// Функция для получения даты "n" дней назад от today
//function getPastDate(today, daysAgo) {
//    return new Date(today.getFullYear(), today.getMonth(), today.getDate() - daysAgo);
//}
//
//// Функция для получения количества дней в предыдущем месяце
//function daysInPreviousMonth(today) {
//    let prevMonth = today.getMonth() - 1;
//    let prevYear = today.getFullYear();
//    if(prevMonth < 0){
//        prevMonth = 11; // декабрь
//        prevYear -= 1;
//    }
//    return new Date(prevYear, prevMonth + 1, 0).getDate();
//}
//
//// Основной обработчик клика
//document.querySelectorAll('.filter-link').forEach(link => {
//    link.addEventListener('click', function(e){
//        e.preventDefault();
//        const period = this.getAttribute('href').split('=')[1];
//        const today = new Date();
//        let fromDate;
//
//        switch(period){
//            case 'today': fromDate = today; break;
//            case 'week': fromDate = getPastDate(today, 6); break;
//            case 'month':
//                const daysPrevMonth = daysInPreviousMonth(today);
//                fromDate = getPastDate(today, daysPrevMonth - 1);
//                break;
//            default: return;
//        }
//
//        const f = fromDate.getFullYear() + '-' + pad(fromDate.getMonth()+1) + '-' + pad(fromDate.getDate());
//        const t = today.getFullYear() + '-' + pad(today.getMonth()+1) + '-' + pad(today.getDate());
//
//        const url = new URL(window.location.href);
//        url.searchParams.set('from_date', f);
//        url.searchParams.set('to_date', t);
//        url.searchParams.set('filter', period);
//        url.searchParams.delete('page'); // сброс страницы при смене фильтра
//        window.location.href = url.toString();
//    });
//});
