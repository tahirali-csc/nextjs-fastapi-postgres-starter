"use client";
import React, {useEffect, useState} from "react";

const apiUrl = process.env.NEXT_PUBLIC_API_URL;

const Chatbot: React.FC = () => {
    const [messages, setMessages] = useState<{ type: "user" | "bot"; text: string }[]>([]);
    const [input, setInput] = useState<string>("");
    const [userId, setUserId] = useState<string>("");
    const [userName, setUserName] = useState<string>("");
    // work around as useEffect is called twice in dev mode!!. Seems like a know thing
    // but in prod, this will be called once
    let didInit: boolean = false;

    let [errorMessage, setErrorMessage] = useState<string>("");
    const [isProcessing, setIsProcessing] = useState<boolean>(false);

    let getCurrentUser = async () => {
        const response = await fetch(`${apiUrl}/users/me`);
        if (!response.ok) {
            throw new Error(`unable to get user`);
        }
        return await response.json();
    };

    let getUserMessages = async (userId: string) => {
        const response = await fetch(`${apiUrl}/messages/${userId}`);
        if (!response.ok) {
            throw new Error(`unable to get messages`);
        }
        return await response.json();
    };

    useEffect(() => {
        if (didInit) return;
        didInit = true;

        const fetchData = async () => {
            try {
                let currentUser = await getCurrentUser();
                setUserId(currentUser.id);
                setUserName(currentUser.name);

                const allMessages = await getUserMessages(currentUser.id);
                for (const i in allMessages) {
                    let userMessage = {type: "user", text: allMessages[i].message}
                    setMessages((prev) => [...prev, userMessage]);

                    let reply = {type: "bot", text: allMessages[i].reply}
                    setMessages((prev) => [...prev, reply]);
                }
            } catch (error) {
                setErrorMessage("Error getting user messages")
            }
        };

        setMessages([])
        setErrorMessage("")
        fetchData();
    }, []);

    const handleSend = async () => {
        if (input.trim() === "") return; // Prevent sending empty messages

        setErrorMessage("")
        setIsProcessing(true);

        try {
            const userMessage = {type: "user", text: input};
            const res = await fetch(`${apiUrl}/messages`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    "message": input,
                    "user": userId.toString(),
                }),
            });

            if (!res.ok) {
                setErrorMessage("unable to send message")
                return;
            }

            setMessages((prev) => [...prev, userMessage]);
            setInput(""); // Clear the input after sending

            // Print the bot response

            const botResponse = {type: "bot", text: res.json()}; // Simple echo bot response
            setMessages((prev) => [...prev, botResponse]);


            console.log("isProcessing:", isProcessing)
        } catch (error) {
            setErrorMessage("unable to process message")
        } finally {
            setIsProcessing(false);
        }
    };

    const isSendDisabled = () => {
        return input.trim().length == 0 || isProcessing;
    }

    return (
        <div>
            Hello, {userName}!
            <div style={{
                maxWidth: "600px",
                margin: "20px auto",
                padding: "20px",
                border: "1px solid #ccc",
                borderRadius: "8px"
            }}>
                <h2>Simple Chatbox</h2>
                <div style={{
                    height: "600px",
                    overflowY: "auto",
                    border: "1px solid #ccc",
                    padding: "10px",
                    borderRadius: "5px",
                    marginBottom: "10px"
                }}>
                    {messages.map((msg, index) => (
                        <div key={index} style={{textAlign: msg.type === "user" ? "right" : "left"}}>
                            <div style={{
                                display: "inline-block",
                                padding: "10px",
                                margin: "5px",
                                borderRadius: "5px",
                                color: "black",
                                backgroundColor: msg.type === "user" ? "#dcf8c6" : "#f1f1f1"
                            }}>
                                {msg.text}
                            </div>
                        </div>
                    ))}
                </div>
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)} // Update input state
                    style={{width: "80%", padding: "10px", color: "black"}}
                    placeholder="Type a message..."
                />
                <button onClick={handleSend} style={{
                    padding: "10px", marginLeft: "10px",
                    backgroundColor: isSendDisabled() ? 'gray' : 'blue'
                }}
                        disabled={isSendDisabled()}>
                    Send
                </button>
                <span style={{color: "red"}}>{errorMessage}</span>
            </div>
        </div>
    );
};

export default Chatbot;