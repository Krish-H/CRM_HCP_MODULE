import React, { useState, useRef, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { addMessage, setLoading } from '../slices/chatSlice';
import { updateFormField } from '../slices/interactionsSlice';
import { Send, Sparkles } from 'lucide-react';
import axios from 'axios';

const renderMessageContent = (content) => {
  if (typeof content !== 'string') return content;
  return content.split('\n').map((line, i) => {
    const parts = line.split(/(\*\*.*?\*\*)/g);
    return (
      <React.Fragment key={i}>
        {parts.map((part, j) => {
          if (part.startsWith('**') && part.endsWith('**')) {
            return <strong key={j}>{part.slice(2, -2)}</strong>;
          }
          return part;
        })}
        {i < content.split('\n').length - 1 && <br />}
      </React.Fragment>
    );
  });
};

const ChatPanel = () => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const dispatch = useDispatch();
  const { messages, isLoading } = useSelector((state) => state.chat);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // 🔥 AI-like field extraction (auto-fill form)
  const extractFields = (text) => {
    const data = {};

    const lowerText = text.toLowerCase();

    // 👨‍⚕️ Doctor Name
    const doctorMatch = text.match(/dr\.?\s?[a-zA-Z]+/i);
    if (doctorMatch) data.hcp_id = doctorMatch[0];

    // 💊 Topics
    if (lowerText.includes("efficacy")) data.topics = "Efficacy";
    if (lowerText.includes("side effect")) data.topics = "Side Effects";
    if (lowerText.includes("safety")) data.topics = "Safety";

    // 📦 Samples
    const sampleMatch = text.match(/\d+\s*(boxes|samples|units)/i);
    if (sampleMatch) data.samples = sampleMatch[0];

    // 😊 Sentiment
    if (lowerText.includes("positive")) data.sentiment = "Positive";
    else if (lowerText.includes("negative")) data.sentiment = "Negative";
    else if (lowerText.includes("neutral")) data.sentiment = "Neutral";

    // 📅 Next Steps
    const followMatch = text.match(/follow(-|\s)*up\s+([^,.]+)/i);
    if (followMatch && followMatch[2]) {
      data.next_steps = followMatch[2].trim();
    } else if (lowerText.includes("follow")) {
      data.next_steps = "Follow-up planned";
    }

    // 📝 Notes (full text)
    data.notes = text;

    return data;
  };

  const handleSend = async (e) => {
    e?.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput('');

    dispatch(addMessage({ role: 'user', content: userMessage }));
    dispatch(setLoading(true));

    try {
      // 🔗 Call backend (LangGraph agent)
      const response = await axios.post('http://localhost:8000/api/chat', {
        message: userMessage
      });

      let agentReply = response.data.reply;
      let extractedFromAgent = response.data.data || null;

      dispatch(addMessage({ role: 'agent', content: agentReply }));

      // 🔥 AUTO-FILL FORM
      const lower = userMessage.toLowerCase();

      const isLogMessage =
        lower.includes("met") ||
        lower.includes("discussed") ||
        lower.includes("visited") ||
        lower.includes("interaction");
        
      const isEditMessage = 
        lower.includes("sorry") ||
        lower.includes("update") ||
        lower.includes("change") ||
        lower.includes("instead") ||
        lower.includes("was") ||
        lower.includes("mistake") ||
        lower.includes("correction");

      if (extractedFromAgent) {
        // AI specifically parsed the form fields! Use them directly.
        const mapping = {
          doctor_name: 'hcp_id',
          product: 'topics', 
          samples: 'samples',
          sentiment: 'sentiment',
          follow_up_date: 'next_steps',
          notes: 'notes'
        };

        Object.entries(extractedFromAgent).forEach(([k, v]) => {
          if (v && mapping[k]) {
              dispatch(updateFormField({ field: mapping[k], value: String(v) }));
          }
        });
      } else if (isLogMessage || isEditMessage) {
        // Fallback to client-side extraction
        const extracted = extractFields(userMessage);

        Object.entries(extracted).forEach(([field, value]) => {
          // Only fill product if it exists
          if (field === "product" && (!value || ["efficacy", "positive", "negative", "neutral", "profile"].includes(value.toLowerCase()))) {
            return;
          }
          // Do not overwrite notes entirely if it's just an edit command
          if (isEditMessage && field === "notes" && !lower.includes("notes:")) {
            return;
          }
          dispatch(updateFormField({ field, value }));
        });
      }

    } catch (error) {
      console.error('Error connecting to AI agent:', error);

      dispatch(addMessage({
        role: 'system',
        content: 'System: Cannot connect to LangGraph agent. Ensure backend is running and API keys are set.'
      }));

    } finally {
      dispatch(setLoading(false));
    }
  };

  return (
    <section className="panel">
      <header className="panel-header">
        <Sparkles size={20} style={{ color: 'var(--primary-color)' }} />
        <h2>AI Co-Pilot</h2>
      </header>

      <div className="panel-body" style={{ padding: '1rem', backgroundColor: '#F8FAFC' }}>
        <div className="chat-messages">
          {messages.map((msg, index) => (
            <div key={index} className={`message message-${msg.role}`}>
              {msg.role === 'agent' && (
                <strong style={{
                  display: 'block',
                  fontSize: '0.8rem',
                  opacity: 0.8,
                  marginBottom: '0.2rem'
                }}>
                  LangGraph AI
                </strong>
              )}
              {renderMessageContent(msg.content)}
            </div>
          ))}

          {isLoading && (
            <div className="typing-indicator">
              <div className="dot"></div>
              <div className="dot"></div>
              <div className="dot"></div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      <form className="chat-input-area" onSubmit={handleSend}>
        <input
          type="text"
          className="chat-input"
          placeholder="Type interaction notes or command..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading}
        />
        <button
          type="submit"
          className="btn-send"
          disabled={!input.trim() || isLoading}
          title="Send to AI Co-Pilot"
        >
          <Send size={18} />
        </button>
      </form>
    </section>
  );
};

export default ChatPanel;