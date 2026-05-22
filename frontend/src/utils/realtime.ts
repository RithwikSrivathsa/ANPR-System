import { useAnprStore } from "../store/useAnprStore";

export function connectRealtime() {
  const wsUrl = import.meta.env.VITE_WS_URL ?? "ws://localhost:8000/ws/detections";
  let socket: WebSocket | undefined;
  let stopped = false;

  const connect = () => {
    socket = new WebSocket(wsUrl);
    socket.onopen = () => useAnprStore.setState({ connected: true });
    socket.onclose = () => {
      useAnprStore.setState({ connected: false });
      if (!stopped) window.setTimeout(connect, 2500);
    };
    socket.onmessage = (message) => {
      const event = JSON.parse(message.data);
      useAnprStore.getState().pushEvent(event);
    };
  };
  connect();
  return () => {
    stopped = true;
    socket?.close();
  };
}
