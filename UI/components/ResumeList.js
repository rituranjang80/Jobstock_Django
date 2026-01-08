import React from "react";

const ResumeList = ({ resumes }) => {
  if (!resumes || resumes.length === 0) return null;
  return (
    <ul className="resume-list">
      {resumes.map((resume) => (
        <li key={resume.id} className="resume-item">
          <strong>{resume.name || resume.candidate_name || "Unnamed"}</strong>
          {resume.email && <div>Email: {resume.email}</div>}
          {resume.position && <div>Position: {resume.position}</div>}
          {/* Add more fields as needed */}
        </li>
      ))}
    </ul>
  );
};

export default ResumeList;
