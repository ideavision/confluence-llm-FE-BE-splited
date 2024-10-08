"use client";

import {
  FiLogOut,
  FiWind,
  FiMoreHorizontal,
  FiPlusSquare,
  FiSearch,
  FiTool,
  FiPlus
} from "react-icons/fi";
import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { User } from "@/lib/types";
import { logout } from "@/lib/user";
import { BasicClickable, BasicSelectable } from "@/components/BasicClickable";
import Image from "next/image";
import { ChatSessionDisplay } from "./SessionDisplay";
import { ChatSession } from "../interfaces";
import { groupSessionsByDateRange } from "../lib";
import { HEADER_PADDING } from "@/lib/constants";

interface ChatSidebarProps {
  existingChats: ChatSession[];
  currentChatId: number | null;
  user: User | null;
}

export const ChatSidebar = ({
  existingChats,
  currentChatId,
  user,
}: ChatSidebarProps) => {
  const router = useRouter();

  const groupedChatSessions = groupSessionsByDateRange(existingChats);

  const [userInfoVisible, setUserInfoVisible] = useState(false);
  const userInfoRef = useRef<HTMLDivElement>(null);

  const handleLogout = () => {
    logout().then((isSuccess) => {
      if (!isSuccess) {
        alert("Failed to logout");
      }
      router.push("/auth/login");
    });
  };

  // hides logout popup on any click outside
  const handleClickOutside = (event: MouseEvent) => {
    if (
      userInfoRef.current &&
      !userInfoRef.current.contains(event.target as Node)
    ) {
      setUserInfoVisible(false);
    }
  };

  useEffect(() => {
    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return (
    <div
      className={`
        w-72
        2xl:w-80
        bg-blue-100
        ${HEADER_PADDING}
        border-r 
        border-border 
        flex 
        flex-col 
        h-screen
        transition-transform`}
      id="chat-sidebar"
    >
      <Link href="/chat" className="mx-3 mt-5">
      <BasicClickable fullWidth>
          <div className="flex text-sm bg-blue-200 p-1.5">
            <FiPlus className="my-auto mr-3 bg-blue-100 text-xl" /> New Chat
          </div>
        </BasicClickable>
      </Link>

      <div className="mt-1 pb-1  m-1 ml-3 overflow-y-auto h-full">
        {Object.entries(groupedChatSessions).map(
          ([dateRange, chatSessions]) => {
            if (chatSessions.length > 0) {
              return (
                <div key={dateRange}>
                  <div className="text-xs text-subtle flex pb-0.5 mb-1.5 mt-5 font-bold">
                    {dateRange}
                  </div>
                  {chatSessions.map((chat) => {
                    const isSelected = currentChatId === chat.id;
                    return (
                      <div key={chat.id} className="mr-3">
                        <ChatSessionDisplay
                          chatSession={chat}
                          isSelected={isSelected}
                        />
                      </div>
                    );
                  })}
                </div>
              );
            }
          }
        )}
        {/* {existingChats.map((chat) => {
          const isSelected = currentChatId === chat.id;
          return (
            <div key={chat.id} className="mr-3">
              <ChatSessionDisplay chatSession={chat} isSelected={isSelected} />
            </div>
          );
        })} */}
      </div>

      <div
        className="mt-auto py-2 border-t border-border px-3"
        ref={userInfoRef}
      >
        <div className="relative text-strong">
          {userInfoVisible && (
            <div
              className={
                (user ? "translate-y-[-110%]" : "translate-y-[-115%]") +
                " absolute top-0 bg-background border border-border z-30 w-full rounded text-strong text-sm"
              }
            >
              {/* <Link
                href="/search"
                className="flex py-3 px-4 cursor-pointer hover:bg-hover"
              >
                <FiSearch className="my-auto mr-2" />
               Search
              </Link> */}
              <Link
                href="/chat"
                className="flex py-3 px-4 cursor-pointer hover:bg-hover"
              >
                <FiWind className="my-auto mr-2" />
                PayserAi Chat
              </Link>
              {(!user || user.role === "admin") && (
                <Link
                  href="/admin/indexing/status"
                  className="flex py-3 px-4 cursor-pointer border-t border-border hover:bg-hover"
                >
                  <FiTool className="my-auto mr-2" />
                  Admin Panel
                </Link>
              )}
              {user && (
                <div
                  onClick={handleLogout}
                  className="flex py-3 px-4 cursor-pointer border-t border-border rounded hover:bg-hover"
                >
                  <FiLogOut className="my-auto mr-2" />
                  Log out
                </div>
              )}
            </div>
          )}
          <BasicSelectable fullWidth selected={false}>
            <div
              onClick={() => setUserInfoVisible(!userInfoVisible)}
              className="flex h-8"
            >
              <div className="my-auto mr-2 bg-user rounded-lg px-1.5">
                {user && user.email ? user.email[0].toUpperCase() : "A"}
              </div>
              <p className="my-auto">
                {user ? user.email : "Anonymous Possum"}
              </p>
              <FiMoreHorizontal className="my-auto ml-auto mr-2" size={20} />
            </div>
          </BasicSelectable>
        </div>
      </div>
    </div>
  );
};
