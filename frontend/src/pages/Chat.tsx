import React from 'react';

const Chat: React.FC = () => {
  return (
    <div className=\"max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8\">
      <div className=\"mb-8\">
        <h1 className=\"text-3xl font-bold text-gray-900\">AI Tutor</h1>
        <p className=\"mt-2 text-gray-600\">
          Have a conversation with your AI learning assistant
        </p>
      </div>

      <div className=\"card\">
        <div className=\"text-center py-12\">
          <div className=\"text-gray-500 mb-4\">
            <svg className=\"mx-auto h-12 w-12\" fill=\"none\" stroke=\"currentColor\" viewBox=\"0 0 24 24\">
              <path strokeLinecap=\"round\" strokeLinejoin=\"round\" strokeWidth={2} d=\"M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z\" />
            </svg>
          </div>
          <h3 className=\"text-lg font-semibold text-gray-900 mb-2\">Start a conversation</h3>
          <p className=\"text-gray-500 mb-6\">Ask questions, get explanations, and solve problems with AI assistance.</p>
          <button className=\"btn btn-primary\">Start Chatting</button>
        </div>
      </div>
    </div>
  );
};

export default Chat;
