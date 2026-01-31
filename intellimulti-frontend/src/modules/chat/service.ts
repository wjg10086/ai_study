import { ChatRequestPayload } from './types';

const API_BASE_URL = 'http://localhost:8000';

export async function streamChat(
  payload: ChatRequestPayload,
  onChunk: (content: string) => void,
  onComplete: (fullContent: string) => void,
  onError: (error: any) => void
) {
  const formData = new FormData();

  // Add content_blocks and history as JSON strings
  // Backend expects 'content_blocks' and 'history' as form fields (strings)
  formData.append('content_blocks', JSON.stringify(payload.content_blocks));
  formData.append('history', JSON.stringify(payload.history));

  if (payload.image_file) {
    formData.append('image_file', payload.image_file);
  }
  if (payload.audio_file) {
    formData.append('audio_file', payload.audio_file);
  }
  if (payload.pdf_file) {
    formData.append('pdf_file', payload.pdf_file);
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    if (!response.body) {
      throw new Error('No response body');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let fullContent = '';
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      buffer += chunk;
      
      const lines = buffer.split('\n\n');
      // Keep the last part if it's incomplete
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const dataStr = line.slice(6);
          
          try {
            const data = JSON.parse(dataStr);
            if (data.type === 'content_delta') {
              fullContent += data.content;
              onChunk(fullContent);
            } else if (data.type === 'message_complete') {
               // Backend sends full content in message_complete
               if (data.full_content) {
                   fullContent = data.full_content; 
               }
               onComplete(fullContent);
            } else if (data.type === 'error') {
              onError(data.error);
            }
          } catch (e) {
            console.warn('Failed to parse SSE data', e);
          }
        }
      }
    }
  } catch (error) {
    onError(error);
  }
}
