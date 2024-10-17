"use client";
import React, {useEffect, useState} from "react";

interface Message {
  type: "user" | "bot";
  text: string;
}

const apiUrl = process.env.NEXT_PUBLIC_API_URL;

const Chatbot: React.FC =  () => {
    const [messages, setMessages] = useState<{ type: "user" | "bot"; text: string }[]>([]);
    const [input, setInput] = useState<string>("");
    const [userId, setUserId] = useState<string>("");

    let getCurrentUserId = async () => {
        const response = await fetch(`${apiUrl}/users/me`);
        if (!response.ok) {
            throw new Error(`unable to get user`);
        }
        const result = await response.json();
        return result.id;
    };

    let getUserMessages = async (userId: string) => {
        const response = await fetch(`${apiUrl}/messages/${userId}`);
        if (!response.ok) {
            throw new Error(`unable to get messages`);
        }
        const result = await response.json();
        return result.id;
    };



      useEffect(() => {
          setMessages([])
        const fetchData = async () => {
            try {
                let userId = await getCurrentUserId()
                setUserId(userId)

                // const botMessages = await fetch(`${apiUrl}/messages/1`);
                // if(!botMessages.ok) {
                //     return
                // }
                const botMessages = await getUserMessages(userId)
                const allMessages = await botMessages.json();

                console.log("setting....")
                for(const i in allMessages) {
                    let userMessage = {type: "user", text: allMessages[i].message}
                    setMessages((prev) => [...prev, userMessage]);

                    let reply = {type: "bot", text: allMessages[i].reply}
                    setMessages((prev) => [...prev, reply]);
                }
            } catch (error) {
                console.error("Error fetching data: ", error);
            }
        };

        fetchData();
      }, []);

    const handleSend = async () => {
        if (input.trim() === "") return; // Prevent sending empty messages

        const userMessage = { type: "user", text: input };

        const user= await fetch(`${apiUrl}/messages`,{
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                "message": input,
                "user": userId.toString(),
            }),
        });

        setMessages((prev) => [...prev, userMessage]);
        setInput(""); // Clear the input after sending

        // Simulate bot response
        const botResponse = { type: "bot", text: user.json() }; // Simple echo bot response
        setMessages((prev) => [...prev, botResponse]);
    };

    return (
        <div style={{
            maxWidth: "600px",
            margin: "20px auto",
            padding: "20px",
            border: "1px solid #ccc",
            borderRadius: "8px"
        }}>
            <h2>Simple Chatbox</h2>
            <div style={{
                height: "300px",
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
                style={{width: "80%", padding: "10px", color:"black"}}
                placeholder="Type a message..."
            />
            <button onClick={handleSend} style={{padding: "10px", marginLeft: "10px"}}>
                Send
            </button>
        </div>
    );
};

export default Chatbot;