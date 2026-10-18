export type ConnectionState = "not_connected" | "connecting" | "connected" | "error";

export interface SensorStatus {
  id: string;
  name: string;
  measures: string;
  state: ConnectionState;
}
