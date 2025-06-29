import React from 'react';
const InputSection = ({ value, onChange }) => {
    return (React.createElement("section", { id: "input-section", className: "input-section card card-body p-2 mb-3", "aria-label": "Input Section" },
        React.createElement("div", { className: "d-flex align-items-center mb-2" },
            React.createElement("i", { className: "bi bi-input-cursor me-2", "aria-hidden": "true" }),
            React.createElement("span", { className: "visually-hidden" }, "Input cursor icon"),
            React.createElement("h6", { className: "mb-0" }, "Inputs for execution (one per line):")),
        React.createElement("textarea", { className: "form-control", rows: 3, placeholder: "Enter inputs here, one per line", "aria-label": "Execution Inputs", value: value, onChange: e => onChange(e.target.value) })));
};
export default InputSection;
