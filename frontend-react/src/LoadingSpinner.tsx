import React from 'react';

const LoadingSpinner: React.FC = () => (
  <div className="loading-spinner" style={{display:'flex', justifyContent:'center', alignItems:'center', margin:'10px 0', minHeight:'40px'}} aria-busy="true" role="status">
    <div className="spinner-border text-primary" role="status">
      <span className="visually-hidden">Loading...</span>
    </div>
  </div>
);

export default LoadingSpinner; 