document.addEventListener("DOMContentLoaded", function() {
    const quizForm = document.querySelector('.form');
    const submitButton = quizForm.querySelector('button[type="submit"]');
    let timer = 10;  // Timer in seconds
    const timerDisplay = document.createElement('p');
    timerDisplay.textContent = `Time left: ${timer}s`;
    document.querySelector('.container').appendChild(timerDisplay);

    // Countdown timer for quiz
    const countdown = setInterval(function() {
        if (timer <= 0) {
            clearInterval(countdown);
            timerDisplay.textContent = 'Time is up!';
            submitButton.disabled = true;  // Disable the submit button after time is up
        } else {
            timerDisplay.textContent = `Time left: ${timer--}s`;
        }
    }, 1000);

    // Feedback after quiz submission
    quizForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const answers = new FormData(quizForm);
        let correctAnswers = 0;
        
        if (answers.get('q1') === 'a') correctAnswers++;
        if (answers.get('q2') === 'a') correctAnswers++;

        alert(`You got ${correctAnswers} out of 2 correct!`);

        // Redirect or show feedback
        setTimeout(() => {
            window.location.href = '/roadmap';  // Redirect to roadmap after quiz
        }, 2000);
    });
});
