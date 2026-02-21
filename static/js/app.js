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
    let symbols = [];

    spinBtn.addEventListener("click", async () => {
        slotCount = parseInt(slotCountInput.value, 10);
        attemptsSection.innerHTML = "";
        attemptHistory = [];
        symbols = [];
        hideNotification();

        try {
            const res = await fetch("/api/spin", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ slots: slotCount })
            });

            const data = await res.json();

            if (res.ok) {
                currentCombinationId = data.combination_id;
                maxAttempts = data.max_attempts;
                symbols = data.symbols;

                renderSymbols(symbols, true);

                attemptsLeftEl.textContent =
                    `Found 0/${data.total_combos} | Attempts 0/${maxAttempts}`;

                addAttemptInputRow();
            } else {
                showNotification(data.error || "Error spinning");
            }
        } catch (err) {
            console.error(err);
            showNotification("Error connecting to server.");
        }
    });

    function renderSymbols(symbolsArray, animate) {
        slotSymbolsDiv.innerHTML = "";
        symbolsArray.forEach(s => {
            const span = document.createElement("span");
            span.textContent = s;
            span.className = "slot-symbol";
            if (animate) span.classList.add("spin");
            slotSymbolsDiv.appendChild(span);
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
            const inputs = Array.from(inputRow.querySelectorAll("input.guess-input"));
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

                if (res.ok) {

                    // lock inputs
                    inputs.forEach(i => i.disabled = true);
                    submitBtn.remove();

                    // mark matched combo visually
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
                        const msg = result.win
                            ? "🎉 You found ALL combinations!"
                            : "❌ Max attempts reached!";
                        showNotification(msg, true);
                    }

                } else {
                    showNotification(result.error || "Error checking guess");
                }

            } catch (err) {
                console.error(err);
                showNotification("Server error.");
            }
        }, {once: true});
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