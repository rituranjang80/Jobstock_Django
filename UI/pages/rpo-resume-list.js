import React, { useEffect, useState } from "react";
import ResumeList from "../components/ResumeList";
import { API_ENDPOINTS } from "../constants/apiEndpoints";
import { MESSAGES } from "../constants/messages";

const RpoResumeListPage = () => {
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(API_ENDPOINTS.RPO_RESUME_LIST)
      .then((res) => {
        if (!res.ok) throw new Error("Network response was not ok");
        return res.json();
      })
      .then((data) => {
        setResumes(Array.isArray(data) ? data : data.results || []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err);
        setLoading(false);
      });
  }, []);

  return (
    <main className="container">
      <h1>RPO Resume List</h1>
      {loading && <p>{MESSAGES.LOADING}</p>}
      {error && <p className="error">{MESSAGES.ERROR}</p>}
      {!loading && !error && resumes.length === 0 && <p>{MESSAGES.NO_DATA}</p>}
      <ResumeList resumes={resumes} />
    </main>
  );
};

export default RpoResumeListPage;
