import React, { useState, useEffect, useRef } from 'react';
import { Paper, TextField, Button, Typography, Box, Avatar, IconButton } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import VolumeUpIcon from '@mui/icons-material/VolumeUp';
import { generateVoice } from '../utils/elevenlabs';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const HeadmasterChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user' as const, content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [...messages, userMessage],
        }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.message }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, there was an error processing your request.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  const playVoice = async (text: string) => {
    try {
      const audioBlob = await generateVoice(text);
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      await audio.play();
    } catch (error) {
      console.error('Error playing voice:', error);
    }
  };

  return (
    <Paper 
      elevation={3} 
      sx={{
        p: 2,
        height: '80vh',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: '#f5f5f5'
      }}
    >
      <Box sx={{ flexGrow: 1, overflow: 'auto', mb: 2 }}>
        {messages.map((message, index) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
              mb: 2
            }}
          >
            <Box
              sx={{
                display: 'flex',
                alignItems: 'flex-start',
                maxWidth: '70%'
              }}
            >
              {message.role === 'assistant' && (
                <Avatar
                  sx={{ mr: 1, bgcolor: '#1976d2' }}
                  alt="Headmaster"
                  src="/headmaster.png"
                />
              )}
              <Paper
                elevation={1}
                sx={{
                  p: 2,
                  bgcolor: message.role === 'user' ? '#e3f2fd' : '#fff',
                  borderRadius: 2
                }}
              >
                <Typography variant="body1">{message.content}</Typography>
                {message.role === 'assistant' && (
                  <IconButton
                    size="small"
                    onClick={() => playVoice(message.content)}
                    sx={{ mt: 1 }}
                  >
                    <VolumeUpIcon />
                  </IconButton>
                )}
              </Paper>
              {message.role === 'user' && (
                <Avatar
                  sx={{ ml: 1, bgcolor: '#4caf50' }}
                  alt="User"
                />
              )}
            </Box>
          </Box>
        ))}
        <div ref={messagesEndRef} />
      </Box>
      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          multiline
          maxRows={4}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          disabled={isLoading}
          sx={{ bgcolor: '#fff' }}
        />
        <Button
          variant="contained"
          onClick={handleSend}
          disabled={isLoading}
          endIcon={<SendIcon />}
        >
          Send
        </Button>
      </Box>
    </Paper>
  );
};

export default HeadmasterChat;
