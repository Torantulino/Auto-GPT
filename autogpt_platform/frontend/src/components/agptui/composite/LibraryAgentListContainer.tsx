"use client";
import { useEffect, useState, useCallback } from "react";
import { LibraryAgentCard } from "../LibraryAgentCard";
import { useBackendAPI } from "@/lib/autogpt-server-api/context";
import { GraphMeta } from "@/lib/autogpt-server-api";
import { useThreshold } from "@/hooks/useThreshold";
import { useLibraryPageContext } from "../providers/LibraryAgentProvider";

interface LibraryAgentListContainerProps {}

export type AgentStatus =
  | "healthy"
  | "something wrong"
  | "waiting for trigger"
  | "Nothing running";

/**
 * LibraryAgentListContainer is a React component that displays a grid of library agents with infinite scroll functionality.
 */

const LibraryAgentListContainer: React.FC<
  LibraryAgentListContainerProps
> = ({}) => {
  const [nextToken, setNextToken] = useState<number>(1);
  const [loadingMore, setLoadingMore] = useState(false);

  const api = useBackendAPI();
  const { agents, setAgents, setAgentLoading, agentLoading } =
    useLibraryPageContext();

  const fetchAgents = useCallback(
    async (page: number) => {
      try {
        const response = await api.listLibraryAgents(
          page === 0 ? {} : { page: page },
        );
        if (page) {
          setAgents((prevAgent) => [...prevAgent, ...response.agents]);
        } else {
          setAgents(response.agents);
        }
        setNextToken(page + 1);
      } finally {
        setAgentLoading(false);
        setLoadingMore(false);
      }
    },
    [api, setAgents, setAgentLoading],
  );

  useEffect(() => {
    fetchAgents(0);
  }, [fetchAgents]);

  const handleInfiniteScroll = useCallback(
    (scrollY: number) => {
      if (!nextToken || loadingMore) return;

      const { scrollHeight, clientHeight } = document.documentElement;
      const SCROLL_THRESHOLD = 20;
      const FETCH_DELAY = 1000;

      if (scrollY + clientHeight >= scrollHeight - SCROLL_THRESHOLD) {
        setLoadingMore(true);
        setTimeout(() => fetchAgents(nextToken), FETCH_DELAY);
      }
    },
    [nextToken, loadingMore, fetchAgents],
  );

  useThreshold(handleInfiniteScroll, 50);

  const LoadingSpinner = () => (
    <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-t-2 border-neutral-800" />
  );

  return (
    <div className="px-2">
      {agentLoading ? (
        <div className="flex h-[200px] items-center justify-center">
          <LoadingSpinner />
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-4">
            {agents?.map((agent) => (
              <LibraryAgentCard
                key={agent.id}
                id={agent.id}
                can_access_graph={agent.can_access_graph}
                creator_name={agent.creator_name}
                creator_image_url={agent.creator_image_url}
                image_url={agent.image_url}
                name={agent.name}
                description={agent.description}
                input_schema={agent.input_schema}
                agent_id={agent.agent_id}
                agent_version={agent.agent_version}
                status={agent.status}
                updated_at={agent.updated_at}
                new_output={agent.new_output}
                is_latest_version={agent.is_latest_version}
              />
            ))}
          </div>
          {loadingMore && (
            <div className="flex items-center justify-center py-4">
              <LoadingSpinner />
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default LibraryAgentListContainer;
