import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { updateFormField, clearForm, addLog } from '../slices/interactionsSlice';
import { FileText, Save, RefreshCw } from 'lucide-react';
import axios from 'axios';

const FormPanel = () => {
  const dispatch = useDispatch();
  const formState = useSelector((state) => state.interactions.currentForm);

  const handleChange = (e) => {
    const { name, value } = e.target;
    dispatch(updateFormField({ field: name, value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      await axios.post('http://localhost:8000/api/chat', {
        message: `
        Log interaction:
        Doctor: ${formState.hcp_id}
        Topics: ${formState.topics}
        Samples: ${formState.samples}
        Sentiment: ${formState.sentiment}
        Next Steps: ${formState.next_steps}
        Notes: ${formState.notes}
      `
      });

      alert('✅ Interaction saved via AI');
      dispatch(addLog(formState));

    } catch (error) {
      console.error(error);
      alert('❌ Failed to save interaction');
    }
  };

  return (
    <section className="panel">
      <header className="panel-header">
        <FileText size={20} style={{ color: 'var(--primary-color)' }} />
        <h2>Structured Form Log</h2>
      </header>
      <div className="panel-body">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">HCP ID / Name</label>
            <input
              type="text"
              name="hcp_id"
              className="form-input"
              value={formState.hcp_id}
              onChange={handleChange}
              placeholder="e.g. Dr. John Smith"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Topics Discussed</label>
            <input
              type="text"
              name="topics"
              className="form-input"
              value={formState.topics}
              onChange={handleChange}
              placeholder="e.g. Efficacy, Side effects"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Samples Provided</label>
            <input
              type="text"
              name="samples"
              className="form-input"
              value={formState.samples}
              onChange={handleChange}
              placeholder="e.g. 5 boxes Drug X"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Sentiment</label>
            <select
              name="sentiment"
              className="form-select"
              value={formState.sentiment}
              onChange={handleChange}
            >
              <option value="Positive">Positive</option>
              <option value="Neutral">Neutral</option>
              <option value="Negative">Negative</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Next Steps / Follow-up</label>
            <input
              type="text"
              name="next_steps"
              className="form-input"
              value={formState.next_steps}
              onChange={handleChange}
              placeholder="e.g. Send literature on Monday"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Raw / Additional Notes</label>
            <textarea
              name="notes"
              className="form-textarea"
              value={formState.notes}
              onChange={handleChange}
              placeholder="Any other details..."
            ></textarea>
          </div>

          <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
            <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>
              <Save size={18} />
              Save Log
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => dispatch(clearForm())}
            >
              <RefreshCw size={18} />
              Clear
            </button>
          </div>
        </form>
      </div>
    </section>
  );
};

export default FormPanel;
