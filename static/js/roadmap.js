document.addEventListener("DOMContentLoaded", function() {
    // Disable all buttons initially
    const buttons = document.querySelectorAll('.topic-btn');
    buttons.forEach(button => {
        button.disabled = true;
    });

    // Enable the first button
    const firstButton = document.querySelector('.topic-btn');
    if (firstButton) firstButton.disabled = false;

    // When a user finishes a lesson, enable the next button
    const enableNextButton = function(buttonIndex) {
        if (buttons[buttonIndex + 1]) {
            buttons[buttonIndex + 1].disabled = false;
        }
    };

    // On lesson completion, call enableNextButton()
    // This function should be called after the lesson is finished
    // Example: enableNextButton(currentLessonIndex);
});
