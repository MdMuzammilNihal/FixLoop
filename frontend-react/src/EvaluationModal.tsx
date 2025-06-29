import React from 'react';

const EvaluationModal: React.FC = () => {
  return (
    <div className="modal fade" id="evalReportModal" tabIndex={-1} aria-labelledby="evalReportModalLabel" aria-hidden="true" aria-modal="true" role="dialog">
      <div className="modal-dialog modal-lg modal-dialog-scrollable">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title" id="evalReportModalLabel">Evaluation Report</h5>
            <button type="button" className="btn-close" data-bs-dismiss="modal" aria-label="Close"><span className="visually-hidden">Close</span></button>
          </div>
          <div className="modal-body" id="eval-report-content" style={{background:'#23283a',color:'#f8f8f2'}}></div>
        </div>
      </div>
    </div>
  );
};

export default EvaluationModal; 