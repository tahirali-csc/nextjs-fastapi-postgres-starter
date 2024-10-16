"use client";
import Image from "next/image";
import Chatbot from "./chatbot"
import {useEffect} from "react";

type User = {
  id: string;
  name: string;
};

const apiUrl = process.env.NEXT_PUBLIC_API_URL;

export default async function Home() {
  // console.log("fetch", `${apiUrl}/users/me`);
  // const user: User = await fetch(`${apiUrl}/users/me`).then((res) =>
  //   res.json()
  // );



  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div>
        {/*Hello, {user.name}!*/}
      </div>
      <div>
        <Chatbot/>
      </div>
    </main>
  );
}
