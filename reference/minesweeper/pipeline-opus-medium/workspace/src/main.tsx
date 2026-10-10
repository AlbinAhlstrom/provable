import React from 'react';
import ReactDOM from 'react-dom/client';
import * as AppModule from './App';
import './index.css';
import './theme.css';

const App = (AppModule as any).default || (AppModule as any).App;

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {App ? <App /> : <div style={{ color: 'red', padding: 20 }}>Failed to load App component</div>}
  </React.StrictMode>,
);
