export interface WorkGroup {
  id: number;
  name: string;
  slug: string;
  description: string;
  members_count: number;
  my_role: string | null;
}

export interface WorkBoard {
  id: number;
  group: number;
  name: string;
  preset: "generic_pm" | "it_sdlc" | "custom";
}

export interface WorkColumn {
  id: number;
  board: number;
  title: string;
  semantic: string;
  position: number;
}

export interface WorkTask {
  id: number;
  board: number;
  column: number;
  title: string;
  description: string;
  assignee: number | null;
  due_date: string | null;
  position: number;
}
