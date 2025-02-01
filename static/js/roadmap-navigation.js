document.addEventListener("DOMContentLoaded", function() {
    const roadmapButtons = document.querySelectorAll('.topic-btn');
    roadmapButtons.forEach((button, index) => {
        button.addEventListener('click', function() {
            const lessonID = button.getAttribute('data-lesson-id');
            window.location.href = `/lesson/${lessonID}`;
        });
    });
});
