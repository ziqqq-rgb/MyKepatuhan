export type FilterOption = { value: string; label: string };

export const AUTHORITIES: FilterOption[] = [
  { value: "All", label: "All" },
  { value: "SSM", label: "SSM" },
  { value: "KKM", label: "KKM" },
  { value: "DBKL", label: "DBKL" },
  { value: "MPKj", label: "MPKj" },
  { value: "LHDN", label: "LHDN" },
  { value: "MyIPO", label: "MyIPO" },
];

export const TOPICS: FilterOption[] = [
  { value: "All", label: "All" },
  { value: "registration", label: "Registration" },
  { value: "tax", label: "Tax" },
  { value: "licensing", label: "Licensing" },
  { value: "zoning", label: "Zoning" },
  { value: "employment", label: "Employment" },
  { value: "compliance", label: "Compliance" },
];

export type UserMessage = { role: "user"; content: string; id: string };
export type AssistantMessage = {
  role: "assistant";
  content: string;
  citations?: import("@/lib/api").Citation[];
  id: string;
};
export type Message = UserMessage | AssistantMessage;