import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  messages: [{ role: 'agent', content: 'Hello! I am your AI Co-pilot. How can I help you log your HCP interaction today?' }],
  isLoading: false,
};

export const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addMessage: (state, action) => {
      state.messages.push(action.payload);
    },
    setLoading: (state, action) => {
      state.isLoading = action.payload;
    }
  }
});

export const { addMessage, setLoading } = chatSlice.actions;
export default chatSlice.reducer;
