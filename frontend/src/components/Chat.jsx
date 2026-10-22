import React, { useEffect, useState, useRef } from "react";
import ReactMarkdown from "react-markdown";
import "../styles/Chat.css";
import { useLocation, useNavigate } from "react-router-dom";
import "../index.css";

const Chat = () => {
  const [query, setQuery] = useState();
  const [responses, setResponses] = useState(new Array());
  const location = useLocation();
  const navigate = useNavigate();
  const [queries, setQueries] = useState([]);
  const endRef = useRef(null);

  const fileName = location.state?.filename;

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [responses]);

  function handleQueryChange(e) {
    setQuery(e.target.value);
  }

  function handleExit() {
    navigate("/");
  }

  async function handleQuerySubmit(e) {
    e.preventDefault();
    setQueries((prev) => [...prev, query]);
    const result = await fetch("http://localhost:8000/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: query }),
    });
    const data = await result.json();
    setQuery("")
    setResponses((prev) => [...prev, data.answer]);

  }

  return (
    <div className="mainChatDiv">
      <div className="asideDiv">
        <aside className="aside">
          <div className="brandDiv">
            <p className="brandPara">Jellyfish</p>
          </div>
          <div className="fileDiv">
            <p className="fileName">{fileName}</p>
          </div>
          <div className="exitButtonDiv">
            <button className="exitButton" onClick={handleExit}>
              exit
            </button>
          </div>
        </aside>
      </div>

      <div className="chatbox">
        <div className="chatDiv">
          {responses.map((response, index) => (
            <React.Fragment key={index}>
              <span className="responseQuery">{queries[index]}</span>
              <div className="responseAnswer">
                <ReactMarkdown>{response}</ReactMarkdown>
              </div>
            </React.Fragment>
          ))}
          <div ref={endRef} />
        </div>
        <div className="queryForm">
          <form className="query" onSubmit={handleQuerySubmit}>
            <input
              type="text"
              className="queryInput"
              onChange={handleQueryChange}
              value={query}
            />
            <button type="submit" className="queryButton">
              submit
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Chat;
