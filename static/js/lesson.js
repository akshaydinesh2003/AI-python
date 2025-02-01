document.addEventListener("DOMContentLoaded", function() {
    const nextLessonButton = document.getElementById('next-lesson-btn');
    const lessonCompleted = localStorage.getItem('lessonCompleted');

    // Check if the lesson is completed, enable next lesson button
    if (lessonCompleted === 'true') {
        nextLessonButton.disabled = false;
    }

    // Mark lesson as completed
    document.querySelector('.lesson-complete-btn').addEventListener('click', function() {
        localStorage.setItem('lessonCompleted', 'true');
        nextLessonButton.disabled = false;
    });
});
