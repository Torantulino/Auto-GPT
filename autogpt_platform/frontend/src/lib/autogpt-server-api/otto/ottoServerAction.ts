"use server";

import { revalidatePath } from "next/cache";
import BackendAPI from "../client";
import { OttoQuery, OttoResponse } from "../types";

const api = new BackendAPI();

export async function askOtto(
  query: string,
  conversationHistory: { query: string; response: string }[],
  userId: string,
  includeGraphData: boolean,
  graphId?: string,
): Promise<OttoResponse> {
  const messageId = `${Date.now()}-web`;

  const ottoQuery: OttoQuery = {
    query,
    conversation_history: conversationHistory,
    user_id: userId,
    message_id: messageId,
    include_graph_data: includeGraphData,
    graph_id: graphId,
  };

  try {
    const response = await api.askOtto(ottoQuery);
    revalidatePath("/build");
    return response;
  } catch (error) {
    console.error("Error in askOtto server action:", error);
    throw error;
  }
}
