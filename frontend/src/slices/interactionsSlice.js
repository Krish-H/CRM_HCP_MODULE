import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  logs: [],
  currentForm: {
    hcp_id: '',
    topics: '',
    samples: '',
    sentiment: 'Positive',
    next_steps: '',
    notes: ''
  }
};

export const interactionsSlice = createSlice({
  name: 'interactions',
  initialState,
  reducers: {
    updateFormField: (state, action) => {
      const { field, value } = action.payload;
      state.currentForm[field] = value;
    },
    addLog: (state, action) => {
      state.logs.push(action.payload);
      // Reset form
      state.currentForm = initialState.currentForm;
    },
    clearForm: (state) => {
      state.currentForm = initialState.currentForm;
    }
  }
});

export const { updateFormField, addLog, clearForm } = interactionsSlice.actions;
export default interactionsSlice.reducer;
