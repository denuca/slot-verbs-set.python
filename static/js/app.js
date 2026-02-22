document.addEventListener("DOMContentLoaded", () => {
    const spinBtn = document.getElementById("spin-btn");
    const slotCountInput = document.getElementById("slot-count");
    const attemptsSection = document.getElementById("attempts-section");
    const attemptsLeftEl = document.getElementById("attempts-left");
    const slotSymbolsDiv = document.getElementById("slot-symbols");
    const notification = document.getElementById("notification");

    let currentCombinationId = null;
    let maxAttempts = 3;
    let slotCount = 3;
    let attemptHistory = [];
    let imageUrls = [];
    let audioUrls = [];

    spinBtn.addEventListener("click", async () => {
        resetGameUI();

        try {
            slotCount = parseInt(slotCountInput.value, 10);
            const res = await fetch("/api/spin", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ slots: slotCount })
            });

            const data = await res.json();

            if (!res.ok) {
                showNotification(data.error || "Spin failed");
                return;
            }

            currentCombinationId = data.combination_id;
            maxAttempts = data.max_attempts;
            imageUrls = data.images || [];
            audioUrls = data.audios || [];

            renderSymbols(imageUrls, true);
            //playAudios(audioUrls); // might be too harsh to play the sound directly

            attemptsLeftEl.textContent =
                `Found 0/${data.total_combos} | Attempts 0/${maxAttempts}`;

            addAttemptInputRow();

        } catch (err) {
            console.error("Spin error:", err);
            showNotification("Server connection error.");
        }
    });

    function resetGameUI() {
        attemptsSection.innerHTML = "";
        attemptHistory = [];
        imageUrls = [];
        audioUrls = [];
        hideNotification();
        slotSymbolsDiv.innerHTML = "";
        attemptsLeftEl.textContent = "";
    }

    function renderSymbols(imagesArray, animate) {
        slotSymbolsDiv.innerHTML = "";

        imagesArray.forEach((src, i) => {
            const img = document.createElement("img");
            img.src = src;
            img.className = "slot-image";
            // Prevent right-click on the image
            img.oncontextmenu = function (e) {
                e.preventDefault();
            };
            // Prevent dragging the image
            img.addEventListener('dragstart', function (e) {
                e.preventDefault();  // Prevent the default drag behavior
            });
            // Prevent image from being dropped anywhere
            img.addEventListener('drop', function (e) {
                e.preventDefault();  // Prevent dropping the image
            });
            // Prevent image from being dropped anywhere
            img.addEventListener('click', function (e) {
                console.log("play " + audioUrls.slice(i, i+1));
                playAudios(audioUrls.slice(i, i+1));
                e.preventDefault();  // Prevent dropping the image
            });
            if (animate) img.classList.add("spin");
            slotSymbolsDiv.appendChild(img);
        });
    }

    function playAudios(audioArray) {
        if (!Array.isArray(audioArray) || audioArray.length === 0) {
            console.warn("Invalid input: The audio array is empty or not an array.");
            return;
        }

        let currentIndex = 0;

        // Function to play the next audio
        function playNextAudio() {
            if (currentIndex < audioArray.length) {
                const audioSrc = audioArray[currentIndex];

                try {
                    const audio = new Audio(audioSrc);

                    // Check if audio is loaded successfully
                    if (!audio.src) {
                        console.warn(`Invalid audio source: ${audioSrc}`);
                        currentIndex++;  // Skip this one and move to next
                        playNextAudio();  // Try to play the next audio
                        return;
                    }

                    audio.play().catch((err) => {
                        console.warn(`Failed to play audio at index ${currentIndex}:`, err);
                        currentIndex++;  // Skip this one on error
                        playNextAudio();  // Continue with next audio
                    });

                    // When the current audio finishes, play the next one
                    audio.onended = () => {
                        currentIndex++;
                        playNextAudio();  // Recursively play the next audio
                    };

                } catch (err) {
                    console.warn(`Error creating audio for ${audioSrc}:`, err);
                    currentIndex++;  // Skip to next audio in case of error
                    playNextAudio();  // Continue playing the next audio
                }
            } else {
                console.log("All audios have been played.");
            }
        }

        playNextAudio();  // Start playing the first audio
    }

    function addAttemptInputRow() {
        const inputs = [];
        const inputRow = document.createElement("div");
        inputRow.className = "attempt-row";

        for (let i = 0; i < slotCount; i++) {
            const input = document.createElement("input");
            input.type = "text";
            input.className = "form-control guess-input";
            input.maxLength = 8;
            inputRow.appendChild(input);
            inputs.push(input);
        }

        const submitBtn = document.createElement("button");
        submitBtn.className = "btn btn-success ms-2";
        submitBtn.textContent = "Send";
        submitBtn.disabled = true;

        attemptsSection.prepend(submitBtn);
        attemptsSection.prepend(inputRow);

        function updateButtonState() {
            const allFilled = inputs.every(i => i.value.trim().length > 0);
            submitBtn.disabled = !allFilled;
        }

        inputs.forEach(i => i.addEventListener("input", updateButtonState));

        submitBtn.addEventListener("click", async () => {
            submitBtn.disabled = true;

            const guesses = inputs.map(i => i.value.trim());

            try {
                const res = await fetch("/api/guess", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        combination_id: currentCombinationId,
                        guesses
                    })
                });

                const result = await res.json();

                if (!res.ok) {
                    showNotification(result.error || "Guess failed");
                    submitBtn.disabled = false;
                    return;
                }

                inputs.forEach(i => i.disabled = true);
                submitBtn.remove();

                if (result.matched) {
                    inputs.forEach(i => i.classList.add("correct"));
                } else {
                    inputs.forEach(i => i.classList.add("incorrect"));
                }

                attemptHistory.unshift({
                    guesses,
                    matched: result.matched
                });

                attemptsLeftEl.textContent =
                    `Found ${result.found_count}/${result.total_combos} | Attempts ${result.attempts_used}/${result.max_attempts}`;

                if (!result.game_over) {
                    addAttemptInputRow();
                } else {
                    showNotification(
                        result.win
                            ? "🎉 You found ALL combinations!"
                            : "❌ Max attempts reached!",
                        true
                    );
                }

            } catch (err) {
                console.error("Guess error:", err);
                showNotification("Server error.");
                submitBtn.disabled = false;
            }
        }, { once: true });
    }

    function showNotification(message, endGame = false) {
        notification.innerHTML = message;
        notification.classList.remove("d-none");

        if (endGame) {
            const closeBtn = document.createElement("button");
            closeBtn.className = "btn-close ms-2";
            closeBtn.addEventListener("click", hideNotification);
            notification.appendChild(closeBtn);
        }
    }

    function hideNotification() {
        notification.classList.add("d-none");
        notification.innerHTML = "";
    }
});