export type ContentType = 'text' | 'image' | 'audio';

export interface ContentBlock {
  type: ContentType;
  content: string; // Text content or base64/url for display (though backend might not need base64 for file uploads if sent as file)
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  content_blocks?: ContentBlock[]; // For user messages with multi-modal content
  timestamp: string;
  references?: any[]; // For PDF references
}

export interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  updatedAt: string;
}

export interface ChatRequestPayload {
  content_blocks: ContentBlock[];
  history: any[]; // Backend expects history as list of dicts
  image_file?: File | null;
  audio_file?: File | null;
  pdf_file?: File | null;
}
