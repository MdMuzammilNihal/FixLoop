import * as React from 'react';
import { Toaster } from 'react-hot-toast';

export const ToastProvider: React.FC = () => (
  <Toaster
    position="top-right"
    toastOptions={{
      style: {
        background: '#1e1e2f',
        color: '#e5e5e5',
        borderRadius: '1rem',
        fontSize: '1rem',
      },
      success: {
        style: { background: '#a3be8c', color: '#1e1e2f' },
      },
      error: {
        style: { background: '#bf616a', color: '#fff' },
      },
    }}
  />
);

export default ToastProvider; 