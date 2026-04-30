export type FeedItem =
  | {
      type: "wall";
      id: number;
      created_at: string;
      body: string;
      wall_owner_id: number;
      author_id: number;
      author_display_name: string;
      wall_owner_display_name: string;
      attachment_url?: string;
      hidden_from_feed?: boolean;
    }
  | {
      type: "community";
      id: number;
      created_at: string;
      body: string;
      community_id: number;
      community_slug: string;
      community_name: string;
      author_id: number;
      author_display_name: string;
      attachment_url?: string;
      hidden_from_feed?: boolean;
    };

export interface FeedResponse {
  results: FeedItem[];
  next_offset: number | null;
}
