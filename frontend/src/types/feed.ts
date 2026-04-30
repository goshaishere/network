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
    };

export interface FeedResponse {
  results: FeedItem[];
  next_offset: number | null;
}
