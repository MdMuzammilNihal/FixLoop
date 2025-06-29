import React from 'react';

interface InputSectionProps {
  value: string;
  onChange: (value: string) => void;
}

const InputSection: React.FC<InputSectionProps> = ({ value, onChange }) => {
  return (
    <section id="input-section" className="input-section card card-body p-2 mb-3" aria-label="Input Section">
      <div className="d-flex align-items-center mb-2">
        <i className="bi bi-input-cursor me-2" aria-hidden="true"></i><span className="visually-hidden">Input cursor icon</span>
        <h6 className="mb-0">Inputs for execution (one per line):</h6>
      </div>
      <textarea className="form-control" rows={3} placeholder="Enter inputs here, one per line" aria-label="Execution Inputs" value={value} onChange={e => onChange(e.target.value)} />
    </section>
  );
};

export default InputSection; 