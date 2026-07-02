export { getToken, setToken, clearToken, apiFetch } from "./client";
export { apiRegister, apiLogin, apiGetMe, apiOAuthLogin } from "./auth";
export type { AuthResponse, UserProfile } from "./auth";
export { apiQuery } from "./query";
export type { QueryResponse, Citation } from "./query";
export { apiUploadDocument, apiGetJobStatus, apiGetDocuments } from "./ingest";
export type { IngestJob, IngestedDocument } from "./ingest";
export {
  apiCreateConversation,
  apiListConversations,
  apiGetConversationMessages,
  apiDeleteConversation,
} from "./conversations";
export type { Conversation, ConversationMessage } from "./conversations";