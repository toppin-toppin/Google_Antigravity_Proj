document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const minutesInput = document.getElementById('minutes-input');
    const secondsInput = document.getElementById('seconds-input');
    const timeDisplay = document.getElementById('time-display');
    const inputContainer = document.getElementById('input-container');
    const startBtn = document.getElementById('start-btn');
    const pauseBtn = document.getElementById('pause-btn');
    const resetBtn = document.getElementById('reset-btn');
    const circle = document.querySelector('.progress-ring__circle');
    const errorMessage = document.getElementById('error-message');
    const timerContainer = document.querySelector('.timer-container');

    // Constants
    const MAX_MINUTES = 150; // 2.5 hours
    const RADIUS = circle.r.baseVal.value;
    const CIRCUMFERENCE = RADIUS * 2 * Math.PI;

    // State Variables
    let totalSeconds = 0;
    let remainingSeconds = 0;
    let timerInterval = null;
    let isRunning = false;
    let isPaused = false;

    // Initialize UI
    circle.style.strokeDasharray = `${CIRCUMFERENCE} ${CIRCUMFERENCE}`;
    circle.style.strokeDashoffset = CIRCUMFERENCE;
    timeDisplay.style.display = 'none'; // Hidden initially, showing input

    // Input Validation
    function validateInput() {
        let mins = parseInt(minutesInput.value) || 0;
        let secs = parseInt(secondsInput.value) || 0;

        if (mins > MAX_MINUTES || (mins === MAX_MINUTES && secs > 0)) {
            errorMessage.classList.add('show');
            return false;
        }

        errorMessage.classList.remove('show');
        
        // Handle overflow (e.g., 90 secs -> 1 min 30 secs)
        if (secs > 59) {
            mins += Math.floor(secs / 60);
            secs = secs % 60;
            
            if (mins > MAX_MINUTES) {
                errorMessage.classList.add('show');
                return false;
            }
            
            minutesInput.value = mins;
            secondsInput.value = secs;
        }

        return (mins > 0 || secs > 0);
    }

    // Format Time for Display
    function formatTime(totalSecs) {
        const h = Math.floor(totalSecs / 3600);
        const m = Math.floor((totalSecs % 3600) / 60);
        const s = totalSecs % 60;
        
        if (h > 0) {
            // Include hours if 60+ minutes
            // max is 150 mins = 2:30:00
            const displayMins = m.toString().padStart(2, '0');
            const displaySecs = s.toString().padStart(2, '0');
            return `${h}:${displayMins}:${displaySecs}`;
        } else {
            const displayMins = m.toString().padStart(2, '0');
            const displaySecs = s.toString().padStart(2, '0');
            return `${displayMins}:${displaySecs}`;
        }
    }

    // Update Progress Ring
    function setProgress(percent) {
        const offset = CIRCUMFERENCE - percent / 100 * CIRCUMFERENCE;
        circle.style.strokeDashoffset = offset;
    }

    // Timer Tick
    function tick() {
        if (remainingSeconds > 0) {
            remainingSeconds--;
            timeDisplay.textContent = formatTime(remainingSeconds);
            setProgress((remainingSeconds / totalSeconds) * 100);
        } else {
            // Timer Finished
            clearInterval(timerInterval);
            isRunning = false;
            isPaused = false;
            
            timerContainer.classList.add('timer-finished');
            startBtn.disabled = true;
            pauseBtn.disabled = true;
            
            // Allow resetting to play again
            
            // Optional: Play a sound here
            playNotificationSound();
        }
    }

    // Small native beep for notification
    function playNotificationSound() {
        try {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            const gainNode = ctx.createGain();
            
            osc.connect(gainNode);
            gainNode.connect(ctx.destination);
            
            osc.type = 'sine';
            osc.frequency.setValueAtTime(880, ctx.currentTime); // A5
            
            gainNode.gain.setValueAtTime(0, ctx.currentTime);
            gainNode.gain.linearRampToValueAtTime(1, ctx.currentTime + 0.1);
            gainNode.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.5);
            
            osc.start(ctx.currentTime);
            osc.stop(ctx.currentTime + 1.5);
        } catch (e) {
            console.log("Audio not supported or blocked");
        }
    }

    // Event Listeners
    
    // Inputs blur handling
    minutesInput.addEventListener('blur', () => {
        if (minutesInput.value === '') minutesInput.value = '0';
        validateInput();
    });
    
    secondsInput.addEventListener('blur', () => {
        if (secondsInput.value === '') secondsInput.value = '0';
        validateInput();
    });

    // Inputs real-time validation
    minutesInput.addEventListener('input', () => {
        const val = parseInt(minutesInput.value) || 0;
        startBtn.disabled = val === 0 && (parseInt(secondsInput.value) || 0) === 0;
        if(val > MAX_MINUTES) errorMessage.classList.add('show');
        else errorMessage.classList.remove('show');
    });

    secondsInput.addEventListener('input', () => {
        const val = parseInt(secondsInput.value) || 0;
        const minVal = parseInt(minutesInput.value) || 0;
        startBtn.disabled = val === 0 && minVal === 0;
    });

    startBtn.addEventListener('click', () => {
        if (isRunning) return;

        if (!isPaused) {
            // Starting fresh
            if (!validateInput()) return;
            
            const mins = parseInt(minutesInput.value) || 0;
            const secs = parseInt(secondsInput.value) || 0;
            
            totalSeconds = (mins * 60) + secs;
            remainingSeconds = totalSeconds;
            
            // Switch UI from input to display
            inputContainer.classList.add('hidden');
            timeDisplay.style.display = 'block';
            timeDisplay.textContent = formatTime(remainingSeconds);
            setProgress(100);
            
            // Reset styles
            timerContainer.classList.remove('timer-finished');
            circle.style.stroke = 'var(--ring-color)';
        }

        // Action: Start or Resume
        isRunning = true;
        isPaused = false;
        
        startBtn.disabled = true;
        pauseBtn.disabled = false;
        resetBtn.disabled = false;
        
        timerInterval = setInterval(tick, 1000);
    });

    pauseBtn.addEventListener('click', () => {
        if (!isRunning) return;
        
        clearInterval(timerInterval);
        isRunning = false;
        isPaused = true;
        
        startBtn.disabled = false;
        startBtn.textContent = 'Resume';
        pauseBtn.disabled = true;
    });

    resetBtn.addEventListener('click', () => {
        clearInterval(timerInterval);
        
        isRunning = false;
        isPaused = false;
        
        // Reset UI to input
        inputContainer.classList.remove('hidden');
        timeDisplay.style.display = 'none';
        
        startBtn.disabled = false;
        startBtn.textContent = 'Start';
        pauseBtn.disabled = true;
        resetBtn.disabled = true;
        
        timerContainer.classList.remove('timer-finished');
        circle.style.stroke = 'var(--ring-color)';
        setProgress(0);
        
        // Check input state to disable start if empty
        const mins = parseInt(minutesInput.value) || 0;
        const secs = parseInt(secondsInput.value) || 0;
        startBtn.disabled = (mins === 0 && secs === 0);
    });
});
