/** Ответ GET/PATCH /profiles/me/ */
export interface ProfileMe {
  email: string;
  display_name: string;
  bio: string;
  avatar: string;
  locale: string;
  privacy: "public" | "private";
  default_landing: string;
  updated_at: string;
}

export interface ProfilePublic {
  display_name: string;
  bio: string;
  avatar: string;
  locale: string;
  privacy: "public" | "private";
}

export type DashboardWidgetType = "note" | "link";

export interface DashboardWidgetBase {
  id: string;
  pinned?: boolean;
}

export interface DashboardNoteWidget extends DashboardWidgetBase {
  type: "note";
  title: string;
  body: string;
}

export interface DashboardLinkWidget extends DashboardWidgetBase {
  type: "link";
  title: string;
  url: string;
}

export type DashboardWidget = DashboardNoteWidget | DashboardLinkWidget;

export interface DashboardLayoutPayload {
  version?: number;
  widgets: DashboardWidget[];
}

export interface WallPost {
  id: number;
  wall_owner_id: number;
  author_id: number;
  author_display_name: string;
  body: string;
  created_at: string;
  updated_at: string;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
