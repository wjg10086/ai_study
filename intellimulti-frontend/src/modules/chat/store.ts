import { create } from 'zustand';
import { Message, ChatMode } from './types';

interface ChatState {
  histories: Record<ChatMode, Message[]>;
  isLoading: boolean;
  
  addMessage: (mode: ChatMode, message: Message) => void;
  updateLastMessage: (mode: ChatMode, content: string) => void;
  setLoading: (loading: boolean) => void;
  clearHistory: (mode: ChatMode) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  histories: {
    qa: [],
    image: [],
    audio: [],
    pdf: []
  },
  isLoading: false,
  
  addMessage: (mode, message) => set((state) => ({
    histories: {
      ...state.histories,
      [mode]: [...(state.histories[mode] || []), message]
    }
  })),
  
  updateLastMessage: (mode, content) => set((state) => {
    const currentHistory = state.histories[mode] || [];
    if (currentHistory.length === 0) return state;
    
    const newHistory = [...currentHistory];
    newHistory[newHistory.length - 1] = {
      ...newHistory[newHistory.length - 1],
      content
    };
    
    return {
      histories: {
        ...state.histories,
        [mode]: newHistory
      }
    };
  }),
  
  setLoading: (isLoading) => set({ isLoading }),
  
  clearHistory: (mode) => set((state) => ({
    histories: {
      ...state.histories,
      [mode]: []
    }
  }))
}));
