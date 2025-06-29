import React from 'react';
const EvaluationModal = () => {
    return (React.createElement("div", { className: "modal fade", id: "evalReportModal", tabIndex: -1, "aria-labelledby": "evalReportModalLabel", "aria-hidden": "true", "aria-modal": "true", role: "dialog" },
        React.createElement("div", { className: "modal-dialog modal-lg modal-dialog-scrollable" },
            React.createElement("div", { className: "modal-content" },
                React.createElement("div", { className: "modal-header" },
                    React.createElement("h5", { className: "modal-title", id: "evalReportModalLabel" }, "Evaluation Report"),
                    React.createElement("button", { type: "button", className: "btn-close", "data-bs-dismiss": "modal", "aria-label": "Close" },
                        React.createElement("span", { className: "visually-hidden" }, "Close"))),
                React.createElement("div", { className: "modal-body", id: "eval-report-content", style: { background: '#23283a', color: '#f8f8f2' } })))));
};
export default EvaluationModal;
