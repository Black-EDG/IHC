import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Forzar reseteo básico de márgenes para asegurar el diseño responsivo en smartphones
const style = document.createElement('style');
style.innerHTML = `
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    background-color: #f3f4f6;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
`;
document.head.appendChild(style);

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);