export interface CommunityListItem {
  id: number;
  name: string;
  slug: string;
  description: string;
  is_open: boolean;
  members_count: number;
  created_at: string;
}

export interface CommunityDetail {
  id: number;
  name: string;
  slug: string;
  description: string;
  is_open: boolean;
  members_count: number;
  created_at: string;
  creator_id: number | null;
  is_member: boolean;
}

export interface CommunityPost {
  id: number;
  author_id: number;
  body: string;
  created_at: string;
}

export interface PaginatedCommunities {
  count: number;
  next: string | null;
  previous: string | null;
  results: CommunityListItem[];
}

export interface PaginatedPosts {
  count: number;
  next: string | null;
  previous: string | null;
  results: CommunityPost[];
}
