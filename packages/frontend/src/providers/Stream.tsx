import React, {
  createContext,
  useContext,
  ReactNode,
  useState,
  useCallback,
} from "react";
import { type Message } from "@langchain/langgraph-sdk";
import { v4 as uuidv4 } from "uuid";

// Mocking the shape of the LangGraph SDK stream interface for our Thread UI
export type StreamContextType = {
  messages: Message[];
  isLoading: boolean;
  error: any;
  submit: (input: any, options?: any) => void;
  stop: () => void;
};

const StreamContext = createContext<StreamContextType | undefined>(undefined);

export const StreamProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<any>(null);
  const [abortController, setAbortController] = useState<AbortController | null>(null);

  const stop = useCallback(() => {
    if (abortController) {
      abortController.abort();
      setAbortController(null);
      setIsLoading(false);
    }
  }, [abortController]);

  const submit = useCallback(async (input: any, options?: any) => {
    if (input?.messages) {
      // Optimistically update messages
      setMessages((prev) => {
        // Find the new human message to append
        const newMsg = input.messages[input.messages.length - 1];
        if (newMsg) return [...prev, newMsg];
        return prev;
      });
    }

    const humanMessageText =
      input?.messages?.[input.messages.length - 1]?.content?.[0]?.text || "Hello";

    setIsLoading(true);
    setError(null);
    const controller = new AbortController();
    setAbortController(controller);

    try {
      // Extract client_user_id and item_id if they were injected in config
      const config = options?.config?.configurable || {};

      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: humanMessageText,
          client_user_id: config.client_user_id,
          item_id: config.item_id,
        }),
        signal: controller.signal,
      });

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantMsgId = uuidv4();
      let currentText = "";

      // Add a placeholder AI message
      setMessages((prev) => [
        ...prev,
        { id: assistantMsgId, type: "ai", content: [] } as Message,
      ]);

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n\n");
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const dataStr = line.replace("data: ", "");
            if (dataStr === "[DONE]") {
              break;
            }
            try {
              const data = JSON.parse(dataStr);
              // LangChain agent stream chunk logic (usually {"messages": [AI Message]} or {"output": "..."})
              if (data.output) {
                currentText += data.output;
              } else if (data.messages && data.messages.length > 0) {
                const msg = data.messages[data.messages.length - 1];
                if (msg.content) {
                  currentText = msg.content;
                }
              } else {
                // Basic concatenation fallback
                currentText += JSON.stringify(data);
              }

              // Update the AI message
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantMsgId
                    ? { ...m, content: [{ type: "text", text: currentText }] }
                    : m
                )
              );
            } catch (e) {
              // Not JSON
            }
          }
        }
      }
    } catch (err: any) {
      if (err.name !== "AbortError") {
        setError(err);
      }
    } finally {
      setIsLoading(false);
      setAbortController(null);
    }
  }, []);

  return (
    <StreamContext.Provider value={{ messages, isLoading, error, submit, stop }}>
      {children}
    </StreamContext.Provider>
  );
};

export const useStreamContext = (): StreamContextType => {
  const context = useContext(StreamContext);
  if (context === undefined) {
    throw new Error("useStreamContext must be used within a StreamProvider");
  }
  return context;
};

export default StreamContext;
