function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value.trim();

    if (message === "") {
        return;
    }

    // Show user's message
    addMessage(message, "user");

    // Clear input
    input.value = "";

    // Send message to Flask backend
    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            message: message
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Server error");
        }

        return response.json();
    })
    .then(data => {
        // Show AI response
        addMessage(data.reply, "bot");
    })
    .catch(error => {
        console.error("Error:", error);

        addMessage(
            "Sorry, something went wrong. Please try again.",
            "bot"
        );
    });
}


function sendQuickMessage(message) {

    const input = document.getElementById("user-input");

    if (!input) {
        return;
    }

    input.value = message;

    sendMessage();
}


function addMessage(message, sender) {

    const chatBox = document.getElementById("chat-box");

    if (!chatBox) {
        return;
    }

    /*
     * Convert Markdown-style bold:
     * **text**
     *
     * into HTML:
     * <strong>text</strong>
     */

    const formattedMessage = message
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\n/g, "<br>");


    const messageDiv = document.createElement("div");


    // USER MESSAGE
    if (sender === "user") {

        messageDiv.className = "message user-message";

        messageDiv.innerHTML = `
            <div class="message-content">
                <p>${formattedMessage}</p>
            </div>
        `;
    }


    // BOT MESSAGE
    else {

        messageDiv.className = "message bot-message";

        messageDiv.innerHTML = `
            <div class="avatar">🤖</div>

            <div class="message-content">
                <p>${formattedMessage}</p>
            </div>
        `;
    }


    // Add message to chat
    chatBox.appendChild(messageDiv);


    // Automatically scroll to latest message
    chatBox.scrollTop = chatBox.scrollHeight;
}


document.addEventListener("DOMContentLoaded", function () {

    const input = document.getElementById("user-input");


    // ENTER KEY
    if (input) {

        input.addEventListener("keypress", function (event) {

            if (event.key === "Enter") {

                event.preventDefault();

                sendMessage();
            }

        });
    }


    // USER TYPE FROM LANDING PAGE
    const userType = localStorage.getItem("userType");

    if (userType) {

        console.log("User type:", userType);

        localStorage.removeItem("userType");
    }


    // INITIAL QUESTION FROM LANDING PAGE
    const initialQuestion =
        localStorage.getItem("initialQuestion");


    if (initialQuestion && input) {

        input.value = initialQuestion;

        localStorage.removeItem("initialQuestion");

        sendMessage();
    }

});