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
            audioUrls = data.audios_urls || [];

            renderSymbols(imageUrls, true);
            playAudios(audioUrls);

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

        imagesArray.forEach(src => {
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
            if (animate) img.classList.add("spin");
            slotSymbolsDiv.appendChild(img);
        });
    }

    function playAudios(audioArray) {
        audioArray.forEach(src => {
            try {
                const audio = new Audio(src);
                audio.play().catch(() => {});
            } catch (err) {
                console.warn("Audio playback failed:", err);
            }
        });
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