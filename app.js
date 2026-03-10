document.addEventListener('DOMContentLoaded', () => {
    // === DOM Elements ===
    const timeDisplay = document.getElementById('time-display');
    const modeText = document.getElementById('mode-text');
    const startBtn = document.getElementById('start-btn');
    const pauseBtn = document.getElementById('pause-btn');
    const resetBtn = document.getElementById('reset-btn');
    const switchModeBtn = document.getElementById('switch-mode-btn');
    const sessionCountDisplay = document.getElementById('session-count');
    const progressRing = document.getElementById('progress-ring');

    // === Constants ===
    const WORK_TIME = 25 * 60; // 25 minutes
    const BREAK_TIME = 5 * 60; // 5 minutes
    const CIRCUMFERENCE = 2 * Math.PI * 140; // r=140 matches SVG

    // === State ===
    let timeLeft = WORK_TIME;
    let isWorkMode = true;
    let isRunning = false;
    let timerInterval = null;
    let sessionCount = 0;

    // === Initialization ===
    function init() {
        progressRing.style.strokeDasharray = `${CIRCUMFERENCE} ${CIRCUMFERENCE}`;
        updateDisplay();
    }

    // === Timer Functions ===
    function startTimer() {
        if (isRunning) return;
        
        isRunning = true;
        startBtn.disabled = true;
        pauseBtn.disabled = false;
        
        timerInterval = setInterval(() => {
            timeLeft--;
            updateDisplay();
            
            if (timeLeft <= 0) {
                handleTimerComplete();
            }
        }, 1000);
    }

    function pauseTimer() {
        if (!isRunning) return;
        
        clearInterval(timerInterval);
        isRunning = false;
        startBtn.disabled = false;
        pauseBtn.disabled = true;
    }

    function resetTimer() {
        pauseTimer();
        timeLeft = isWorkMode ? WORK_TIME : BREAK_TIME;
        updateDisplay();
    }

    function switchMode() {
        isWorkMode = !isWorkMode;
        document.body.classList.toggle('break-mode', !isWorkMode);
        modeText.textContent = isWorkMode ? 'Work Session' : 'Break Time';
        resetTimer();
    }

    function handleTimerComplete() {
        pauseTimer();
        
        // Play sound (optional)
        // const audio = new Audio('ding.mp3');
        // audio.play();
        
        if (isWorkMode) {
            sessionCount++;
            sessionCountDisplay.textContent = sessionCount;
            // Auto switch to break
            switchMode();
        } else {
            // Auto switch to work
            switchMode();
        }
    }

    // === UI Updaters ===
    function updateDisplay() {
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        
        const timeString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        timeDisplay.textContent = timeString;
        document.title = `${timeString} - ${isWorkMode ? 'Work' : 'Break'}`;
        
        updateProgressRing();
    }

    function updateProgressRing() {
        const totalTime = isWorkMode ? WORK_TIME : BREAK_TIME;
        const progress = timeLeft / totalTime;
        // Calculate offset (0 = full circle, CIRCUMFERENCE = empty circle)
        const offset = CIRCUMFERENCE - (progress * CIRCUMFERENCE);
        progressRing.style.strokeDashoffset = offset;
    }

    // === Event Listeners ===
    startBtn.addEventListener('click', startTimer);
    pauseBtn.addEventListener('click', pauseTimer);
    resetBtn.addEventListener('click', resetTimer);
    switchModeBtn.addEventListener('click', switchMode);

    // Run init
    init();
});
