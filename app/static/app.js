const questionInput = document.getElementById("question");
const sendButton = document.getElementById("send-button");

const knowledgeFileInput = document.getElementById("knowledge-file");
const uploadButton = document.getElementById("upload-button");
const uploadStatus = document.getElementById("upload-status");

const messagesContainer = document.getElementById("messages");
const chatContainer = document.querySelector(".chat");

const toggleUploadButton =
    document.getElementById("toggle-upload-button");

const uploadToggleIcon =
    document.getElementById("upload-toggle-icon");

const uploadToggleText =
    document.getElementById("upload-toggle-text");

const uploadPanel =
    document.getElementById("upload-panel");

const selectedFileName =
    document.getElementById("selected-file-name");

async function configureFeatures() {
    try {
        const response = await fetch("/config");

        if (!response.ok) {
            return;
        }

        const config = await response.json();

        toggleUploadButton.hidden =
            !config.ingestion_enabled;

    } catch (error) {
        console.error(
            "Failed to load public configuration"
        );
    }
}

configureFeatures();

function scrollChatToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

sendButton.addEventListener("click", async () => {
    const question = questionInput.value.trim();

    if (!question) {
        return;
    }

    const userMessage = document.createElement("div");
    userMessage.className = "message user-message";

    const userLabel = document.createElement("div");
    userLabel.className = "message-label";
    userLabel.textContent = "You";

    const userText = document.createElement("div");
    userText.textContent = question;

    userMessage.appendChild(userLabel);
    userMessage.appendChild(userText);

    messagesContainer.appendChild(userMessage);
    scrollChatToBottom();

    questionInput.value = "";
    sendButton.disabled = true;

    const thinkingMessage = document.createElement("div");
    thinkingMessage.className = "message assistant-message";

    const thinkingLabel = document.createElement("div");
    thinkingLabel.className = "message-label";
    thinkingLabel.textContent = "CloudOps AI";

    const thinkingText = document.createElement("div");
    thinkingText.className = "answer";
    thinkingText.textContent = "Thinking...";

    thinkingMessage.appendChild(thinkingLabel);
    thinkingMessage.appendChild(thinkingText);

    messagesContainer.appendChild(thinkingMessage);
    scrollChatToBottom();

    try {
        const response = await fetch("/rag/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                question: question,
            }),
        });

        if (!response.ok) {
            throw new Error("Failed to get response");
        }

        const data = await response.json();

        thinkingText.textContent = data.answer;

        if (data.sources && data.sources.length > 0) {
            const sourcesContainer = document.createElement("div");
            sourcesContainer.className = "sources";

            const sourcesTitle = document.createElement("p");
            sourcesTitle.textContent = "Sources:";

            sourcesContainer.appendChild(sourcesTitle);

            data.sources.forEach((source) => {
                const sourceElement = document.createElement("div");
                sourceElement.className = "source-item";

                sourceElement.textContent =
                    `${source.name} · chunk ${source.chunk_index}`;

                sourcesContainer.appendChild(sourceElement);
            });

            thinkingMessage.appendChild(sourcesContainer);
            scrollChatToBottom();
        }

    } catch (error) {
        thinkingText.textContent =
            "Something went wrong. Please try again.";

        console.error(error);

    } finally {
        sendButton.disabled = false;
    }
});


questionInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendButton.click();
    }
});


toggleUploadButton.addEventListener("click", () => {
    uploadPanel.classList.toggle("hidden");

    const isOpen = !uploadPanel.classList.contains("hidden");

    uploadToggleText.textContent =
        isOpen ? "Close upload" : "Upload document";

    uploadToggleIcon.textContent =
        isOpen ? "x" : "+";

    toggleUploadButton.classList.toggle("active", isOpen);
});


knowledgeFileInput.addEventListener("change", () => {
    const file = knowledgeFileInput.files[0];

    if (file) {
        selectedFileName.textContent = file.name;
    } else {
        selectedFileName.textContent = "No file selected";
    }
});


uploadButton.addEventListener("click", async () => {
    const file = knowledgeFileInput.files[0];

    if (!file) {
        uploadStatus.className = "upload-error";
        uploadStatus.textContent =
            "Please select a Markdown file.";
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
        uploadButton.disabled = true;

        uploadStatus.className = "";
        uploadStatus.textContent = "Uploading...";

        const response = await fetch("/knowledge/upload", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error("Upload failed");
        }

        const data = await response.json();

        uploadStatus.className = "upload-success";
        uploadStatus.textContent =
            `${data.file_name} uploaded successfully · ${data.chunks_stored} chunks stored`;

        knowledgeFileInput.value = "";
        selectedFileName.textContent = "No file selected";

    } catch (error) {
        uploadStatus.className = "upload-error";
        uploadStatus.textContent =
            "Upload failed. Please try again.";

        console.error(error);

    } finally {
        uploadButton.disabled = false;
    }
});