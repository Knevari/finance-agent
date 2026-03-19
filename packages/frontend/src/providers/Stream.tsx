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
  getMessagesMetadata: (message: Message) => any;
  setBranch: (branch: string) => void;
  patchMetadata: (metadata: any) => void;
  values: any;
  interrupt: any;
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

              // 1. Direct output
              if (data.output) {
                currentText += data.output;
              }
              // 2. Standardized messages array (usually one message per chunk)
              else if (data.messages && Array.isArray(data.messages) && data.messages.length > 0) {
                const msg = data.messages[data.messages.length - 1];
                if (msg.content !== undefined && msg.content !== null) {
                  if (typeof msg.content === 'string') {
                    // APPEND for streaming deltas
                    currentText += msg.content;
                  } else {
                    // Replace for complex content (e.g. tool results)
                    currentText = JSON.stringify(msg.content);
                  }
                }
              }
              // 3. Nested node output (legacy/alternative format)
              else {
                const nodeKey = Object.keys(data).find(key => data[key] && data[key].messages);
                if (nodeKey) {
                  const messages = data[nodeKey].messages;
                  if (Array.isArray(messages) && messages.length > 0) {
                    const msg = messages[messages.length - 1];
                    if (msg.content) {
                      // For node-based updates, we might want to replace because it's usually the final state of the node
                      currentText = typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content);
                    }
                  }
                } else if (!data.error) {
                  // Fallback for unknown shapes
                  // currentText += JSON.stringify(data); // Disabling this to avoid cluttering UI with JSON
                }
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

  const getMessagesMetadata = useCallback((_message: Message) => {
    return {
      branch: undefined,
      branchOptions: undefined,
      firstSeenState: undefined,
    };
  }, []);

  const setBranch = useCallback((_branch: string) => {
    // No-op for now
  }, []);

  const patchMetadata = useCallback((_metadata: any) => {
    // No-op for now
  }, []);

  return (
    <StreamContext.Provider
      value={{
        messages,
        isLoading,
        error,
        submit,
        stop,
        getMessagesMetadata,
        setBranch,
        patchMetadata,
        values: { messages }, // Basic values object
        interrupt: null, // Basic interrupt state
      }}
    >
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
