import React from 'react';
const LoadingSpinner = () => (React.createElement("div", { className: "loading-spinner", style: { display: 'flex', justifyContent: 'center', alignItems: 'center', margin: '10px 0', minHeight: '40px' }, "aria-busy": "true", role: "status" },
    React.createElement("div", { className: "spinner-border text-primary", role: "status" },
        React.createElement("span", { className: "visually-hidden" }, "Loading..."))));
export default LoadingSpinner;
