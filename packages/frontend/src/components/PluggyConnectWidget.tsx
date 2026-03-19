"use client";
import React, { useState, useCallback } from 'react';
import { PluggyConnect } from 'react-pluggy-connect';
import { Button } from './ui/button';
import { toast } from 'sonner';

export function PluggyConnectWidget({
    clientUserId,
    onConnect
}: {
    clientUserId: string,
    onConnect: (itemId: string) => void
}) {
    const [connectToken, setConnectToken] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleOpen = useCallback(async () => {
        try {
            setIsLoading(true);
            // Calls the FastAPI endpoint we created earlier
            const res = await fetch("http://localhost:8000/pluggy/token", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ client_user_id: clientUserId })
            });
            if (!res.ok) {
                throw new Error("Failed to fetch connect token");
            }
            const data = await res.json();
            setConnectToken(data.accessToken);
        } catch (e: any) {
            console.error(e);
            toast.error("Error launching Connect Widget: " + e.message);
        } finally {
            setIsLoading(false);
        }
    }, [clientUserId]);

    return (
        <>
            <Button
                variant="outline"
                onClick={handleOpen}
                disabled={isLoading || !!connectToken}
            >
                {isLoading ? "Loading..." : "Connect Bank"}
            </Button>
            {connectToken && (
                <PluggyConnect
                    connectToken={connectToken}
                    includeSandbox={true}
                    onSuccess={async (itemData) => {
                        onConnect(itemData.item.id);
                        setConnectToken(null);
                        toast.success("Bank connected successfully! Syncing data...");

                        try {
                            await fetch("http://localhost:8000/pluggy/sync", {
                                method: "POST",
                                headers: { "Content-Type": "application/json" },
                                body: JSON.stringify({
                                    client_user_id: clientUserId,
                                    item_id: itemData.item.id
                                })
                            });
                            toast.success("Data synced successfully!");
                        } catch (e) {
                            console.error("Failed to sync data:", e);
                            toast.error("Connected, but failed to sync data.");
                        }
                    }}
                    onError={(e) => {
                        console.error("Pluggy error:", e);
                        toast.error("Error connecting to bank.");
                        setConnectToken(null);
                    }}
                    onClose={() => setConnectToken(null)}
                />
            )}
        </>
    );
}
