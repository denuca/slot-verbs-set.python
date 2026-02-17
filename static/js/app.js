document.addEventListener("DOMContentLoaded", () => {
    const spinBtn = document.getElementById("spin-btn");
    const slotCountInput = document.getElementById("slot-count");
    const attemptsSection = document.getElementById("attempts-section");
    const attemptsLeftEl = document.getElementById("attempts-left");
    const slotSymbolsDiv = document.getElementById("slot-symbols");
    const notification = document.getElementById("notification");

    let currentCombinationId = null;
    let sessionId = null;
    let maxAttempts = 3;
    let attemptsUsed = 0;
    let slotCount = 3;

    let attemptHistory = [];
    let symbols = [];

    // Load shared data if present in URL
    const urlParams = new URLSearchParams(window.location.search);
    const sharedData = urlParams.get("data");
    if (sharedData) {
        try {
            const decoded = decodeURIComponent(escape(atob(sharedData)));
            const parsed = JSON.parse(decoded);
            slotCount = parsed.slotCount;
            symbols = parsed.symbols;
            attemptHistory = parsed.attempts;
            maxAttempts = attemptHistory.length;

            renderSymbols(symbols, false);
            attemptHistory.forEach((attempt, index) => renderAttemptRow(attempt, index + 1, false));

            attemptsLeftEl.textContent = "Shared game view";
        } catch (e) { console.error("Failed to load shared data:", e); }
    }

    // Spin button handler
    spinBtn.addEventListener("click", async () => {
        slotCount = parseInt(slotCountInput.value, 10);
        attemptsSection.innerHTML = "";
        attemptsUsed = 0;
        attemptHistory = [];
        symbols = [];
        hideNotification();

        try {
            const res = await fetch("/api/spin", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ slots: slotCount, session_id: sessionId })
            });
            const data = await res.json();

            if (res.ok) {
                currentCombinationId = data.combination_id;
                sessionId = data.session_id;
                maxAttempts = data.max_attempts;
                symbols = data.symbols;

                renderSymbols(symbols, true);
                attemptsLeftEl.textContent = `Attempts left: ${maxAttempts - attemptsUsed}`;
                addAttemptInputRow();
            } else {
                showNotification(data.error || "Error spinning");
            }
        } catch (err) {
            console.error(err);
            showNotification("Error connecting to server.");
        }
    });

    // Render spun symbols
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

    // Add current attempt input row
    function addAttemptInputRow() {
        const inputRow = document.createElement("div");
        inputRow.className = "attempt-row";

        const attemptNumber = document.createElement("span");
        attemptNumber.className = "attempt-number";
        attemptNumber.textContent = `#${attemptsUsed + 1}`;
        inputRow.appendChild(attemptNumber);

        for (let i = 0; i < slotCount; i++) {
            const input = document.createElement("input");
            input.type = "text";
            input.className = "form-control guess-input";
            input.setAttribute("aria-label", `Guess word for slot ${i + 1}`);
            input.maxLength = 25;

            // Pre-fill previously guessed correct words
            if (attemptHistory.length > 0) {
                const prev = attemptHistory[0][i];
                if (prev.correct) input.value = prev.guess;
            }

            inputRow.appendChild(input);
        }

        const submitBtn = document.createElement("button");
        submitBtn.className = "btn btn-success ms-2";
        submitBtn.textContent = "Submit";
        inputRow.appendChild(submitBtn);

        attemptsSection.prepend(inputRow);

        submitBtn.addEventListener("click", async () => {
            const inputs = Array.from(inputRow.querySelectorAll("input.guess-input"));
            const guesses = inputs.map(i => i.value.trim());

            try {
                const res = await fetch("/api/guess", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ combination_id: currentCombinationId, guesses })
                });
                const result = await res.json();

                if (res.ok) {
                    const attemptRecord = [];
                    let allCorrect = true;

                    result.results.forEach((r, idx) => {
                        const input = inputs[idx];
                        input.value = r.user_guess;
                        input.disabled = true;
                        if (r.correct) input.classList.add("correct");
                        else { input.classList.add("incorrect"); allCorrect = false; }
                        attemptRecord.push({ symbol: r.symbol, guess: r.user_guess, correct: r.correct });
                    });

                    // ✅ Record attempt before removing submit button
                    attemptHistory.unshift(attemptRecord);

                    submitBtn.remove();
                    attemptsUsed++;
                    attemptsLeftEl.textContent = `Attempts left: ${maxAttempts - attemptsUsed}`;

                    if (attemptsUsed < maxAttempts && !allCorrect) {
                        addAttemptInputRow();
                    } else {
                        let msg = allCorrect ? "🎉 Congratulations! All words guessed!" : "❌ Game over! Max attempts reached.";
                        showNotification(msg, true);
                    }
                } else {
                    showNotification(result.error || "Error checking guesses");
                }
            } catch (err) {
                console.error(err);
                showNotification("Error connecting to server.");
            }
        });
    }

    // Render previous attempt rows
    function renderAttemptRow(attempt, attemptNum, top = true) {
        const rowDiv = document.createElement("div");
        rowDiv.className = "attempt-row";

        const attemptNumber = document.createElement("span");
        attemptNumber.className = "attempt-number";
        attemptNumber.textContent = `#${attemptNum}`;
        rowDiv.appendChild(attemptNumber);

        attempt.forEach(a => {
            const input = document.createElement("input");
            input.type = "text";
            input.className = "form-control guess-input";
            input.value = a.guess;
            input.disabled = true;
            input.maxLength = 25;
            if (a.correct) input.classList.add("correct");
            else input.classList.add("incorrect");
            rowDiv.appendChild(input);
        });

        if (top) attemptsSection.prepend(rowDiv);
        else attemptsSection.appendChild(rowDiv);
    }

    // Show notification with optional share link
    function showNotification(message, endGame = false) {
        notification.innerHTML = "";

        const msgSpan = document.createElement("span");
        msgSpan.textContent = message;
        notification.appendChild(msgSpan);

        if (endGame) {
            const shareDiv = document.createElement("div");
            shareDiv.className = "mt-2 d-flex flex-wrap align-items-center";

            const dataObj = { slotCount, symbols, attempts: attemptHistory };
            const jsonStr = JSON.stringify(dataObj);
            const encoded = btoa(unescape(encodeURIComponent(jsonStr)));
            const url = `${window.location.origin}${window.location.pathname}?data=${encoded}`;

            // Shareable hyperlink
            const shareLink = document.createElement("a");
            shareLink.href = url;
            shareLink.textContent = "View & share your game";
            shareLink.target = "_blank";
            shareLink.rel = "noopener noreferrer";
            shareLink.className = "me-2";
            shareLink.setAttribute("aria-label", "Shareable link to view your attempts");
            shareDiv.appendChild(shareLink);

            // Copy button
            const copyBtn = document.createElement("button");
            copyBtn.className = "btn btn-outline-secondary btn-sm";
            copyBtn.textContent = "Copy";
            copyBtn.setAttribute("aria-label", "Copy shareable link to clipboard");
            copyBtn.addEventListener("click", async () => {
                try {
                    await navigator.clipboard.writeText(url);
                    copyBtn.textContent = "Copied!";
                    setTimeout(() => (copyBtn.textContent = "Copy"), 2000);
                } catch (err) { console.error("Failed to copy link:", err); }
            });

            shareDiv.appendChild(copyBtn);
            notification.appendChild(shareDiv);
        }

        // Close button
        const closeBtn = document.createElement("button");
        closeBtn.type = "button";
        closeBtn.className = "btn-close ms-2";
        closeBtn.setAttribute("aria-label", "Close notification");
        closeBtn.addEventListener("click", hideNotification);
        notification.appendChild(closeBtn);

        notification.classList.remove("d-none");
    }

    function hideNotification() {
        notification.classList.add("d-none");
        notification.innerHTML = "";
    }
});
