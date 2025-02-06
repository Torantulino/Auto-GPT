"use client";

import * as React from "react";
import { PublishAgentPopout } from "./composite/PublishAgentPopout";
interface BecomeACreatorProps {
  title?: string;
  description?: string;
  buttonText?: string;
  onButtonClick?: () => void;
}

export const BecomeACreator: React.FC<BecomeACreatorProps> = ({
  title = "Become a creator",
  description = "Join a community where your AI creations can inspire, engage, and be downloaded by users around the world.",
  buttonText = "Upload your agent",
  onButtonClick,
}) => {
  const handleButtonClick = () => {
    onButtonClick?.();
    console.log("Become A Creator clicked");
  };

  return (
    <div className="relative mx-auto h-auto min-h-[300px] w-full max-w-[1360px] md:min-h-[400px] lg:h-[459px]">
      {/* Top border */}
      <div className="top-0 left-0 h-px w-full bg-gray-200 dark:bg-gray-700" />

      {/* Title */}
      <h2 className="font-poppins underline-from-font decoration-skip-ink-none mt-[25px] mb-[77px] text-left text-[18px] leading-[28px] font-semibold text-neutral-800 dark:text-neutral-200">
        {title}
      </h2>

      {/* Content Container */}
      <div className="absolute top-1/2 left-1/2 w-full max-w-[900px] -translate-x-1/2 -translate-y-1/2 px-4 pt-16 text-center md:px-6 lg:px-0">
        <h2 className="font-poppins underline-from-font decoration-skip-ink-none mb-6 text-center text-[48px] leading-[54px] font-semibold tracking-[-0.012em] text-neutral-950 md:mb-8 lg:mb-12 dark:text-neutral-50">
          Build AI agents and share
          <br />
          <span className="text-violet-600 dark:text-violet-400">
            your
          </span>{" "}
          vision
        </h2>

        <p className="font-geist mx-auto mb-8 max-w-[90%] text-lg leading-relaxed font-normal text-neutral-700 md:mb-10 md:text-xl md:leading-loose lg:mb-14 lg:text-2xl dark:text-neutral-300">
          {description}
        </p>

        <PublishAgentPopout
          trigger={
            <button
              onClick={handleButtonClick}
              className="inline-flex h-[48px] cursor-pointer items-center justify-center rounded-[38px] bg-neutral-800 px-8 py-3 transition-colors hover:bg-neutral-700 md:h-[56px] md:px-10 md:py-4 lg:h-[68px] lg:px-12 lg:py-5 dark:bg-neutral-700 dark:hover:bg-neutral-600"
            >
              <span className="font-poppins text-base leading-normal font-medium whitespace-nowrap text-neutral-50 md:text-lg md:leading-relaxed lg:text-xl lg:leading-7">
                {buttonText}
              </span>
            </button>
          }
        />
      </div>
    </div>
  );
};
