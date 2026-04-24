export interface ConversationRow {
  id: number;
  kind: string;
  other_user_id: number | null;
  other_display_name: string | null;
  created_at: string;
}

export interface ChatMessage {
  id: number;
  sender_id: number;
  body: string;
  created_at: string;
}

export interface CursorPage<T> {
  next: string | null;
  previous: string | null;
  results: T[];
}
